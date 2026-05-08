# 🐄 AgroGuardian - Sistema de Detección y Conteo de Ganado Bovino

Un sistema robusto y modular para detectar, rastrear y contar vacas en video usando **YOLOv8** y **DeepSORT**.

## 📋 Características

✅ **Detección precisa** de vacas cercanas y en movimiento usando YOLOv8  
✅ **Tracking estable** con DeepSORT para mantener IDs consistentes  
✅ **Conteo confiable** solo de vacas estacionarias  
✅ **Configuración centralizada** para fácil ajuste de parámetros  
✅ **Modular y mantenible** con separación clara de responsabilidades  
✅ **Visualización en tiempo real** con información detallada  
✅ **Manejo robusto de errores** en todas las capas  

---

## 🏗️ Arquitectura del Sistema

```
main.py
    ├── detector.py       (Detección YOLO)
    ├── tracker.py        (Tracking DeepSORT)
    ├── counter.py        (Conteo de vacas)
    ├── visualizer.py     (Anotación de frames)
    ├── config.py         (Configuración centralizada)
    └── utils.py          (Funciones auxiliares)
```

### Flujo de Datos

```
Video Input
    ↓
[detector.py] → Detecciones raw (bbox, conf, clase)
    ↓
[tracker.py] → Tracks confirmados (bbox, track_id)
    ↓
[counter.py] → Conteo de vacas estacionarias
    ↓
[visualizer.py] → Anotación visual
    ↓
Video Output
```

---

## 📦 Módulos

### 1. **detector.py** - Detección YOLO
- Carga el modelo YOLOv8
- Ejecuta inferencia sobre cada frame
- Filtra por confianza y clase
- Filtra detecciones pequeñas (ruido)
- Retorna: `[(x1, y1, x2, y2, conf, class_id), ...]`

### 2. **tracker.py** - Tracking DeepSORT
- Mantiene identidades persistentes de vacas
- Asocia detecciones entre frames
- Solo retorna tracks confirmados
- Retorna: `[{bbox, confidence, class_id, track_id}, ...]`

### 3. **counter.py** - Conteo Inteligente
- Rastrea posición de cada vaca en el tiempo
- Solo cuenta vacas que están estacionarias por N frames
- Previene duplicados y falsas cuentas
- Retorna: `{total_cows, stationary_cows, active_cows, people}`

### 4. **visualizer.py** - Visualización
- Dibuja bounding boxes de cada track
- Muestra label con clase e ID
- Muestra contadores en la esquina superior izquierda
- Mejor legibilidad con fondos negros

### 5. **config.py** - Configuración
- Parámetros YOLO (confidence, iou, imgsz, device, classes)
- Parámetros del tracker (max_age, n_init)
- Parámetros de conteo (move_thresh, stationary_frames)
- Comentarios detallados de cada parámetro

### 6. **utils.py** - Utilidades
- Parsing de argumentos de línea de comandos
- Rutas de video y salida

---

## 🚀 Uso

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar el sistema

```bash
cd agroguardian-yolo-test/data/src
python main.py --video ../videos/input.mp4 --output ../outputs/output.mp4
```

### Argumentos

- `--video`: Ruta al video de entrada (default: `../videos/input.mp4`)
- `--output`: Ruta del video de salida (default: `../outputs/output.mp4`)

### Controles durante ejecución

- **ESC**: Detener procesamiento
- **Ctrl+C**: Interrumpir (limpieza automática)

---

## ⚙️ Configuración y Tuning

Todos los parámetros se modifican en **`config.py`**.

### Para mejorar DETECCIÓN de vacas cercanas

```python
CONFIDENCE_THRESHOLD = 0.15      # Reducir para detectar más (más falsos positivos)
MODEL_PATH = 'yolov8s.pt'        # Usar modelo más grande (s, m, l)
IMGSZ = 1024                     # Aumentar tamaño de imagen (más preciso)
DEVICE = 'cuda'                  # Usar GPU si está disponible
```

### Para mejorar CONTEO confiable (sin duplicados)

```python
STATIONARY_FRAMES = 20           # Aumentar para ser más estricto
MOVE_THRESH = 3.0                # Reducir para estacionariedad más estricta
N_INIT_TRACKER = 5               # Aumentar frames para confirmar track
```

### Para mejorar PERFORMANCE

```python
IMGSZ = 416                      # Reducir tamaño de imagen
MODEL_PATH = 'yolov8n.pt'        # Usar modelo nano
DEVICE = 'cuda'                  # Usar GPU
FRAME_SKIP = 2                   # Procesar cada 2do frame
```

---

## 🐛 Troubleshooting

### Problema: "Detecta algunas vacas pero no todas"

**Causas posibles:**
- Confianza muy alta → Reducir `CONFIDENCE_THRESHOLD`
- Modelo muy pequeño → Cambiar a `yolov8s.pt` o mayor
- Imagen muy pequeña → Aumentar `IMGSZ` a 1024

**Solución recomendada:**
```python
CONFIDENCE_THRESHOLD = 0.2       # Paso 1: reducir confianza
MODEL_PATH = 'yolov8s.pt'        # Paso 2: modelo más grande
IMGSZ = 1024                     # Paso 3: imagen más grande
```

### Problema: "Cuenta incorrecta o duplicados"

**Causas posibles:**
- Rastreador inestable → Aumentar `N_INIT_TRACKER`
- Conteo demasiado rápido → Aumentar `STATIONARY_FRAMES`
- Umbral de movimiento incorrecto → Ajustar `MOVE_THRESH`

**Solución recomendada:**
```python
N_INIT_TRACKER = 5               # Requerir 5 frames para confirmar
STATIONARY_FRAMES = 20           # Requerir 20 frames estacionarios
MOVE_THRESH = 3.0                # Más estricto
```

### Problema: "Sistema muy lento"

**Causas posibles:**
- Imagen muy grande → Reducir `IMGSZ`
- Modelo muy grande → Cambiar a `yolov8n.pt`
- Usando CPU → Usar `DEVICE = 'cuda'` si está disponible

**Solución recomendada:**
```python
IMGSZ = 416                      # Reducir tamaño
MODEL_PATH = 'yolov8n.pt'        # Modelo nano
DEVICE = 'cuda'                  # GPU si está disponible
```

### Problema: "CUDA out of memory"

**Soluciones:**
```python
IMGSZ = 416                      # Reducir tamaño de imagen
DEVICE = 'cpu'                   # Usar CPU
BATCH_SIZE = 1                   # Si existe, reducir batch
```

---

## 📊 Interpretación de Salida

La visualización muestra:

```
┌─────────────────────────────────────────────┐
│ VACAS TOTALES: 5                             │
│ Activas: 3 | Fijas: 5 | Personas: 1        │
└─────────────────────────────────────────────┘

[Vaca detectada]
  ┌─────────────┐
  │ Vaca #1     │
  │ (bbox verde)│
  └─────────────┘
```

- **VACAS TOTALES**: Suma de todas las vacas que fueron estacionarias
- **Activas**: Vacas visibles actualmente (moviéndose o no)
- **Fijas**: Vacas que fueron contadas (estacionarias por N frames)
- **Personas**: Personas detectadas en el video

---

## 🔍 Detalles de Implementación

### Detección (detector.py)

1. Carga modelo YOLOv8 en GPU/CPU
2. Ejecuta inferencia con parámetros configurados
3. Filtra por:
   - Confianza mínima (`CONFIDENCE_THRESHOLD`)
   - Clase (`CLASSES`)
   - Área mínima de bbox (evita ruido)

### Tracking (tracker.py)

1. DeepSORT asocia detecciones entre frames
2. Solo retorna tracks "confirmados" (visto N frames)
3. Descarta tracks muy nuevos o fantasmas
4. Mantiene ID consistente para cada vaca

### Conteo (counter.py)

1. Rastrea posición del centro de cada vaca
2. Calcula distancia total recorrida en últimos N frames
3. Si distancia < `MOVE_THRESH` → vaca estacionaria
4. Cuenta vaca una sola vez (previene duplicados)

### Visualización (visualizer.py)

1. Dibuja bbox con color según clase
2. Etiqueta con "Vaca #ID"
3. Dibuja contadores en esquina superior
4. Fondos negros para mejor legibilidad

---

## 📈 Métricas de Performance

- **FPS**: Frames procesados por segundo
- **Precisión**: % de detecciones correctas
- **Recall**: % de objetos reales detectados
- **Consistencia**: Estabilidad de IDs entre frames

**Objetivos recomendados:**
- FPS: 10-30 fps (suficiente para surveillance)
- Precisión: >90%
- Recall: >85%
- Consistencia: >95% (IDs estables)

---

## 🛠️ Mejoras Futuras

- [ ] Agregar ByteTrack como alternativa a DeepSORT
- [ ] Implementar Line Crossing Detection (conteo por línea)
- [ ] Agregar face recognition para identificar ganado específico
- [ ] Crear dashboard web para monitoreo
- [ ] Exportar estadísticas a JSON
- [ ] Soportar múltiples cámaras
- [ ] Agregar alertas en tiempo real

---

## 📝 Estructura de Archivos

```
agroguardian-yolo-test/
├── README.md              (Este archivo)
├── requirements.txt       (Dependencias)
├── data/
│   ├── models/
│   │   └── yolov8n.pt     (Modelo YOLO)
│   ├── videos/
│   │   └── input.mp4      (Video de entrada)
│   └── src/
│       ├── config.py      (Configuración)
│       ├── detector.py    (Detección)
│       ├── tracker.py     (Tracking)
│       ├── counter.py     (Conteo)
│       ├── visualizer.py  (Visualización)
│       ├── utils.py       (Utilidades)
│       └── main.py        (Punto de entrada)
└── outputs/
    └── output.mp4         (Video procesado)
```

---

## 📞 Soporte y Contacto

Para reportar bugs, sugerencias o mejoras:
1. Verifica el archivo `config.py` para ajustar parámetros
2. Consulta la sección "Troubleshooting"
3. Revisa los comentarios en cada módulo

---

## 📄 Licencia

Este proyecto es de código abierto para propósitos educativos y de investigación.

---

**Última actualización**: Abril 2026  
**Versión**: 2.0 (Refactorizado y optimizado)
