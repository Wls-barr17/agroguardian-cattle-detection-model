# 🚀 Instrucciones Detalladas para Reentrenamiento con Dataset Grande

## Resumen Ejecutivo

Tu modelo anterior fue entrenado con pocos datos. Ahora tienes un dataset más grande.

Este documento explica **exactamente** cómo reentrenar el modelo y reemplazar el anterior.

---

## 📋 PASO 1: Preparar el Dataset

### 1.1 Estructura Correcta

Tu dataset debe estar organizando así:

```
data/datasets/cows/
├── images/
│   ├── train/          (70% de imágenes)
│   ├── val/            (15% de imágenes)
│   └── test/           (15% de imágenes)
└── labels/
    ├── train/          (anotaciones YOLO)
    ├── val/            (anotaciones YOLO)
    └── test/           (anotaciones YOLO)
```

### 1.2 Formato de Anotaciones (YOLO)

Cada imagen debe tener un archivo `.txt` correspondiente con el mismo nombre.

**Ejemplo:** `imagen_vacas_001.jpg` → `imagen_vacas_001.txt`

**Contenido del .txt:**
```
0 0.5 0.5 0.3 0.4
0 0.2 0.3 0.1 0.2
```

Formato: `<class_id> <x_center> <y_center> <width> <height>`

Donde:
- `class_id` = `0` (para vacas, es la única clase)
- Coordenadas = normalizadas 0-1 (relativo al tamaño de la imagen)

**Si tus anotaciones son en otro formato** (JSON, XML, etc.):
- Usa [Roboflow](https://roboflow.com/) o script personalizado
- Convierte a formato YOLO antes de entrenar

### 1.3 Verificar Estructura

Ejecuta esto en PowerShell para verificar:

```powershell
# Ver estructura
Get-ChildItem -Recurse "data/datasets/cows/" | Measure-Object

# Ver sample de anotación
Get-Content "data/datasets/cows/labels/train/image_001.txt" | Select-Object -First 5
```

---

## 📊 PASO 2: Configurar data.yaml

Edita `data/datasets/data.yaml`:

```yaml
# Dataset configuration for YOLOv8
path: ../datasets/cows

train: train/images
val: val/images
test: test/images

nc: 1
names:
  0: cow
```

**IMPORTANTE:**
- `path:` debe apuntar a la carpeta `cows`
- `train:`, `val:`, `test:` son rutas RELATIVAS a `path:`
- `nc: 1` significa 1 clase (vacas solamente)
- `names:` mapea ID de clase a nombre legible

---

## 🤖 PASO 3: Entrenar el Modelo

### 3.1 Activar Entorno Virtual

```powershell
# Navegar a la carpeta del proyecto
cd C:\Users\Yunio\Downloads\Agroguardian-model

# Activar venv
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& .\venv\Scripts\Activate.ps1)
```

### 3.2 Comando de Entrenamiento

Ejecuta **UNO** de estos comandos según tu computadora:

#### 🔹 Opción A: Entrenamiento Estándar (RECOMENDADO)
```powershell
cd data\src

python train.py --dataset cows --model yolov8m.pt --epochs 100 --batch 16 --imgsz 640 --device cpu
```

**Parámetros:**
- `--dataset cows` = usa el dataset en `../datasets/cows`
- `--model yolov8m.pt` = modelo medium (buena precisión, moderada velocidad)
- `--epochs 100` = 100 ciclos de entrenamiento (puede tomar 2-4 horas en CPU)
- `--batch 16` = 16 imágenes por lote
- `--imgsz 640` = resuelve entrenamiento a 640x640 píxeles
- `--device cpu` = usar CPU (cambiar a `cuda` si tienes GPU)

#### 🔹 Opción B: Entrenamiento Rápido (Pocos Datos)
Si tienes poco dataset:
```powershell
python train.py --dataset cows --model yolov8n.pt --epochs 50 --batch 8 --imgsz 416 --device cpu
```

#### 🔹 Opción C: Entrenamiento Profesional (GPU)
Si tienes GPU NVIDIA:
```powershell
python train.py --dataset cows --model yolov8l.pt --epochs 150 --batch 32 --imgsz 1024 --device cuda
```

---

## ⏱️ Tiempos Esperados

| Modelo  | Dataset | CPU      | GPU      |
|---------|---------|----------|----------|
| nano    | Pequeño | 30 min   | 5 min    |
| small   | Pequeño | 1 hora   | 10 min   |
| medium  | Grande  | 3 horas  | 20 min   |
| large   | Grande  | 6 horas  | 40 min   |

---

## ✅ PASO 4: Monitorear Entrenamiento

Durante el entrenamiento, verás salida como:

```
Epoch 1/100: 100%|█████| 50/50 [00:45<00:00, 0.90s/it]
            Class   Images  Instances      Box(P          R      mAP50  mAP50-95)
              all       100         150      0.95      0.92      0.93      0.87
```

**Métricas importantes:**
- `mAP50` > 0.85 = bueno
- `mAP50-95` > 0.80 = muy bueno
- Si la precisión baja después de N epochs → detención automática (early stopping)

---

## 📁 PASO 5: Encontrar el Modelo Entrenado

Al terminar, el modelo estará en:

```
data/runs/detect/train/weights/best.pt
```

**Primera vez:** La carpeta se llama `train`
**Segunda vez:** Se llama `train2`, `train3`, etc.

Para ver todas las carpetas:
```powershell
Get-ChildItem "data/runs/detect/" -Directory | Sort-Object CreationTime -Descending
```

---

## 🔄 PASO 6: Reemplazar el Modelo Anterior

### Opción A: Copiar a carpeta de modelos entrenados (RECOMENDADO)

```powershell
$source = "data\runs\detect\train\weights\best.pt"
$dest = "data\trained_models\yolov8_cows_$(Get-Date -Format 'yyyyMMdd_HHmmss').pt"

Copy-Item -Path $source -Destination $dest

Write-Host "✓ Modelo guardado en: $dest"
```

### Opción B: Actualizar config.py con nueva ruta

Edita `data/src/config.py`:

```python
# Anterior:
MODEL_PATH = './runs/detect/train/weights/best.pt'

# Nuevo:
MODEL_PATH = './trained_models/yolov8_cows_20260520_143025.pt'
```

**Usa la fecha/hora del archivo real.**

---

## 🧪 PASO 7: Probar el Nuevo Modelo

### 7.1 Validación Rápida (Métricas)

```powershell
cd data\src

python -c "
from ultralytics import YOLO

# Cargar modelo entrenado
model = YOLO('../trained_models/yolov8_cows_latest.pt')

# Validar en conjunto de validación
metrics = model.val(data='../datasets/data.yaml', imgsz=640)

print(f'mAP50: {metrics.results_dict[\"metrics/mAP50(B)\"]}')
print(f'Precisión: {metrics.results_dict[\"metrics/precision(B)\"]}')
print(f'Recall: {metrics.results_dict[\"metrics/recall(B)\"]}')
"
```

### 7.2 Prueba con Video

```powershell
cd data\src

python main.py --video ../videos/test_video.mp4 --output ../outputs/resultado.mp4
```

**Verificar:**
- ¿Se detectan las vacas?
- ¿Los IDs son estables?
- ¿El conteo es correcto?
- ¿El HUD muestra bien?

---

## 🎯 PASO 8: Optimizaciones Posteriores

### Si la precisión es baja:
1. Agregar más imágenes de entrenamiento
2. Aumentar `--epochs` a 150-200
3. Cambiar modelo a uno más grande (`yolov8l.pt`)
4. Aumentar `--imgsz` a 1024

### Si es lento:
1. Reducir `--imgsz` a 416
2. Usar modelo más pequeño (`yolov8n.pt`)
3. Aumentar `--batch` (si memoria lo permite)

### Si hay falsos positivos (detecta cosas que no son vacas):
1. Aumentar `CONFIDENCE_THRESHOLD` en `config.py` (ej: 0.50)
2. Reentrenar con mejor etiquetado de datos

---

## 📝 Resumen de Pasos Rápido

```powershell
# 1. Activar venv
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& .\venv\Scripts\Activate.ps1)

# 2. Entrenar
cd data\src
python train.py --dataset cows --model yolov8m.pt --epochs 100 --batch 16 --imgsz 640

# 3. Esperar 2-4 horas...

# 4. Copiar modelo
Copy-Item "data\runs\detect\train\weights\best.pt" "data\trained_models\yolov8_cows_nuevo.pt"

# 5. Actualizar config.py con nueva ruta

# 6. Probar con video
python main.py --video ../videos/test.mp4 --output ../outputs/resultado.mp4
```

---

## ⚠️ Troubleshooting

### "CUDA out of memory"
→ Reducir `--batch` o usar `--device cpu`

### "File not found: data.yaml"
→ Verifica que `data/datasets/data.yaml` existe

### "No module named 'ultralytics'"
→ Instalar dependencias: `pip install ultralytics opencv-python torch`

### Entrenamiento muy lento
→ Usar GPU: `--device cuda`
→ O reducir `--imgsz` y `--batch`

### El modelo no mejora
→ Aumentar epochs
→ Agregar más datos
→ Revisar anotaciones (¿son correctas?)

---

## 📚 Referencias

- [YOLOv8 Docs](https://docs.ultralytics.com/tasks/detect/)
- [Formato YOLO](https://docs.ultralytics.com/datasets/detect/)
- [Data Augmentation](https://docs.ultralytics.com/usage/cfg/#augmentation)

---

**Última actualización:** 19/05/2026
