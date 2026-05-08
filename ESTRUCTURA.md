# 📋 ESTRUCTURA DEL PROYECTO

Documento de referencia rápida sobre la organización del proyecto.

## 🗂️ Árbol Completo

```
agroguardian-yolo-test/
│
├── 📄 README.md                    ← START HERE (Inicio rápido)
├── 📘 TRAINING.md                  ← Guía completa de entrenamiento
├── requirements.txt                ← Dependencias
│
├── 📁 data/
│   ├── 🤖 models/
│   │   ├── yolov8n.pt             (modelo pre-entrenado - 50MB)
│   │   └── yolov8s.pt             (descargar si usas train.py)
│   │
│   ├── 📊 datasets/                (PARA ENTRENAMIENTO)
│   │   ├── data.yaml              (configuración de dataset)
│   │   └── cows/
│   │       ├── images/
│   │       │   ├── train/         (aquí pones tus imágenes de entrenamiento)
│   │       │   ├── val/           (validación)
│   │       │   └── test/          (prueba)
│   │       └── labels/            (anotaciones YOLO format)
│   │           ├── train/
│   │           ├── val/
│   │           └── test/
│   │
│   ├── 🎓 trained_models/         (MODELOS PERSONALIZADOS)
│   │   └── yolov8_cows_20250420_143022.pt
│   │
│   ├── 📈 runs/                    (OUTPUTS DE ENTRENAMIENTO)
│   │   └── train_20250420_143022/
│   │       ├── weights/
│   │       │   ├── best.pt
│   │       │   └── last.pt
│   │       ├── results.csv
│   │       └── results.png
│   │
│   ├── 🎬 videos/                 (ENTRADA)
│   │   └── cows.mp4
│   │
│   ├── 📺 outputs/                (SALIDA)
│   │   └── resultado_cow.mp4
│   │
│   └── 🐍 src/                    (CÓDIGO FUENTE)
│       ├── main.py                (ejecuta: python main.py --video ...)
│       ├── train.py               (entrenar: python train.py --epochs 50) ⭐
│       ├── detector.py            (YOLOv8)
│       ├── tracker.py             (DeepSORT)
│       ├── counter.py             (contador)
│       ├── visualizer.py          (visualización)
│       ├── utils.py               (utilidades)
│       └── config.py              (configuración centralizada)
```

## 🚀 Uso Rápido

### 1️⃣ Procesar Video (sin entrenar)
```bash
cd data/src
python main.py --video ../videos/cows.mp4 --output ../outputs/resultado.mp4
```

### 2️⃣ Entrenar Modelo Personalizado
Ver **TRAINING.md** para instrucciones detalladas.

```bash
cd data/src
python train.py --dataset cows --epochs 50 --batch 16 --augment
```

## 📊 Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `config.py` | Todos los parámetros ajustables (confianza, thresholds, etc) |
| `train.py` | Entrenar modelos personalizados |
| `main.py` | Script principal de ejecución |
| `data.yaml` | Configuración del dataset |


