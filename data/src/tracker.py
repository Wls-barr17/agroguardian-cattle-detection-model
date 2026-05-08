"""
tracker.py
Mantiene y actualiza identidades de vacas a lo largo de los frames usando DeepSORT.
Parámetros de tracking configurables desde config.py
"""

from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np
from config import MAX_AGE_TRACKER, N_INIT_TRACKER

class Tracker:
    """
    Tracker basado en DeepSORT que asocia detecciones entre frames.
    Mantiene IDs consistentes para cada vaca detectada.
    """
    def __init__(self):
        """Inicializa DeepSORT con parámetros desde config.py"""
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
        
        Args:
            detections: Lista de tuplas (x1, y1, x2, y2, conf, class_id) del Detector
            frame: Frame actual (np.ndarray)
        
        Returns:
            Lista de dicts con keys: bbox, confidence, class_id, track_id
            Solo retorna tracks confirmados (han existido por N_INIT_TRACKER frames)
        """
        tracks = []
        
        # Si no hay detecciones, retorna lista vacía
        if len(detections) == 0:
            return []
        
        try:
            # Convierte detecciones al formato esperado por DeepSORT
            # (bbox, confidence, class_id)
            raw_detections = [(d[:4], d[4], d[5]) for d in detections]
            
            # Actualiza tracker con las nuevas detecciones
            tracks = self.tracker.update_tracks(
                raw_detections=raw_detections,
                frame=frame
            )
        except Exception as e:
            print(f"Error actualizando tracker: {e}")
            return []

        output = []
        for t in tracks:
            # Filtrado: solo tracks confirmados y que no se han perdido por mucho tiempo
            # is_confirmed() asegura que el track ha sido visto en al menos N_INIT_TRACKER frames
            # time_since_update == 0 significa que fue actualizado en este frame
            if not t.is_confirmed():
                continue
            
            # Si el track no fue visto en este frame, lo descartamos (muy fresco o fantasma)
            if t.time_since_update > 1:
                continue
            
            bbox = t.to_ltrb()  # left, top, right, bottom
            track_id = t.track_id
            cls = t.det_class
            conf = t.det_conf
            
            # Validación adicional de confidencia
            if conf is None or conf < 0:
                conf = 0.5
            
            output.append({
                "bbox": bbox,
                "confidence": conf,
                "class_id": cls,
                "track_id": track_id,
            })

        return output