"""
config.py - Configuración centralizada de AgroGuardian

Este archivo contiene todos los parámetros del sistema.
Se carga una sola vez al iniciar el programa, por lo que los cambios
requieren reiniciar la aplicación.

Secciones:
- YOLO detection: modelos, umbrales, tamaños
- Tracking: persistencia de identidades
- Counting: lógica de conteo de vacas
- Features: activación/desactivación de características
"""

# ==================== CONFIGURACIÓN YOLO ====================

CONFIDENCE_THRESHOLD = 0.30  # Umbral de confianza mínima para considerar una detección
                              # 0.30: Detecta mejor objetos lejanos/pequeños
                              # 0.50+: Más preciso pero pierde objetos
                              # Ajusta según precisión deseada

IOU_THRESHOLD = 0.45        # Umbral de IoU para NMS (elimina boxes duplicadas)
                              # Valores bajos = elimina más duplicados
                              # Valores altos = mantiene boxes cercanos

IMGSZ = 640                 # Tamaño de imagen que ve el modelo
                              # 640 es el balance entre precisión y velocidad
                              # Aumentar a 1024 si tienes GPU y necesitas más precisión

DEVICE = 'cpu'              # 'cpu' para CPU, 'cuda' para GPU
                              # GPU es 10-20x más rápido para inferencia

# Ruta al modelo YOLO entrenado
MODEL_PATH = '../runs/runs/train_20260519_162008/weights/best.pt'
# Cuando reentrenes con más datos, actualiza a:
# './trained_models/yolov8_cows_YYYYMMDD_improved.pt'

# ==================== CONFIGURACIÓN TRACKER ====================
# DeepSORT mantiene identidades de vacas entre frames

MAX_AGE_TRACKER = 30        # Frames máximo sin actualización antes de eliminar track
                              # Valores altos mantienen tracks de objetos ocluidos
                              # Valores bajos = más estrictos (evita fantasmas)

N_INIT_TRACKER = 2          # Frames necesarios para confirmar un track como válido
                              # Valores bajos confirman rápido (más sensible)
                              # Valores altos requieren más frames (más robusto)

# ==================== CONFIGURACIÓN DE CONTEO ====================
# Estrategia: solo contar vacas estacionarias para evitar duplicados

MOVE_THRESH = 5.0           # Umbral de movimiento en píxeles
                              # Si una vaca se mueve más de esto, se considera activa
                              # Valores bajos = más estrictos

STATIONARY_FRAMES = 20      # Frames consecutivos sin movimiento para contar
                              # Valores altos = más confiable pero más lento
                              # Recomendado: 15-30 (depende de FPS del video)

# ==================== CONFIGURACIÓN DE PROCESAMIENTO ====================

FRAME_SKIP = 1              # Procesar cada Nth frame (1 = todos los frames)
                              # Aumentar para más velocidad pero menos precisión

LINE_POSITION = 0.5         # Posición normalizada (0-1) para línea de conteo
                              # Actualmente no se usa, reservado para futuro


# ==================== CARACTERÍSTICAS Y DETECCIÓN ====================
# Sistema preparado para agregar detección de personas

ENABLE_PERSON_DETECTION = False  # Cambiar a True cuando tengas modelo con clase "person"
                                  # El sistema detecta automáticamente si está disponible

# Este parámetro se sobrescribe automáticamente en detector.py:
# Si el modelo entrenado contiene la clase "person",
# ENABLE_PERSON_DETECTION se activa automáticamente


# ==================== NOTAS DE AJUSTE ====================
"""
PARA MEJORAR DETECCIÓN DE VACAS:
1. Reducir CONFIDENCE_THRESHOLD → 0.20 (más sensible, puede falsos positivos)
2. Aumentar IMGSZ → 1024 (más precisión si tienes GPU)
3. Usar GPU: DEVICE = 'cuda'
4. Reentrenar modelo con dataset más grande

PARA MEJORAR CONTEO (menos duplicados):
1. Aumentar STATIONARY_FRAMES → 30-40
2. Reducir MOVE_THRESH → 3.0
3. Aumentar N_INIT_TRACKER → 3-4

PARA AGREGAR DETECCIÓN DE PERSONAS:
1. Reentrenar modelo con dataset que incluya personas
2. ENABLE_PERSON_DETECTION se activará automáticamente
3. Los paneles de UI se actualizarán automáticamente
"""
