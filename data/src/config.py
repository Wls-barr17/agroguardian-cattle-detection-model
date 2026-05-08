"""
config.py
Configuración centralizada del sistema AgroGuardian.
Modifica estos parámetros para ajustar el comportamiento del sistema.
TODAS las configuraciones se cargan desde aquí para facilitar ajustes sin editar código.
"""

# ==================== CONFIGURACIÓN YOLO ====================
# Parámetros de inferencia del modelo de detección

CONFIDENCE_THRESHOLD = 0.35  # Umbral de confianza para detección (0-1)
                              # Valores bajos detectan más, pero tienen falsos positivos
                              # Valores altos detectan menos, pero son más precisos
                              # Recomendado: 0.25-0.4
                              # OPTIMIZADO: Bboxes pequeños y precisos

IOU_THRESHOLD = 0.60         # Umbral de IoU (Intersection over Union) para NMS
                              # (Non-Maximum Suppression): elimina boxes duplicadas/solapadas
                              # Recomendado: 0.4-0.6

IMGSZ = 1024                 # Tamaño de imagen para la red YOLO
                              # Valores comunes: 416, 640, 1024
                              # Mayor = más precisión pero más lento
                              # Recomendado: 640 para balance
                              # OPTIMIZADO PARA VACAS EN MOVIMIENTO: 1024

DEVICE = 'cpu'               # 'cpu' para CPU, 'cuda' para GPU
                              # GPU es 10-20x más rápido si está disponible

CLASSES = [16]               # Clases COCO a detectar
                              # 16 = vaca (cow)
                              # 0 = persona (person)
                              # [16] = solo vacas
                              # [0, 16] = personas y vacas

MODEL_PATH = '../models/yolov8s.pt'  # Ruta al modelo YOLO
                                      # Opciones: '../models/yolov8n.pt' (nano)
                                      #           '../models/yolov8s.pt' (small - recomendado)
                                      #           '../models/yolov8m.pt' (medium)
                                      #           '../models/yolov8l.pt' (large)
                                      # O: '../trained_models/yolov8_cows_YYYYMMDD.pt' (personalizado)

# ==================== CONFIGURACIÓN TRACKER ====================
# Parámetros del tracking (DeepSORT)

MAX_AGE_TRACKER = 30         # Máximo número de frames que un track puede estar sin
                              # actualización antes de ser eliminado (evita fantasmas)
                              # Recomendado: 20-50

N_INIT_TRACKER = 2           # Número de frames para confirmar un track
                              # (evita contar detecciones falsas transitorias)
                              # Recomendado: 2-5
                              # OPTIMIZADO PARA VACAS EN MOVIMIENTO: 2 (confirma rápido)

# ==================== CONFIGURACIÓN DE CONTEO ====================
# Parámetros para contar vacas de forma confiable

MOVE_THRESH = 3.0            # Umbral de movimiento en píxeles
                              # Una vaca se considera "estacionaria" si no se mueve más de esto
                              # en STATIONARY_FRAMES frames
                              # Recomendado: 3-10

STATIONARY_FRAMES = 10       # Número de frames consecutivos que una vaca debe estar
                              # estacionaria para ser contada
                              # Mayor = más confiable pero más lento
                              # Recomendado: 10-30

# ==================== CONFIGURACIÓN DE PROCESAMIENTO ====================

FRAME_SKIP = 1               # Procesar cada Nth frame (1 = procesar todos)
                              # Aumentar para procesar más rápido pero con menos precisión
                              # Recomendado: 1 (procesar todos)

LINE_POSITION = 0.5          # Relativo a la altura (0.5 = mitad, no usado actualmente)

# ==================== NOTAS DE TUNING ====================
"""
Para MEJORAR DETECCIÓN DE VACAS CERCANAS Y EN MOVIMIENTO:
1. Reducir CONFIDENCE_THRESHOLD (ej: 0.15-0.25)
2. Usar modelo más grande (ej: yolov8s.pt en lugar de yolov8n.pt)
3. Si tienes GPU, usar DEVICE='cuda'
4. Aumentar IMGSZ a 1024 (más preciso pero lento)

Para MEJORAR CONTEO CONFIABLE (menos duplicados):
1. Aumentar STATIONARY_FRAMES (ej: 20-30)
2. Reducir MOVE_THRESH para ser más estricto
3. Aumentar N_INIT_TRACKER (requiere más frames para confirmar)

Para MEJORAR PERFORMANCE:
1. Usar modelo nano (yolov8n.pt)
2. Reducir IMGSZ a 416
3. Usar DEVICE='cuda' si está disponible
4. Aumentar FRAME_SKIP (procesar menos frames)
"""
