"""
tracker.py - Mantiene identidades consistentes de animales entre frames

Usa DeepSORT para asociar detecciones a través del tiempo.
Esto permite darle un ID único a cada vaca/persona y rastrearla.
"""

from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np
from config import MAX_AGE_TRACKER, N_INIT_TRACKER


class Tracker:
    """
    Tracker basado en DeepSORT.
    
    Función:
    - Asocia detecciones entre frames
    - Mantiene IDs consistentes para cada objeto detectado
    - Filtra detecciones falsas transitorias
    """
    
    def __init__(self):
        """Inicializa DeepSORT con parámetros de config.py"""
        try:
            self.tracker = DeepSort(
                max_age=MAX_AGE_TRACKER,
                n_init=N_INIT_TRACKER
            )
        except Exception as e:
            raise RuntimeError(f"Error inicializando tracker DeepSORT: {e}")

    def update(self, detections, frame):
        """
        Actualiza tracks con nuevas detecciones.
        
        Proceso:
        1. Convierte formato de detecciones (XYXY → XYWH)
        2. Pasa al tracker de DeepSORT
        3. Filtra tracks confirmados (valida que existan suficiente frames)
        4. Retorna solo objetos rastreados válidos
        
        Args:
            detections: Lista de (x1, y1, x2, y2, conf, class_id)
            frame: Frame actual (usado por DeepSORT para feature extraction)
        
        Returns:
            Lista de dicts: {bbox, confidence, class_id, track_id}
        """
        if len(detections) == 0:
            return []
        
        try:
            # Convertir formato XYXY → XYWH (lo que DeepSORT espera)
            raw_detections = []
            for d in detections:
                x1, y1, x2, y2, conf, class_id = d
                w = x2 - x1
                h = y2 - y1
                raw_detections.append(([x1, y1, w, h], conf, class_id))
            
            # Actualizar tracker
            tracks = self.tracker.update_tracks(
                raw_detections=raw_detections,
                frame=frame
            )
        except Exception as e:
            print(f"Error actualizando tracker: {e}")
            return []

        # Filtrar y preparar salida
        output = []
        for t in tracks:
            # Solo usar tracks confirmados (evita contar falsas detecciones)
            if not t.is_confirmed():
                continue
            
            # Solo usar tracks actualizados en este frame (evita fantasmas)
            if t.time_since_update > 1:
                continue
            
            bbox = t.to_ltrb()  # left, top, right, bottom
            track_id = t.track_id
            cls = t.det_class
            conf = t.det_conf
            
            # Validación de confianza
            if conf is None or conf < 0:
                conf = 0.5
            
            output.append({
                "bbox": bbox,
                "confidence": conf,
                "class_id": cls,
                "track_id": track_id,
            })

        return output