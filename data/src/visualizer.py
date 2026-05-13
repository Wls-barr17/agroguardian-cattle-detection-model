"""
visualizer.py
Dibuja bounding boxes, labels de tracking y contadores en los frames.
Proporciona visualización clara del sistema para debugging y validación.
"""

import cv2

class Visualizer:
    """
    Visualiza detecciones, tracks y contadores sobre los frames.
    Muestra información en tiempo real para validar el funcionamiento del sistema.
    """
    def __init__(self):
        """Define colores y etiquetas para clases COCO"""
        # Colores para cada clase (BGR)
        self.colors = {
            0: (0, 255, 0),   # Vaca (modelo actual)
            1: (0, 0, 255),   # Persona (reservado futuro)
            }
        
        self.labels = {0: "Vaca",
                       1: "Persona",
                       }
        
        # Fuente y tamaño para texto
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.font_thickness = 2
        self.line_type = cv2.LINE_AA

    def draw(self, frame, tracks, counts):
        """
        Dibuja bounding boxes, labels de tracking y contadores sobre el frame.
        
        Args:
            frame: np.ndarray del frame actual
            tracks: Lista de dicts con bbox, class_id, track_id, confidence
            counts: Dict con total_cows, stationary_cows, active_cows, people, stationary_ids
        
        Returns:
            Frame anotado con visualizaciones
        """
        # Obtiene el set de IDs estacionarios
        stationary_ids = counts.get("stationary_ids", set())
        
        # Dibuja bounding boxes y labels para cada track
        for t in tracks:
            bbox = t["bbox"]
            cls = int(t["class_id"])
            track_id = t["track_id"]
            confidence = t.get("confidence", 0.0)

            # Coordenadas del bbox
            l, top, r, b = map(int, bbox)

            # Define color y espesor según estado
            if cls == 0 and track_id in stationary_ids:
                # Vaca ESTACIONARIA: VERDE, box grueso, con ID
                color = (0, 255, 0)  # Verde
                thickness = 3  # Box más grueso
                show_id = True
            elif cls == 0:
                # Vaca en MOVIMIENTO: AMARILLO, box fino, sin ID
                color = (0, 255, 255)  # Amarillo
                thickness = 1  # Box fino
                show_id = False
            else:
                # Persona: ROJO
                color = (0, 0, 255)
                thickness = 2
                show_id = True

            # Dibuja rectángulo
            cv2.rectangle(frame, (l, top), (r, b), color, thickness)

            # Solo dibuja etiqueta si es estacionaria o persona
            if show_id:
                if cls == 0:
                    label = f"ID {track_id}"  # Vacas: solo mostrar ID
                else:
                    label = f"Persona #{track_id}"  # Personas: etiqueta completa
                    
                label_y = max(top - 8, 15)
                
                # Fondo para mejorar legibilidad del texto
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, self.font, 0.6, 2
                )
                cv2.rectangle(
                    frame,
                    (l, label_y - text_height - baseline - 5),
                    (l + text_width + 5, label_y + baseline),
                    color,
                    -1
                )

                # Dibuja etiqueta
                cv2.putText(
                    frame,
                    label,
                    (l + 3, label_y - baseline),
                    self.font,
                    0.6,
                    (255, 255, 255),
                    2,
                    self.line_type
                )

        # Dibuja información de contadores
        self._draw_counters(frame, counts)

        return frame

    def _draw_counters(self, frame, counts):
        """
        Dibuja información de contadores en la esquina superior izquierda.
        
        Args:
            frame: np.ndarray del frame
            counts: Dict con contadores
        """
        # Información a mostrar
        total_cows = counts.get("total_cows", 0)
        active = counts.get("active_cows", 0)
        people = counts.get("people", 0)
        show_people = people > 0

        # Línea 1: Vacas CONTADAS (estacionarias)
        text1 = f"VACAS CONTADAS (QUIETAS): {total_cows}"
        y1 = 30
        
        # Fondo para línea 1 (VERDE - vacas contadas)
        (w1, h1), baseline1 = cv2.getTextSize(text1, self.font, 0.7, 2)
        cv2.rectangle(frame, (5, y1 - h1 - 5), (15 + w1, y1 + baseline1 + 5), (0, 200, 0), -1)
        cv2.putText(frame, text1, (10, y1), self.font, 0.7, (255, 255, 255), 2, self.line_type)

        # Línea 2: Vacas en movimiento
        text2 = f"En movimiento (no contadas): {active - total_cows}"
        y2 = 60
        
        # Fondo para línea 2 (AMARILLO - en movimiento)
        (w2, h2), baseline2 = cv2.getTextSize(text2, self.font, self.font_scale, 1)
        cv2.rectangle(frame, (5, y2 - h2 - 5), (15 + w2, y2 + baseline2 + 5), (0, 200, 200), -1)
        cv2.putText(frame, text2, (10, y2), self.font, self.font_scale, (0, 0, 0), 1, self.line_type)
        
        # Línea 3: Personas
        if show_people:
            text3 = f"Personas: {people}"
            y3 = 85
            (w3, h3), baseline3 = cv2.getTextSize(text3, self.font, self.font_scale, 1)
            
            cv2.rectangle(frame, (5, y3 - h3 - 5), (15 + w3, y3 + baseline3 + 5), (0, 0, 200), -1)
            cv2.putText(frame, text3, (10, y3), self.font, self.font_scale, (255, 255, 255), 1, self.line_type)