# 🚀 INSTRUCCIONES PARA ENTRENAR - AgroGuardian YOLOv8

Guía paso a paso para preparar y entrenar el modelo YOLOv8n personalizado para detección de vacas.

---

## 📋 ESTRUCTURA ACTUAL DEL PROYECTO

```
Agroguardian-model/
├── data/
│   ├── datasets/
│   │   ├── data.yaml                    ✅ Configuración (CORREGIDO para Roboflow)
│   │   └── cows/
│   │       ├── images/
│   │       │   ├── train/              ← Aquí van tus imágenes de entrenamiento
│   │       │   ├── val/                ← Imágenes de validación
│   │       │   └── test/               ← Imágenes de prueba (opcional)
│   │       └── labels/
│   │           ├── train/              ← Anotaciones YOLO (.txt)
│   │           ├── val/
│   │           └── test/
│   ├── models/
│   │   ├── yolov8n.pt                  ✅ Modelo Nano (ligero)
│   │   └── yolov8s.pt                  ❌ SERÁ ELIMINADO
│   ├── trained_models/                 ✅ Aquí se guardarán modelos entrenados
│   ├── outputs/                        ✅ Videos procesados
│   ├── runs/                           ✅ Logs de entrenamiento
│   └── src/
│       ├── config.py                   ✅ Configuración centralizada
│       ├── train.py                    ✅ Script de entrenamiento
│       ├── main.py                     ✅ Script de procesamiento de videos
│       ├── detector.py                 ✅ Detector YOLO
│       ├── tracker.py                  ✅ Tracking DeepSORT
│       ├── counter.py                  ✅ Lógica de conteo
│       ├── visualizer.py               ✅ Visualización
│       ├── utils.py                    ✅ Utilidades
│       └── prepare_dataset.py           ✅ Preparación de dataset
├── venv/                               ✅ Virtual environment
└── requirements.txt                    ✅ Dependencias
```

---

## ✅ VERIFICACIÓN PRE-ENTRENAMIENTO

Ejecuta esto en PowerShell desde el directorio del proyecto:

```powershell
# 1. Activar virtual environment
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
.\venv\Scripts\Activate.ps1

# 2. Verificar instalación
cd data\src
python -c "import cv2, ultralytics, deep_sort_realtime; print('✓ Todas las librerías instaladas')"

# 3. Validar estructura
python -c "from config import *; print(f'✓ Config OK: Modelo={DEFAULT_DETECT_MODEL}'); import os; print(f'✓ Datasets: {os.path.exists(\"../datasets/cows\")}')"
```

---

## 🔄 PASO 1: PREPARAR DATASET (Roboflow Format)

### Opción A: Descargar desde Roboflow

1. **Ir a [roboflow.com](https://roboflow.com/)**
   - Crear cuenta/Login
   - Crear proyecto: "cattle-detection"
   - Seleccionar formato: **YOLO v8**

2. **Subir imágenes y anotar**
   - Subir imágenes (JPG/PNG)
   - Anotar vacas con bounding boxes
   - Mínimo 200 imágenes recomendado

3. **Descargar dataset**
   - Ir a "Export" → Seleccionar **"YOLO v8"**
   - Descargar (te da un ZIP con la estructura correcta)

4. **Extraer en carpeta correcta**
   ```powershell
   # Descomprime el ZIP descargado (ej: cattle-detection-1.zip)
   # Debería tener esta estructura:
   # ├── images/
   # │   ├── train/
   # │   ├── valid/     ← Nota: Roboflow usa "valid" en lugar de "val"
   # │   └── test/
   # └── labels/
   #     ├── train/
   #     ├── valid/
   #     └── test/
   
   # Copiar imágenes:
   Copy-Item "descarga\images\train\*" "data\datasets\cows\images\train\" -Force
   Copy-Item "descarga\images\valid\*" "data\datasets\cows\images\val\" -Force
   Copy-Item "descarga\images\test\*" "data\datasets\cows\images\test\" -Force -ErrorAction SilentlyContinue
   
   # Copiar etiquetas:
   Copy-Item "descarga\labels\train\*" "data\datasets\cows\labels\train\" -Force
   Copy-Item "descarga\labels\valid\*" "data\datasets\cows\labels\val\" -Force
   Copy-Item "descarga\labels\test\*" "data\datasets\cows\labels\test\" -Force -ErrorAction SilentlyContinue
   ```

### Opción B: Dataset Manual

Si tienes imágenes anotadas ya:

1. Copiar imágenes a: `data\datasets\cows\images\{train,val,test}`
2. Copiar etiquetas (.txt en formato YOLO) a: `data\datasets\cows\labels\{train,val,test}`

**Formato YOLO (.txt)**:
```
<class_id> <x_center> <y_center> <width> <height>
0 0.512 0.456 0.234 0.345
```

---

## ✅ PASO 2: VERIFICAR ESTRUCTURA DE DATOS

Ejecuta desde PowerShell en `data/src`:

```powershell
# Contar imágenes y etiquetas
$train_images = (Get-ChildItem "..\datasets\cows\images\train" -Filter "*.jpg" -o "*.png" | Measure-Object).Count
$val_images = (Get-ChildItem "..\datasets\cows\images\val" -Filter "*.jpg" -o "*.png" | Measure-Object).Count
$test_images = (Get-ChildItem "..\datasets\cows\images\test" -Filter "*.jpg" -o "*.png" | Measure-Object).Count

Write-Host "📊 Dataset Status:"
Write-Host "  Train: $train_images imágenes"
Write-Host "  Val:   $val_images imágenes"
Write-Host "  Test:  $test_images imágenes"

# Verificar data.yaml
python -c "import yaml; data = yaml.safe_load(open('../datasets/data.yaml')); print(f\"✓ Dataset path: {data['path']}\"); print(f\"✓ Classes: {data['names']}\")"
```

---

## 🚀 PASO 3: ENTRENAR MODELO (YOLOv8n)

### Entrenamiento Básico

```powershell
# Activar environment si no está activado
.\venv\Scripts\Activate.ps1

# Ir al directorio src
cd data\src

# Ejecutar entrenamiento (YOLOv8n - recomendado)
python train.py --model yolov8n.pt --epochs 50 --batch 16 --device cpu
```

**Parámetros de entrenamiento:**

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `--model` | `yolov8n.pt` | Usar modelo Nano (ligero, rápido) |
| `--epochs` | 50 | Número de epochs (aumentar a 100 para mejor precisión) |
| `--batch` | 16 | Batch size (reducir a 8 si da error de memoria) |
| `--imgsz` | 640 | Tamaño de imagen |
| `--device` | `cpu` | Usar CPU (o `0` para GPU NVIDIA) |
| `--augment` | (flag) | Activar augmentación de datos |

### Entrenamiento Optimizado (GPU)

Si tienes GPU NVIDIA:

```powershell
python train.py `
  --model yolov8n.pt `
  --epochs 100 `
  --batch 32 `
  --device 0 `
  --augment
```

### Entrenamiento Optimizado (CPU)

Para mejores resultados sin GPU:

```powershell
python train.py `
  --model yolov8n.pt `
  --epochs 80 `
  --batch 8 `
  --device cpu `
  --augment
```

---

## 📊 MONITOREAR ENTRENAMIENTO

Mientras se entrena, verás:

```
Epoch 1/50
 100% 16/16 [00:15<00:00, 1.05s/it]
       Class   Images   Targets          P          R      mAP50   mAP50-95: 100% 16/16 [00:15<00:00, 1.05s/it]
         all       16       16      0.234      0.567      0.356      0.123
         cow       16       16      0.234      0.567      0.356      0.123
```

**Métricas importantes:**
- **P (Precisión)**: % de detecciones correctas
- **R (Recall)**: % de vacas detectadas correctamente
- **mAP50**: Precisión media (mejor es >0.7)
- **mAP50-95**: Métrica más estricta

---

## ✅ PASO 4: DESPUÉS DEL ENTRENAMIENTO

### 1. Encontrar modelo entrenado

El modelo se guarda en:
```
runs/cattle_detection/yolov8n_training/weights/best.pt
```

Copiar a trained_models:
```powershell
Copy-Item "runs\cattle_detection\yolov8n_training\weights\best.pt" "..\trained_models\yolov8n_cows_latest.pt" -Force
```

### 2. Validar modelo

```powershell
python -c "from ultralytics import YOLO; m = YOLO('../trained_models/yolov8n_cows_latest.pt'); print('✓ Modelo validado')"
```

### 3. Procesar video con modelo entrenado

```powershell
python main.py `
  --video ..\videos\cows.mp4 `
  --output ..\outputs\resultado.mp4 `
  --model ..\trained_models\yolov8n_cows_latest.pt `
  --conf 0.35 `
  --device cpu
```

---

## 🗑️ PASO 5: ELIMINAR yolov8s.pt

Una vez confirmado que yolov8n funciona bien:

```powershell
Remove-Item "data\models\yolov8s.pt" -Force
Write-Host "✓ yolov8s.pt eliminado"
```

---

## 🐛 TROUBLESHOOTING

### ❌ Error: "No module named 'ultralytics'"

```powershell
pip install ultralytics
```

### ❌ Error: "Dataset not found"

Verifica que exista: `data/datasets/cows/images/train/` con imágenes

```powershell
Get-ChildItem data\datasets\cows\images\train\
```

### ❌ Error: "CUDA out of memory"

Reducir batch size:
```powershell
python train.py --batch 4 --device cpu
```

### ❌ Entrenamiento muy lento

- Usar GPU si disponible: `--device 0`
- Reducir image size: `--imgsz 416`
- Reducir epochs inicialmente: `--epochs 20`

### ❌ Modelo entrenado tiene bajo accuracy

- Aumentar epochs: `--epochs 100`
- Mejor dataset: mínimo 500 imágenes
- Usar data augmentation: agregar `--augment`
- Ajustar confidence threshold en config.py

---

## 📈 PRÓXIMOS PASOS

1. ✅ Descargar dataset desde Roboflow
2. ✅ Entrenar modelo con yolov8n
3. ✅ Validar en videos
4. ✅ Ajustar parámetros si es necesario
5. ✅ Eliminar yolov8s.pt

---

## 📞 RESUMEN DE COMANDOS

```powershell
# Activar environment
.\venv\Scripts\Activate.ps1

# Entrenar
cd data\src
python train.py --model yolov8n.pt --epochs 50 --batch 16

# Procesar video
python main.py --video ../videos/cows.mp4 --output ../outputs/resultado.mp4

# Limpiar
Remove-Item ../models/yolov8s.pt -Force
```

---

✅ **Estructura lista para entrenar. Procede con los pasos indicados.**
