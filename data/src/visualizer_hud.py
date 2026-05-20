"""
visualizer_hud.py - Sistema de visualización profesional (HUD)

Diseño tipo dashboard moderno con:
- Panel superior: estado del sistema
- Lado izquierdo: contador de personas (futuro)
- Lado derecho: contador de vacas
- Inferior: información de movimiento y eventos
- Bounding boxes sobre objetos
"""

import cv2
import numpy as np
from datetime import datetime


class VisualizerHUD:
    """
    Visualización avanzada con HUD tipo dashboard.
    
    Este HUD es responsive y se adapta a cualquier resolución de video.
    Mantiene la disposición original:
    - Barra superior
    - Panel izquierdo: PERSONAS
    - Panel derecho: VACAS CONTADAS
    - Panel inferior: MOVIMIENTO / STATUS
    """

    def __init__(self):
        # Colores BGR: estilo oscuro tipo monitoreo (CCTV / HUD táctico)
        # Panels: negro mate / gris oscuro
        # ===== PALETA HUD NEGRO / CCTV =====
        self.color_bg = (8, 10, 12)          # negro profundo
        self.color_panel = (15, 18, 22)      # panel oscuro
        self.color_border = (45, 75, 110)    # borde azul oscuro
        self.color_accent = (80, 170, 255)   # azul tecnológico
        self.color_text = (230, 235, 240)    # blanco suave

        # Bounding boxes
        self.color_cow_stationary = (0, 255, 0)   # VERDE = contadas
        self.color_cow_moving = (0, 0, 255)       # ROJO = no contadas
        self.color_person = (255, 0, 0)           # AZUL = personas

        # Fuentes
        self.font_main = cv2.FONT_HERSHEY_SIMPLEX
        self.font_mono = cv2.FONT_HERSHEY_DUPLEX

        # Configuración de visualización
        self.panel_alpha = 0.88

        # Configuración de escalado
        self.min_ui_scale = 0.5
        self.max_ui_scale = 1.8
        self.reference_width = 1280.0
        self.reference_height = 720.0

    def draw(self, frame, tracks, counts, fps=0, frame_number=0):
        h, w = frame.shape[:2]

        self.ui_scale = min(w / self.reference_width, h / self.reference_height)
        self.ui_scale = max(self.min_ui_scale, min(self.ui_scale, self.max_ui_scale))

        self.margin = max(int(0.015 * w), 10)
        self.panel_width = int(w * 0.16)
        self.panel_width = min(self.panel_width, int((w - 3 * self.margin) / 2))
        self.panel_width = max(self.panel_width, int(0.18 * w))
        self.panel_width = max(self.panel_width, int(110 * self.ui_scale))

        self.panel_height = int(h * 0.08)  # antes 0.13 → ahora compacto
        self.panel_height = min(self.panel_height, int(h * 0.28))
        self.panel_height = max(self.panel_height, int(0.16 * h))
        self.panel_height = max(self.panel_height, int(120 * self.ui_scale))

        self.top_height = int(max(h * 0.05, 34 * self.ui_scale))
        self.bottom_height = int(max(h * 0.072, 40 * self.ui_scale))

        self.title_padding = max(int(0.03 * w), int(12 * self.ui_scale))
        self.inner_padding = max(int(10 * self.ui_scale), 8)
        self.left_x = self.margin
        self.right_x = w - self.panel_width - self.margin
        self.panel_y = self.top_height + self.margin

        self._draw_bboxes(frame, tracks, counts)
        self._draw_top_panel(frame, fps, frame_number)
        self._draw_left_panel(frame, counts)
        self._draw_right_panel(frame, counts)
        self._draw_bottom_panel(frame, counts)

        return frame

    def _draw_bboxes(self, frame, tracks, counts):
        stationary_ids = counts.get("stationary_ids", set())

        for track in tracks:
            bbox = track["bbox"]
            cls = int(track["class_id"])
            track_id = track["track_id"]
            l, top, r, b = map(int, bbox)

            # Colores fijos: VACAS contadas = VERDE, VACAS en movimiento = ROJO, PERSONAS = AZUL
            if cls == 0:
                if track_id in stationary_ids:
                    color = self.color_cow_stationary
                    thickness = max(1, int(2 * self.ui_scale))
                    label = f"COW#{track_id}"
                else:
                    color = self.color_cow_moving
                    thickness = max(1, int(2 * self.ui_scale))
                    label = None
            else:
                color = self.color_person
                thickness = max(1, int(2 * self.ui_scale))
                label = f"PERSON#{track_id}"

            cv2.rectangle(frame, (l, top), (r, b), color, thickness)
            if label:
                self._draw_label(frame, label, (l, top), color)

    def _draw_label(self, frame, text, pos, bg_color):
        x, y = pos
        font_scale = max(0.26, 0.32 * self.ui_scale)
        font_thickness = max(1, int(max(1, self.ui_scale)))

        (text_w, text_h), baseline = cv2.getTextSize(text, self.font_main, font_scale, font_thickness)
        box_tl = (x - int(3 * self.ui_scale), y - text_h - baseline - int(3 * self.ui_scale))
        box_br = (x + text_w + int(5 * self.ui_scale), y + baseline)

        cv2.rectangle(frame, box_tl, box_br, bg_color, -1)
        cv2.putText(frame, text, (x + int(2 * self.ui_scale), y - baseline - int(2 * self.ui_scale)),
                    self.font_main, font_scale, self.color_text, font_thickness, cv2.LINE_AA)

    def _draw_top_panel(self, frame, fps, frame_number):
        h, w = frame.shape[:2]
        overlay = frame.copy()

        # barra negra pura (sin bordes visibles)
        cv2.rectangle(overlay, (0, 0), (w, self.top_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.92, frame, 0.08, 0, frame)

        # texto limpio sin línea inferior
        left_text = "AGROGUARDIAN SYSTEM"
        right_text = f"FPS: {fps:.1f} | FRAME: {frame_number}"

        font_scale = max(0.38, 0.55 * self.ui_scale)
        thickness = 1

        # título verde (como pediste)
        cv2.putText(frame, left_text,
                    (self.margin, int(self.top_height * 0.7)),
                    self.font_main, font_scale,
                    (0, 255, 0), thickness, cv2.LINE_AA)

        # FPS blanco
        right_size = cv2.getTextSize(right_text, self.font_main, font_scale, thickness)[0]
        cv2.putText(frame, right_text,
                    (w - right_size[0] - self.margin, int(self.top_height * 0.7)),
                    self.font_main, font_scale,
                    (230, 230, 230), thickness, cv2.LINE_AA)
        
        
    def _draw_left_panel(self, frame, counts):
        panel_x = self.left_x
        panel_y = self.panel_y
        panel_w = self.panel_width
        panel_h = self.panel_height

        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (panel_x, panel_y),
            (panel_x + panel_w, panel_y + panel_h),
            (10, 10, 10),
            -1
        )
        cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)

        # Borde del panel
        cv2.rectangle(
            frame,
            (panel_x, panel_y),
            (panel_x + panel_w, panel_y + panel_h),
            self.color_border,
            max(1, int(1 * self.ui_scale))
        )

        # =========================
        # POSICIONES BASE
        # =========================
        title_y = panel_y + int(panel_h * 0.30)
        value_y = panel_y + int(panel_h * 0.72)

        # =========================
        # TÍTULO
        # =========================
        title = "PERSONAS"
        cv2.putText(
            frame,
            title,
            (panel_x + self.inner_padding, title_y),
            self.font_main,
            0.45 * self.ui_scale,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )

        # =========================
        # CONTEO PRINCIPAL
        # =========================
        count = counts.get("people", 0)

        cv2.putText(
            frame,
            str(count),
            (panel_x + self.inner_padding, value_y),
            self.font_mono,
            0.95 * self.ui_scale,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        # =========================
        # BLOQUE EXTRA (ESTADO DINÁMICO)
        # =========================
        person_count = counts.get("people", 0)

        if person_count > 0:
            count_text = str(person_count)

            count_scale = self._fit_text_scale(
                count_text,
                self.font_mono,
                panel_w - 2 * self.inner_padding,
                max(1.6 * self.ui_scale, 0.9),
                max(1, int(2 * self.ui_scale))
            )

            count_size = cv2.getTextSize(
                count_text,
                self.font_mono,
                count_scale,
                max(1, int(2 * self.ui_scale))
            )[0]

            txt_x = panel_x + (panel_w - count_size[0]) // 2
            txt_y = panel_y + int(panel_h * 0.62)

            cv2.putText(
                frame,
                count_text,
                (txt_x, txt_y),
                self.font_mono,
                count_scale,
                self.color_text,
                max(1, int(2 * self.ui_scale)),
                cv2.LINE_AA
            )

        else:
            status_text = "Proximo"

            status_scale = max(0.36, 0.56 * self.ui_scale)

            status_size = cv2.getTextSize(
                status_text,
                self.font_main,
                status_scale,
                max(1, int(self.ui_scale))
            )[0]

            txt_x = panel_x + (panel_w - status_size[0]) // 2
            txt_y = panel_y + int(panel_h * 0.78)

            cv2.putText(
                frame,
                status_text,
                (txt_x, txt_y),
                self.font_main,
                status_scale,
                self.color_text,
                max(1, int(self.ui_scale)),
                cv2.LINE_AA
            )

        return

    def _draw_bottom_panel(self, frame, counts):
        h, w = frame.shape[:2]
        panel_y = h - self.bottom_height

        overlay = frame.copy()

        # Fondo barra inferior
        cv2.rectangle(
            overlay,
            (0, panel_y),
            (w, h),
            (0, 0, 0),
            -1
        )
        cv2.addWeighted(overlay, 0.94, frame, 0.06, 0, frame)

        # =========================
        # DATA
        # =========================
        active_cows = counts.get("active_cows", 0)
        stationary_cows = counts.get("stationary_cows", 0)
        moving_cows = active_cows - stationary_cows

        left_text = f"MOVIMIENTO: {moving_cows} | ACTIVAS: {active_cows}"
        status_text = "STATUS: OPERATIVO"
        time_text = datetime.now().strftime("%H:%M:%S")

        font_scale = max(0.4, 0.55 * self.ui_scale)
        thickness = 1

        # =========================
        # LAYOUT FIX
        # =========================
        line1_y = panel_y + int(self.bottom_height * 0.38)
        line2_y = panel_y + int(self.bottom_height * 0.68)

        # LEFT: MOVIMIENTO
        cv2.putText(
            frame,
            left_text,
            (self.margin, line1_y),
            self.font_main,
            font_scale,
            (240, 240, 240),
            thickness,
            cv2.LINE_AA
        )

        # LEFT: STATUS
        cv2.putText(
            frame,
            status_text,
            (self.margin, line2_y),
            self.font_main,
            font_scale,
            (0, 255, 0),
            thickness,
            cv2.LINE_AA
        )

        # RIGHT: TIME
        time_size = cv2.getTextSize(
            time_text,
            self.font_main,
            font_scale,
            thickness
        )[0]

        cv2.putText(
            frame,
            time_text,
            (w - time_size[0] - self.margin, line2_y),
            self.font_main,
            font_scale,
            (0, 255, 0),
            thickness,
            cv2.LINE_AA
        )

    def _draw_right_panel(self, frame, counts):
        panel_x = self.right_x
        panel_y = self.panel_y
        panel_w = self.panel_width
        panel_h = self.panel_height

        # =========================
        # BACKGROUND CARD
        # =========================
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (panel_x, panel_y),
            (panel_x + panel_w, panel_y + panel_h),
            (10, 10, 10),
            -1
        )
        cv2.addWeighted(overlay, 0.92, frame, 0.08, 0, frame)

        # =========================
        # BORDER (thin, clean)
        # =========================
        cv2.rectangle(
            frame,
            (panel_x, panel_y),
            (panel_x + panel_w, panel_y + panel_h),
            self.color_border,
            max(1, int(self.ui_scale))
        )

        # =========================
        # TITLE (top aligned like LEFT panel)
        # =========================
        title = "VACAS CONTADAS"
        title_y = panel_y + int(panel_h * 0.35)

        cv2.putText(
            frame,
            title,
            (panel_x + self.inner_padding, title_y),
            self.font_main,
            0.45 * self.ui_scale,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )

        # =========================
        # DATA
        # =========================
        total_cows = counts.get("total_cows", 0)
        count_text = str(total_cows)

        # auto-fit scale
        count_scale = self._fit_text_scale(
            count_text,
            self.font_mono,
            panel_w - 2 * self.inner_padding,
            max(1.7 * self.ui_scale, 0.9),
            max(1, int(2 * self.ui_scale))
        )

        # center perfectly
        count_size = cv2.getTextSize(
            count_text,
            self.font_mono,
            count_scale,
            max(1, int(2 * self.ui_scale))
        )[0]

        center_x = panel_x + (panel_w - count_size[0]) // 2
        center_y = panel_y + int(panel_h * 0.68)

        # =========================
        # COUNT (main visual anchor)
        # =========================
        cv2.putText(
            frame,
            count_text,
            (center_x, center_y),
            self.font_mono,
            count_scale,
            self.color_text,
            max(1, int(2 * self.ui_scale)),
            cv2.LINE_AA
        )

    def _fit_text_scale(self, text, font, max_width, max_scale, thickness):
        scale = max_scale
        while scale > 0.25:
            text_size = cv2.getTextSize(text, font, scale, thickness)[0]
            if text_size[0] <= max_width:
                return scale
            scale -= 0.05
        return max(0.25, scale)
