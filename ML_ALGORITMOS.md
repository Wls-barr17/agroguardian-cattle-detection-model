# 🧠 ML & ALGORITMOS - Explicación Técnica

Cómo funcionan los algoritmos de Machine Learning en este sistema y cómo optimarlos.

---

## 🎯 Qué es YOLO (You Only Look Once)

YOLO es una red neuronal que predice bounding boxes en una sola pasada:

```
Imagen (832x464) 
    ↓
[Red Neuronal Convolucional]
    ↓
Detecciones: [(x,y,w,h,clase,confianza), ...]
```

**Diferencia con otros métodos:**
- ❌ R-CNN: Lento (propone regiones primero)
- ❌ SSD: Menos preciso
- ✅ YOLO: Rápido y preciso

---

## 🧬 Arquitectura de YOLO

### Input → Backbone → Neck → Head → Output

```
Imagen RGB (640x640x3)
    ↓
[Backbone: Extrae features]  ← Busca patrones (bordes, formas)
    ↓
[Neck: Fusiona información] ← Combina features de múltiples escalas
    ↓
[Head: Predice boxes]        ← Genera coordenadas + confianza
    ↓
(x₁,y₁,x₂,y₂,conf,clase)    ← Bounding boxes finales
```

### Features (Características) = Vectores

Cada capa genera **mapas de características** que representan patrones:

```
Input: [832 x 464 x 3]  (RGB)
↓
Conv Layer 1: [416 x 232 x 32]  (detecta bordes)
↓
Conv Layer 2: [208 x 116 x 64]  (detecta formas)
↓
Conv Layer 3: [104 x 58 x 128]  (detecta texturas)
↓
...
↓
Output: [1 x 1 x 255]   (predicciones finales)
```

Cada valor en estos mapas es un **vector** que contiene información.

---

## 📊 Loss Function (Función de Pérdida)

Mide cuán "mal" está el modelo. Entrenar = reducir esto:

```
Total Loss = (Localization Loss) + (Objectness Loss) + (Classification Loss)
             ↓                       ↓                   ↓
         ¿Bbox exacta?         ¿Hay objeto?        ¿Qué clase?
```

### Ejemplo concreto:

```
Predicción: bbox=[10,20,100,100], conf=0.8, clase=vaca
Verdad:     bbox=[12,22,102,98],  conf=1.0, clase=vaca

Loss = |10-12|² + |20-22|² + (0.8-1.0)² + 0
     = 4 + 4 + 0.04 + 0 = 8.04
```

Entrenar ajusta pesos para minimizar esto.

---

## 🎓 Transfer Learning (Lo que Usamos)

En vez de entrenar desde cero (pesos aleatorios):

```
Opción 1: ENTRENAR DESDE CERO
Random weights → Época 1: Loss=500
              → Época 2: Loss=450
              → Época 50: Loss=50
              ❌ Lento, necesita 10,000+ imágenes

Opción 2: TRANSFER LEARNING (Lo que hacemos)
Pre-trained weights (ImageNet) → Época 1: Loss=100
                               → Época 2: Loss=80
                               → Época 50: Loss=20
                               ✅ Rápido, necesita 500 imágenes
```

**Por qué funciona:**
- La red ya aprendió a detectar: bordes, curvas, patrones básicos
- Solo ajusta los últimos layers para vacas
- Como enseñar a un biólogo sobre vacas vs enseñar a un niño

---

## 🔢 Métricas de Evaluación

### IoU (Intersection over Union)

```
Predicción: [━━━━]
Verdad:      [  ━━━━]
             Overlap
             
IoU = Overlap / (Pred + Verdad - Overlap)
    = 2 / (4 + 4 - 2) = 2/6 = 0.33 = 33%
```

### Precision & Recall

```
Precision = TP / (TP + FP)
          = Vacas correctas / (Todas predichas)
          = 90/100 = 90%  (de las que detectamos, 90% son reales)

Recall = TP / (TP + FN)
       = Vacas correctas / (Todas reales)
       = 90/100 = 90%   (encontramos 90% de las vacas totales)
```

### mAP (Mean Average Precision)

```
mAP = Promedio de Precision a diferentes thresholds de IoU

mAP50:    IoU > 0.5  (generoso, menos exacto)   ← Usualmente 0.80-0.95
mAP75:    IoU > 0.75 (normal)                     ← 0.70-0.90
mAP50-95: IoU > 0.5,0.55...0.95 (muy estricto)  ← 0.50-0.80
```

---

## 🎯 Data Augmentation (Aumentar Variedad)

Durante entrenamiento, modificamos imágenes para que la red generalice:

```
Imagen original → Se aplica ALEATORIAMENTE:
  ├── Rotación: -15° a +15°
  ├── Flip: Horizontal, Vertical
  ├── Zoom: 0.8x a 1.2x
  ├── HSV: Cambios de color
  ├── Blur: Desenfoque
  └── Noise: Ruido aleatorio

Resultado: Red ve 1 imagen como 10 variaciones
          → Aprende más robusto
```

---

## 🚀 Optimizadores (Algoritmos de Entrenamiento)

### SGD (Stochastic Gradient Descent)

```
Pensar en descender una montaña en la oscuridad:

while not en_minimo:
    pendiente = calcular_gradiente()
    paso = pendiente * learning_rate
    posición -= paso
```

### Adam (Lo que YOLO usa)

Mejora de SGD que adapta el learning rate:

```
while not en_minimo:
    gradiente = calcular_gradiente()
    momentum = 0.9 * momentum + 0.1 * gradiente
    posición -= learning_rate * momentum
```

Mejor que SGD para converger rápido.

---

## 🔧 Técnicas de Optimización Para Tu Caso

### 1️⃣ Aumentar Datos (Data Augmentation)

```bash
python train.py --augment  # Activa rotación, flip, zoom
```

**Vectorialmente:** Genera más puntos de entrenamiento en espacio de características.

---

### 2️⃣ Aumentar Epochs

```bash
python train.py --epochs 150  # Más iteraciones
```

**Vectorialmente:** La red tiene más oportunidades de ajustar pesos (w, b).

---

### 3️⃣ Aumentar Tamaño de Imagen

```bash
python train.py --imgsz 1024  # De 640 a 1024
```

**Vectorialmente:** Más "resolución" en los vectores de características.

---

### 4️⃣ Batch Normalization (Automático en YOLO)

Normaliza los vectores internos:

```
Input: [100, 0.1, 1000]  ← Escalas diferentes
       ↓
Batch Norm: [0.5, -0.8, 0.3]  ← Normalizados
            ↓
Faster training, más estable
```

---

### 5️⃣ Early Stopping

```bash
python train.py --patience 30  # Detiene si no mejora en 30 epochs
```

Evita overfitting:

```
Epoch 1-50: mAP sube (aprende)
Epoch 51-80: mAP baja (memoriza datos de entrenamiento)
            ↑ DETIENE AQUÍ
```

---

## 📈 Monitoreo de Entrenamiento

### Qué Buscar en los Gráficos

```
IDEAL:
train_loss: ↘️ ↘️ ↘️ (cae suave)
val_loss: ↘️ ↘️ ↘️   (cae suave)
mAP: ↗️ ↗️ ↗️         (sube suave)

OVERFITTING:
train_loss: ↘️ ↘️ ↘️ (cae)
val_loss: ↗️ ↗️ ↗️   (sube) ← PROBLEMA
         → Detener aquí

UNDERFITTING:
train_loss: ↘️ pero lentamente
val_loss: no baja
         → Aumentar epochs o modelo
```

---

## 🎯 DeepSORT (Tracking)

Después de YOLO detecta, DeepSORT mantiene IDs:

```
Frame 1: Detecta [vaca1@(100,200), vaca2@(300,400)]
         ↓
Frame 2: Detecta [vaca@(102,205), vaca@(298,395)]
         ↓
DeepSORT: Asocia mediante DISTANCIA EUCLIDIANA
         vaca1 se movió (100,200)→(102,205) = distancia 2.8
         vaca2 se movió (300,400)→(298,395) = distancia 3.16
         ↓
         ID 1 = vaca1, ID 2 = vaca2
```

Usa **vectores de features** de CNN para diferenciar vacas.

---

## 💡 Resumen: Cómo Funciona Todo Junto

```
1. INPUT: Imagen 832x464
   ↓
2. YOLO: Extrae vectores de características
         Predice: [(bbox1, conf1, clase1), ...]
   ↓
3. TRACKER (DeepSORT): Mantiene IDs usando vectores de features
   ↓
4. COUNTER: Si la vaca está "quieta" (se movió <3px en 10 frames)
            Incrementa contador
   ↓
5. OUTPUT: Frame anotado con bboxes, IDs, contador
```

---

## 🚀 Cómo Mejorar Precisión (Resumen)

| Técnica | Mejora | Costo |
|---------|--------|-------|
| Aumentar epochs | +5% | Tiempo |
| Data augmentation | +10% | Complejidad |
| Mejor dataset | +20% | Anotación manual |
| Modelo más grande (s→m) | +8% | GPU/CPU más rápida |
| Aumentar imgsz | +5% | Velocidad |
| Ensemble (3 modelos) | +10% | 3x más lento |

**Más impacto: DATOS > MODELO > PARÁMETROS**

---

## 📚 Recursos

- Papers: https://arxiv.org/abs/2301.07715 (YOLOv8)
- Docs: https://docs.ultralytics.com/
- Tutorial: https://github.com/ultralytics/yolov8
