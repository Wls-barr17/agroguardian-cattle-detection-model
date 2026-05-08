"""detector.py
Responsible for loading YOLOv8n model and running inference on frames.
"""


from ultralytics import YOLO
import numpy as np
import torch
import os
from config import (
    CONFIDENCE_THRESHOLD, IOU_THRESHOLD, IMGSZ, DEVICE, CLASSES, MODEL_PATH
)

class Detector:
    """
    Detector YOLOv8 para vacas y personas.
    Carga el modelo y realiza inferencia sobre frames.
    Parámetros y clases filtradas se leen de config.py
    """
    def __init__(self):
        # Verifica si el modelo existe, sino YOLO lo descargará automáticamente
        if not os.path.exists(MODEL_PATH):
            print(f"⏳ Descargando modelo {MODEL_PATH}... (primera vez solamente)")

        # Selecciona dispositivo (cpu/cuda)
        self.device = DEVICE if torch.cuda.is_available() or DEVICE == 'cpu' else 'cpu'
        try:
            self.model = YOLO(MODEL_PATH)
            self.model.to(self.device)
        except Exception as e:
            raise RuntimeError(f"Error cargando modelo YOLO: {e}")

        self.conf_threshold = CONFIDENCE_THRESHOLD
        self.iou_threshold = IOU_THRESHOLD
        self.imgsz = IMGSZ
        self.detect_classes = CLASSES
        self.class_names = self.model.names

    def predict(self, frame: np.ndarray):
        """
        Ejecuta inferencia sobre un frame.
        Devuelve lista de detecciones: (x1, y1, x2, y2, conf, class_id)
        Aplica filtrado adicional para evitar falsos positivos y asegurar detección de vacas cercanas.
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
        min_box_area = 200  # área mínima de bbox para considerar (ajustable)
                            # Reducido de 500 a 200 para detectar vacas pequeñas/lejanas
        frame_h, frame_w = frame.shape[:2]

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf < self.conf_threshold:
                    continue
                if self.detect_classes and cls not in self.detect_classes:
                    continue
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                # Filtrado por tamaño mínimo de bounding box (evita falsos positivos pequeños)
                box_w = x2 - x1
                box_h = y2 - y1
                area = box_w * box_h
                if area < min_box_area:
                    continue
                # (Opcional) Filtrar por posición: evitar bordes si se desea
                # if x1 < 5 or y1 < 5 or x2 > frame_w-5 or y2 > frame_h-5:
                #     continue
                detections.append((x1, y1, x2, y2, conf, cls))

        # (Opcional) Hook para métricas de calidad, logging, etc.
        # print(f"Detecciones válidas: {len(detections)}")

        return detections
