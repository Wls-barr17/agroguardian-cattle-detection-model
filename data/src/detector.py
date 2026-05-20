"""
detector.py - Carga modelo YOLO y realiza inferencia sobre frames

Responsabilidades:
- Cargar modelo entrenado (custom o preentrenado)
- Ejecutar inferencia
- Filtrar detecciones por confianza y tamaño
- Soportar múltiples clases (vacas, personas, etc.)
"""

from ultralytics import YOLO
import numpy as np
import torch
import os
from config import (
    CONFIDENCE_THRESHOLD, IOU_THRESHOLD, IMGSZ, DEVICE, MODEL_PATH
)


class Detector:
    """
    Detector YOLO que maneja vacas y potencialmente otras clases.
    
    Características:
    - Auto-detecta clases disponibles en el modelo
    - Activa/desactiva personas automáticamente si existen
    - Filtra detecciones por tamaño para evitar ruido
    """
    
    def __init__(self):
        # Cargar modelo
        if not os.path.exists(MODEL_PATH):
            print(f"⏳ Descargando modelo {MODEL_PATH}... (primera vez)")

        self.device = DEVICE if torch.cuda.is_available() or DEVICE == 'cpu' else 'cpu'
        try:
            self.model = YOLO(MODEL_PATH)
            self.model.to(self.device)
        except Exception as e:
            raise RuntimeError(f"Error cargando modelo YOLO: {e}")

        # Detectar automáticamente qué clases están disponibles en el modelo
        self.class_names = self.model.names
        self.available_classes = list(self.class_names.keys())
        
        # Determinar clases a detectar
        self.detect_classes = self._get_detect_classes()
        
        # Mostrar información de clases
        print(f"✓ Modelo cargado: {os.path.basename(MODEL_PATH)}")
        print(f"  Clases disponibles: {[self.class_names[c] for c in self.available_classes]}")
        print(f"  Clases a detectar: {[self.class_names[c] for c in self.detect_classes]}")
        
        # Parámetros de detección
        self.conf_threshold = CONFIDENCE_THRESHOLD
        self.iou_threshold = IOU_THRESHOLD
        self.imgsz = IMGSZ
        self.min_box_area = 100  # Píxeles² mínimos

    def _get_detect_classes(self):
        """
        Determina qué clases detectar automáticamente.
        
        Lógica:
        - Siempre detecta clase 0 (vacas, es lo entrenado)
        - Si existe clase 1 (personas), la agrega automáticamente
        - Ignora otras clases no relevantes
        
        Returns:
            Lista de clase IDs a detectar
        """
        classes_to_detect = [0]  # Siempre vacas (clase 0)
        
        if 1 in self.available_classes:
            classes_to_detect.append(1)
            print("✓ Clase 'person' detectada en el modelo - será usada")
        
        return classes_to_detect

    def predict(self, frame: np.ndarray):
        """
        Ejecuta inferencia sobre un frame.
        
        Args:
            frame: Frame de video (np.ndarray)
        
        Returns:
            Lista de tuplas (x1, y1, x2, y2, conf, class_id)
            Solo incluye detecciones válidas (conf > threshold, área > min)
        """
        try:
            results = self.model(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                imgsz=self.imgsz,
                device=self.device,
                classes=self.detect_classes,
                verbose=False
            )
        except Exception as e:
            print(f"Error en inferencia YOLO: {e}")
            return []

        detections = []
        frame_h, frame_w = frame.shape[:2]

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                if conf < self.conf_threshold:
                    continue
                if cls not in self.detect_classes:
                    continue
                
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Filtrar por tamaño mínimo (evita falsos positivos pequeños)
                box_w = x2 - x1
                box_h = y2 - y1
                area = box_w * box_h
                
                if area < self.min_box_area:
                    continue
                
                detections.append((x1, y1, x2, y2, conf, cls))

        return detections
