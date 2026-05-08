# TRAINING.md - Entrenar YOLOv8 Personalizado para Detección de Vacas

Guía completa para preparar datos, entrenar y optimizar un modelo YOLOv8 personalizado.

## 📋 Tabla de Contenidos

1. [Preparar Dataset](#preparar-dataset)
2. [Entrenar Modelo](#entrenar-modelo)
3. [Técnicas de Optimización ML](#técnicas-de-optimización-ml)
4. [Evaluación de Resultados](#evaluación-de-resultados)
5. [Troubleshooting](#troubleshooting)

---

## 📊 Preparar Dataset

### Estructura Esperada

```
data/datasets/cows/
├── images/
│   ├── train/          (70% de tus imágenes)
│   ├── val/            (15% de tus imágenes)
│   └── test/           (15% de tus imágenes)
│
└── labels/             (ANOTACIONES EN FORMATO YOLO)
    ├── train/
    ├── val/
    └── test/
```

### Formato de Anotaciones (YOLO Format)

Cada imagen `image.jpg` debe tener `image.txt` con:

```
<class_id> <x_center> <y_center> <width> <height>
0 0.512 0.456 0.234 0.345
0 0.712 0.356 0.156 0.267
```

**Donde:**
- `class_id` = 0 (para vacas, cambiar si usas múltiples clases)
- Coordenadas **normalizadas** entre 0-1

### Herramientas para Anotar

**Opción 1: Roboflow (Recomendado - Gratis)**
1. Sube imágenes a https://roboflow.com/
2. Anota vacas (bounding boxes)
3. Descarga en formato YOLO
4. Copia a `data/datasets/cows/`

**Opción 2: Label Studio (Local)**
```bash
pip install label-studio
label-studio
```

**Opción 3: CVAT (Profesional)**
- Descarga desde https://www.cvat.ai/
- Interfaz web potente

### Reglas para Buenas Anotaciones

- ✅ Bounding boxes **ajustados** al cuerpo de la vaca
- ✅ Mínimo **200 imágenes** por set (train/val/test)
- ✅ Mínimo **3 vacas** diferentes en el dataset
- ✅ Variedad: diferentes ángulos, iluminación, distancias
- ✅ Validar: revisar 10% aleatorio antes de entrenar

---

## 🚀 Entrenar Modelo

### Inicio Rápido

```bash
cd data/src
python train.py --dataset cows --epochs 50 --batch 16
```

### Opciones de Entrenamiento

```bash
python train.py \
    --dataset cows              # Nombre del dataset
    --model yolov8s.pt          # Modelo base (n/s/m/l)
    --epochs 100                # Número de epochs
    --batch 32                  # Tamaño de batch
    --imgsz 640                 # Tamaño de imagen (416/640/1024)
    --device cuda               # GPU (si disponible)
    --patience 30               # Early stopping
    --augment                   # Activar augmentación agresiva
```

### Duración Estimada

| Dispositivo | Modelo | Epochs | Duración |
|-----------|--------|--------|----------|
| CPU | yolov8n | 50 | 8-12 horas |
| CPU | yolov8s | 50 | 15-20 horas |
| GPU (RTX 3060) | yolov8s | 50 | 30-45 minutos |
| GPU (RTX 4090) | yolov8l | 100 | 20-30 minutos |

### Monitoreo Entrenamiento

Durante el entrenamiento, se generan en `data/runs/train_YYYYMMDD_HHMMSS/`:

- `results.csv` - Métricas por epoch
- `results.png` - Gráficos de loss y mAP
- `weights/best.pt` - Mejor modelo
- `weights/last.pt` - Último checkpoint

---

## 🧠 Técnicas de Optimización ML

### 1. Transfer Learning (Lo que ya hacemos)

Iniciamos desde `yolov8n.pt` (pre-entrenado en ImageNet):

```python
model = YOLO('yolov8n.pt')  # Pesos pre-entrenados
model.train(...)            # Fine-tuning
```

**Ventaja:** 
- Entrena 10x más rápido
- Necesita menos datos
- Mejor generalización

---

### 2. Data Augmentation (Aumentar Datos)

Rotación, flip, zoom automático:

```bash
python train.py --augment
```

Técnicas aplicadas:
- **HSV Jitter**: Cambios de color realistas
- **Rotación**: -10 a +10 grados
- **Flip**: Horizontal y vertical (50%)
- **Escalado**: 0.5x a 2.0x
- **Mosaic**: Combina 4 imágenes en 1

---

### 3. Ajuste de Hiperparámetros

**Para Precisión (menos falsos positivos):**
```bash
python train.py \
    --epochs 100        # Entrenar más
    --batch 32          # Batch mayor
    --augment           # Más variedad
```

**Para Velocidad (menos preciso pero rápido):**
```bash
python train.py \
    --model yolov8n.pt  # Modelo pequeño
    --imgsz 416         # Imagen más pequeña
    --batch 64          # Batch grande
```

**Balanced (Recomendado):**
```bash
python train.py \
    --model yolov8s.pt  # Small (balance)
    --epochs 50         # Suficiente
    --batch 32          # Standard
    --imgsz 640         # Standard
```

---

### 4. Métricas Importantes

**mAP (Mean Average Precision)**
- `mAP50`: % correcto con IoU ≥ 0.5
- `mAP50-95`: Promedio riguroso (0.5 a 0.95)
- **Target**: > 0.80 es bueno

**Ejemplo interpretación:**
```
mAP50: 0.92    ✅ Muy bueno (92% de precisión)
mAP50-95: 0.65 ⚠️  Necesita ajuste (bboxes imprecisas)
```

---

### 5. Validación Cruzada

Si tienes dataset pequeño:

```python
# Dividir: 80% train, 20% val
# Repetir 5 veces con diferentes splits
# Promediar resultados
```

Ultralytics lo hace automáticamente si configurar `val=True`.

---

### 6. Ensemble (Combinar Modelos)

Entrenar múltiples tamaños y promediar predicciones:

```bash
# Entrena modelos de diferente tamaño
python train.py --model yolov8n.pt --epochs 50
python train.py --model yolov8s.pt --epochs 50
python train.py --model yolov8m.pt --epochs 50

# Luego combinarlos es manual (ver código)
```

---

### 7. Clase Imbalanceada (Vacas vs Fondo)

YOLO maneja automáticamente, pero puedes:

```python
# Pesar pérdida más en vacas
class_weight = [10.0]  # 10x peso en vacas
```

---

## 📊 Evaluación de Resultados

### Revisar Entrenamiento

```bash
# Ver gráficos
cd data/runs/train_YYYYMMDD_HHMMSS/
# Abre results.png
```

Busca:
- ✅ **Loss decrece** (baja suavemente)
- ✅ **mAP sube** (aumenta con epochs)
- ❌ **Overfitting** (val loss sube, train loss baja)

### Prueba Modelo Entrenado

```bash
# Editar config.py
MODEL_PATH = 'data/trained_models/yolov8_cows_YYYYMMDD_HHMMSS.pt'

# Ejecutar
python main.py --video ../videos/test.mp4 --output ../outputs/resultado.mp4
```

### Comparar Modelos

```bash
# Base (pre-entrenado)
python main.py --video ../videos/test.mp4  # CON yolov8n.pt original

# Personalizado (entrenado)
python main.py --video ../videos/test.mp4  # CON modelo entrenado

# Comparar resultados
```

---

## 🔧 Troubleshooting

### "CUDA out of memory"
```bash
python train.py --batch 8 --device cpu  # Reduce batch o usa CPU
```

### "Val loss no baja"
```bash
# Revisar anotaciones (pueden estar mal)
# Aumentar epochs
python train.py --epochs 150 --patience 50
```

### "Modelo detecta todo pero impreciso"
```bash
# Aumentar confianza
CONFIDENCE_THRESHOLD = 0.5  # en config.py

# Entrenar más epochs
python train.py --epochs 150
```

### "No detecta vacas lejanas"
```bash
# Aumentar imgsz
python train.py --imgsz 1024

# Entrenar con vacas lejanas en dataset
```

---

## 📈 Workflow Completo (Paso a Paso)

```
1. Reunir ~500-1000 imágenes de vacas
   ↓
2. Anotar en Roboflow/CVAT (con bounding boxes)
   ↓
3. Descargar en formato YOLO → data/datasets/cows/
   ↓
4. Editar data/datasets/data.yaml (rutas)
   ↓
5. Entrenar:
   python train.py --model yolov8s.pt --epochs 50
   ↓
6. Ver resultados en data/runs/
   ↓
7. Si mAP > 0.80: Usar el modelo
   Si mAP < 0.70: Mejorar anotaciones y reintentar
   ↓
8. Copiar best.pt a data/trained_models/
   ↓
9. Actualizar config.py con nueva ruta
   ↓
10. ¡Usar en producción!
```

---

## 💡 Pro Tips

1. **Más datos > Mejor modelo**: 1000 imágenes bien anotadas > 100 mal anotadas
2. **Validación manual**: Revisa 10% de predicciones en validation set
3. **Iteración**: Entrena, evalúa, mejora dataset, vuelve a entrenar
4. **GPU es importante**: Si tienes acceso a GPU, úsala (10-50x más rápido)
5. **Documentar**: Guarda nombres de modelos con fecha y mAP

---

## 🚀 Siguientes Pasos

- Entrenar con ByteTrack en vez de DeepSORT
- Agregar detección de líneas de conteo
- Exportar a ONNX para inferencia optimizada
- Desplegar en Jetson/RPi (optimizado)
