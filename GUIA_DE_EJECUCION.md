# 🎯 GUÍA DE EJECUCIÓN - AgroGuardian Ready to Train

**Estado Actual**: ✅ SISTEMA 100% LISTO PARA ENTRENAR  
**Modelo**: YOLOv8n (Nano - Optimizado)  
**Framework**: Ultralytics YOLOv8 + DeepSORT + OpenCV  
**Fecha**: 13 de Mayo, 2026

---

## 📊 ESTADO ACTUAL DEL SISTEMA

```
✅ Estructura de directorios:        COMPLETADA
✅ data.yaml configurado:            ROBOFLOW FORMAT
✅ Carpetas de dataset:              CREADAS (vacías, listas para llenar)
✅ Modelo yolov8n.pt:                DISPONIBLE (6.2 MB)
❌ Modelo yolov8s.pt:                ELIMINADO (21.5 MB liberados)
✅ Scripts Python:                   TODOS FUNCIONALES
✅ Configuración centralizada:       LISTA (config.py)
✅ Documentación:                    COMPLETA
```

---

## 🚀 INSTRUCCIONES PASO A PASO

### PASO 1️⃣ : DESCARGAR DATASET (Roboflow)

**IMPORTANTE**: Necesitas imágenes anotadas con vacas en formato YOLO.

#### Opción A: Usar Roboflow (RECOMENDADO)

1. **Ir a [roboflow.com](https://roboflow.com/)**
   
2. **Crear Proyecto**
   - Click en "Create Project"
   - Nombre: `cattle-detection`
   - Seleccionar: "Object Detection"

3. **Subir Imágenes**
   - Subir mínimo **200 imágenes** (mejor 500+)
   - Formatos: JPG, PNG, JPEG
   - Tamaño: máximo 5MB por imagen

4. **Anotar Vacas**
   - Para cada imagen, dibujar bounding boxes alrededor de las vacas
   - Asignar label: `cow`
   - Mínimo 2-3 vacas por imagen

5. **Dividir en Sets** (automático en Roboflow)
   - Train: 70%
   - Valid: 15%  
   - Test: 15%

6. **Exportar en Formato YOLO v8**
   - Click en "Export"
   - Seleccionar: "YOLO v8"
   - Descargar ZIP

7. **Extraer Dataset**
   ```powershell
   # Descomprime el ZIP descargado
   # Debería contener:
   # ├── images/
   # │   ├── train/
   # │   ├── valid/     ← Nota: "valid" no "val"
   # │   └── test/
   # └── labels/
   #     ├── train/
   #     ├── valid/
   #     └── test/
   
   # Copiar imágenes (desde PowerShell):
   Copy-Item "ruta\descarga\images\train\*" "data\datasets\cows\images\train\" -Force
   Copy-Item "ruta\descarga\images\valid\*" "data\datasets\cows\images\val\" -Force
   Copy-Item "ruta\descarga\images\test\*" "data\datasets\cows\images\test\" -Force -ErrorAction SilentlyContinue
   
   # Copiar etiquetas:
   Copy-Item "ruta\descarga\labels\train\*" "data\datasets\cows\labels\train\" -Force
   Copy-Item "ruta\descarga\labels\valid\*" "data\datasets\cows\labels\val\" -Force
   Copy-Item "ruta\descarga\labels\test\*" "data\datasets\cows\labels\test\" -Force -ErrorAction SilentlyContinue
   ```

#### Opción B: Dataset Ya Anotado

Si tienes imágenes con etiquetas YOLO lisas:

1. Copiar imágenes a:
   ```
   data/datasets/cows/images/{train,val,test}/
   ```

2. Copiar etiquetas (.txt) a:
   ```
   data/datasets/cows/labels/{train,val,test}/
   ```

**Formato YOLO (.txt)**:
```
<class_id> <x_center> <y_center> <width> <height>
0 0.512 0.456 0.234 0.345
0 0.712 0.156 0.234 0.345
```

---

### PASO 2️⃣ : VERIFICAR DATASET

Ejecuta esto desde PowerShell:

```powershell
# Navegar a proyecto
cd c:\Users\Yunio\Downloads\Agroguardian-model
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
.\venv\Scripts\Activate.ps1

# Ir a src
cd data\src

# Contar imágenes
$train_imgs = (Get-ChildItem "..\datasets\cows\images\train" | Measure-Object).Count
$val_imgs = (Get-ChildItem "..\datasets\cows\images\val" | Measure-Object).Count
$test_imgs = (Get-ChildItem "..\datasets\cows\images\test" | Measure-Object).Count

Write-Host "📊 Dataset Preparado:"
Write-Host "  Train: $train_imgs imágenes"
Write-Host "  Val:   $val_imgs imágenes"
Write-Host "  Test:  $test_imgs imágenes"

# Verificación completa
python verify_and_cleanup.py
```

**Salida esperada:**
```
✓ Estructura: OK
✓ Dataset: OK
✓ Modelos: LISTO
```

---

### PASO 3️⃣ : ENTRENAR MODELO (YOLOv8n)

**Opción A: Entrenamiento Rápido (CPU - 2-3 horas)**

```powershell
# Ya en data\src\
python train.py --model yolov8n.pt --epochs 50 --batch 16 --device cpu
```

**Opción B: Entrenamiento Optimizado (CPU - Mejor precisión, más lento)**

```powershell
python train.py `
  --model yolov8n.pt `
  --epochs 100 `
  --batch 8 `
  --device cpu `
  --augment
```

**Opción C: Entrenamiento GPU NVIDIA (Muy rápido)**

```powershell
python train.py `
  --model yolov8n.pt `
  --epochs 100 `
  --batch 32 `
  --device 0 `
  --augment
```

---

### 📈 MONITOREO DE ENTRENAMIENTO

Mientras se ejecuta, verás:

```
Epoch 1/50
 100%  16/16  [00:15<00:00, 1.05s/it]
    Class   Images   Targets      P      R   mAP50  mAP50-95
      all       16       16  0.234  0.567  0.356    0.123
      cow       16       16  0.234  0.567  0.356    0.123
```

**Indicadores de buen entrenamiento:**
- mAP50 aumenta cada epoch
- P y R se mantienen altos (>0.6)
- Loss disminuye

---

### PASO 4️⃣ : DESPUÉS DEL ENTRENAMIENTO

El modelo entrenado se guarda en:
```
runs/cattle_detection/yolov8n_training/weights/best.pt
```

**Copiar a trained_models:**
```powershell
Copy-Item "runs\cattle_detection\yolov8n_training\weights\best.pt" "..\trained_models\yolov8n_cows_best.pt" -Force
Write-Host "✓ Modelo copiado a trained_models\"
```

---

### PASO 5️⃣ : PROCESAR VIDEO CON MODELO ENTRENADO

```powershell
# Con modelo personalizado
python main.py `
  --video ..\videos\cows.mp4 `
  --output ..\outputs\resultado_detectado.mp4 `
  --model ..\trained_models\yolov8n_cows_best.pt `
  --conf 0.35 `
  --device cpu
```

**Resultado:**
- ✅ Video con vacas detectadas (bounding boxes)
- ✅ Tracking de IDs individuales
- ✅ Conteo automático
- ✅ FPS mostrado en esquina superior

---

## 📋 TABLA DE CONFIGURACIÓN RECOMENDADA

### CPU (Sin GPU):
```
Epochs:     50-100
Batch:      8-16
Image Size: 640
Device:     cpu
Tiempo:     2-4 horas
```

### GPU NVIDIA (Disponible):
```
Epochs:     100-200
Batch:      32-64
Image Size: 640
Device:     0 (o 1, 2, etc)
Tiempo:     30-60 minutos
```

### Presupuesto Limitado (Dataset pequeño <100 img):
```
Epochs:     30-50
Batch:      8
Image Size: 416
Device:     cpu
Augment:    Activar
```

---

## 🔧 PARÁMETROS AJUSTABLES (en config.py)

```python
# Detección
CONFIDENCE_THRESHOLD = 0.35        # Umbral mínimo (0-1)
IOU_THRESHOLD = 0.5               # NMS threshold

# Tracking
MAX_AGE = 30                      # Frames para perder track
MIN_STATIONARY_FRAMES = 10        # Antes de contar

# Entrenamiento
EPOCHS = 50
BATCH_SIZE = 16
TRAINING_BASE_MODEL = "yolov8n.pt"
DEVICE = "cpu"
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "No module named 'ultralytics'"
```powershell
pip install ultralytics
```

### ❌ Error: "data.yaml not found"
Verificar que existe: `data/datasets/data.yaml`
```powershell
Get-Item data\datasets\data.yaml
```

### ❌ Error: "Dataset not found"
Las carpetas deben existir con al menos imágenes:
```powershell
Get-ChildItem data\datasets\cows\images\train\
```

### ❌ Entrenamiento muy lento (CPU)
- Usar GPU si disponible: `--device 0`
- Reducir epochs: `--epochs 25`
- Reducir tamaño imagen: `--imgsz 416`
- Reducir batch: `--batch 4`

### ❌ Bajo accuracy en validación
- Aumentar epochs: `--epochs 100-200`
- Mejor dataset: mínimo 500 imágenes
- Activar augmentation: `--augment`
- Dataset más variado (ángulos, iluminación, distancias)

### ⚠️ Out of Memory (CUDA)
```powershell
python train.py --batch 4 --device cpu
```

---

## 📞 RESUMEN DE COMANDOS RÁPIDOS

```powershell
# 1. Activar environment
.\venv\Scripts\Activate.ps1
cd data\src

# 2. Verificar sistema
python verify_and_cleanup.py

# 3. Entrenar (rápido)
python train.py --model yolov8n.pt --epochs 50 --batch 16

# 4. Entrenar (optimizado)
python train.py --model yolov8n.pt --epochs 100 --batch 8 --augment

# 5. Procesar video
python main.py --video ../videos/cows.mp4 --output ../outputs/resultado.mp4 --model ../trained_models/yolov8n_cows_best.pt

# 6. Ver logs
Get-Content ../logs/agroguardian.log -Tail 20
```

---

## ✅ CHECKLIST DE INICIO

- [ ] Dataset descargado de Roboflow (o imágenes anotadas)
- [ ] Imágenes en `data/datasets/cows/images/{train,val,test}/`
- [ ] Etiquetas en `data/datasets/cows/labels/{train,val,test}/`
- [ ] `verify_and_cleanup.py` retorna "OK"
- [ ] Espacio suficiente en disco (~5GB)
- [ ] Environment virtual activado
- [ ] Todas las dependencias instaladas

---

## 📊 ESTRUCTURA FINAL

```
data/
├── datasets/
│   ├── data.yaml                    ← Configuración
│   └── cows/
│       ├── images/
│       │   ├── train/               ← Imágenes a llenar
│       │   ├── val/
│       │   └── test/
│       └── labels/
│           ├── train/               ← Etiquetas a llenar
│           ├── val/
│           └── test/
├── models/
│   └── yolov8n.pt                   ← Modelo base
├── trained_models/                  ← Se generan aquí
├── outputs/                         ← Videos procesados
├── runs/                            ← Logs entrenamiento
└── src/
    ├── train.py                     ← ENTRENAR
    ├── main.py                      ← PROCESAR VIDEO
    ├── config.py
    ├── detector.py
    ├── tracker.py
    ├── counter.py
    ├── visualizer.py
    └── verify_and_cleanup.py
```

---

## 🎬 FLUJO DE TRABAJO VISUAL

```
INICIO
  ↓
[Descargar Dataset Roboflow] ← PASO 1
  ↓
[Copiar a data/datasets/cows/] ← PASO 2
  ↓
[Ejecutar verify_and_cleanup.py]
  ↓
[Entrenar: python train.py] ← PASO 3 (15 min - 3 horas)
  ↓
[Modelo guardado en runs/]
  ↓
[Copiar a trained_models/]
  ↓
[Procesar video: python main.py] ← PASO 4
  ↓
[Video con detecciones: outputs/]
  ↓
✅ LISTO PARA USAR
```

---

## 📈 MÉTRICAS DE ÉXITO

Después del entrenamiento, deberías ver:

| Métrica | Objetivo | Excelente |
|---------|----------|-----------|
| mAP50 | >0.60 | >0.75 |
| Precision (P) | >0.60 | >0.80 |
| Recall (R) | >0.60 | >0.80 |
| FPS (CPU) | >15 | >20 |
| FPS (GPU) | >60 | >120 |

---

## 📖 ARCHIVOS DE DOCUMENTACIÓN

- **INSTRUCCIONES_PARA_ENTRENAR.md** - Guía detallada
- **RESUMEN_CAMBIOS.md** - Cambios realizados
- **README.md** - Información general
- **TRAINING.md** - Técnicas de optimización

---

## ⏱️ TIEMPO ESTIMADO

| Tarea | Tiempo |
|-------|--------|
| Preparar dataset (Roboflow) | 30 min - 2 horas |
| Entrenar (50 epochs, CPU) | 2-3 horas |
| Entrenar (100 epochs, GPU) | 30-60 min |
| Procesar video | 5-15 min |
| **TOTAL** | **3-6 horas** |

---

## ✨ PRÓXIMA FASE (Después de entrenar)

1. ✅ Evaluar precisión en validación
2. ✅ Procesar videos de prueba
3. ✅ Ajustar confidence threshold si es necesario
4. ✅ Fine-tuning si resultados son bajos
5. ✅ Deplegamiento en producción

---

## 🚀 ¡LISTO PARA EMPEZAR!

**Ejecuta este comando ahora mismo:**

```powershell
# Desde PowerShell en la raíz del proyecto
.\venv\Scripts\Activate.ps1
cd data\src
python verify_and_cleanup.py
```

Si ves ✅ en los tres items, **estás 100% listo para entrenar**.

---

*Documento: AgroGuardian Ready to Train*  
*Versión: 1.0*  
*Estado: ✅ OPERATIONAL*  
*Última actualización: 2026-05-13*
