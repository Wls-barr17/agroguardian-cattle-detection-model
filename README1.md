# README - AgroGuardian YOLO Cattle Detection System

Sistema profesional de detección y conteo de vacas usando YOLOv8 + DeepSORT.

## 📁 Estructura del Proyecto

```
agroguardian-yolo-test/
├── README.md                 # Este archivo
├── TRAINING.md              # Guía completa de entrenamiento
├── requirements.txt          # Dependencias Python
│
├── data/
│   ├── models/              # Modelos YOLOv8 base
│   │   └── yolov8n.pt      # Modelo Nano (pre-entrenado)
│   │
│   ├── datasets/            # Dataset de entrenamiento
│   │   ├── data.yaml        # Config del dataset
│   │   └── cows/
│   │       ├── images/
│   │       │   ├── train/   # 70% imágenes de entrenamiento
│   │       │   ├── val/     # 15% imágenes de validación
│   │       │   └── test/    # 15% imágenes de prueba
│   │       └── labels/      # Anotaciones YOLO format
│   │           ├── train/
│   │           ├── val/
│   │           └── test/
│   │
│   ├── trained_models/      # Modelos personalizados entrenados
│   │   └── yolov8_cows_YYYYMMDD_HHMMSS.pt
│   │
│   ├── runs/                # Outputs de entrenamiento
│   │   └── train_YYYYMMDD_HHMMSS/
│   │       ├── weights/     # best.pt, last.pt
│   │       ├── results.csv  # Métricas
│   │       └── *.png        # Gráficos
│   │
│   ├── videos/              # Videos para procesar
│   │   └── cows.mp4
│   │
│   ├── outputs/             # Videos procesados
│   │   └── resultado_cow.mp4
│   │
│   └── src/                 # Código fuente
│       ├── main.py          # Script principal
│       ├── train.py         # Script de entrenamiento ⭐
│       ├── detector.py      # Detector YOLO
│       ├── tracker.py       # Tracker DeepSORT
│       ├── counter.py       # Contador de vacas
│       ├── visualizer.py    # Visualización
│       ├── utils.py         # Utilidades
│       └── config.py        # Configuración centralizada
```

## 🚀 Inicio Rápido

### 1. Instalación

```bash
cd agroguardian-yolo-test
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ejecución Básica (sin entrenar)

```bash
cd data/src
python main.py --video ../videos/cows.mp4 --output ../outputs/resultado.mp4
```

### 3. Entrenar Modelo Personalizado ⭐

Ver [TRAINING.md](TRAINING.md) para guía completa.

## 📊 Características

- **Detección**: YOLOv8 para identificación de vacas
- **Tracking**: DeepSORT para IDs persistentes
- **Conteo**: Solo cuenta vacas estacionarias (evita duplicados)
- **Visualización**: 
  - 🟢 Verde = Vacas contadas (quietas)
  - 🟡 Amarillo = Vacas en movimiento (no contadas)
  - 🔴 Rojo = Personas
- **Configuración**: Centralizada en `config.py`

## ⚙️ Configuración

Editar `data/src/config.py`:

```python
CONFIDENCE_THRESHOLD = 0.35  # Sensibilidad detección
MOVE_THRESH = 3.0            # Umbral movimiento (px)
STATIONARY_FRAMES = 10       # Frames para contar como quieta
MODEL_PATH = 'yolov8s.pt'    # Modelo a usar
DEVICE = 'cpu'               # O 'cuda' si tiene GPU
```

## 📖 Documentación Detallada

- **TRAINING.md** - Cómo entrenar modelo personalizado con tus datos
- **config.py** - Todas las opciones configurables

## 🎯 Próximas Mejoras

- [ ] Entrenar con dataset personalizado de vacas
- [ ] ByteTrack para mejor persistencia
- [ ] Detección de línea de conteo
- [ ] Export a JSON con resultados

## 📞 Support

Revisa los comentarios en el código (totalmente documentado) o consulta `TRAINING.md`.
