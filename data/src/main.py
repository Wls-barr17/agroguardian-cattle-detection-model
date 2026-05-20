"""
main.py - Punto de entrada del sistema AgroGuardian

Orquesta el pipeline de:
1. Lectura de video
2. Detección (YOLO)
3. Tracking (DeepSORT)
4. Conteo (estacionariedad)
5. Visualización (HUD)
6. Guardado de video procesado

Flujo principal sin modificaciones,
pero mejorado con mejor tracking de estadísticas.
"""

import cv2
import os
import sys
import time
from detector import Detector
from tracker import Tracker
from counter import Counter
from visualizer import Visualizer
from utils import parse_args


def main():
    """
    Procesa video completo con detección, tracking y conteo de vacas.
    
    Pipeline:
    1. Abrir video de entrada
    2. Para cada frame:
       - Detectar objetos (YOLO)
       - Rastrear IDs (DeepSORT)
       - Contar vacas estacionarias
       - Visualizar con HUD
       - Guardar frame procesado
    3. Generar video de salida
    """
    args = parse_args()
    video_path = os.path.abspath(args.video)
    output_path = os.path.abspath(args.output)

    # Validaciones previas
    if not os.path.exists(video_path):
        print(f"❌ Error: Video no encontrado en {video_path}")
        sys.exit(1)

    # Abrir video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: No se pudo abrir el video {video_path}")
        sys.exit(1)

    # Obtener propiedades del video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps is None:
        fps = 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Ventana escalable para adaptarse a diferentes resoluciones
    window_name = "AgroGuardian - Sistema de Detección"
    # Asegurar que no haya ventanas residuales
    cv2.destroyAllWindows()
    # Crear una única ventana escalable (sin KEEPRATIO evita comportamientos inconsistentes en Windows)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    try:
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
    except Exception:
        screen_width, screen_height = 1920, 1080

    scale = min(1.0, screen_width / (width + 40), screen_height / (height + 120))
    resized_width = max(320, int(width * scale))
    resized_height = max(240, int(height * scale))
    cv2.resizeWindow(window_name, resized_width, resized_height)
    # Coordenadas objetivo para centrar la ventana
    center_x = max(0, (screen_width - resized_width) // 2)
    center_y = max(0, (screen_height - resized_height) // 2)
    # Mover la ventana al centro de la pantalla sin mostrar un frame previo
    cv2.moveWindow(window_name, center_x, center_y)

    print(f"📹 Video: {os.path.basename(video_path)}")
    print(f"   Resolución: {width}x{height}")
    print(f"   FPS: {fps:.1f}")
    print(f"   Frames totales: {total_frames}")

    # Preparar writer para salida
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not writer.isOpened():
        print(f"❌ Error: No se pudo crear el video de salida {output_path}")
        cap.release()
        sys.exit(1)

    # Inicializar componentes del sistema
    try:
        print("\n🔧 Inicializando componentes...")
        detector = Detector()
        print("   ✓ Detector YOLO cargado")
        
        tracker = Tracker()
        print("   ✓ Tracker inicializado")
        
        counter = Counter(
            move_thresh=args.move_thresh,
            stationary_frames=args.stationary_frames
        )
        print("   ✓ Counter inicializado")
        
        visualizer = Visualizer()
        print("   ✓ Visualizer HUD listo")
        
    except Exception as e:
        print(f"❌ Error inicializando componentes: {e}")
        cap.release()
        writer.release()
        sys.exit(1)

    # Procesamiento principal
    print("\n▶ Procesando video...\n")
    frame_count = 0
    start_time = time.time()
    fps_actual = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Paso 1: DETECCIÓN con YOLO
            detections = detector.predict(frame)

            # Paso 2: TRACKING con DeepSORT
            tracks = tracker.update(detections, frame)

            # Paso 3: CONTEO con estacionariedad
            counts = counter.update(tracks)

            # Paso 4: VISUALIZACIÓN con HUD
            vis_frame = visualizer.draw(frame, tracks, counts, fps_actual, frame_count)

            # Mostrar en pantalla
            display_frame = vis_frame
            if vis_frame.shape[1] != resized_width or vis_frame.shape[0] != resized_height:
                display_frame = cv2.resize(vis_frame, (resized_width, resized_height), interpolation=cv2.INTER_AREA)
            cv2.imshow(window_name, display_frame)
            # Re-centrar periódicamente para evitar desplazamientos de la ventana en Windows
            if frame_count % 30 == 0:
                try:
                    cv2.moveWindow(window_name, center_x, center_y)
                except Exception:
                    pass
            
            # Guardar frame procesado
            writer.write(vis_frame)

            # Control de usuario
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC para salir
                print("\n⏹ Procesamiento detenido por usuario (ESC)")
                break

            # Mostrar progreso cada 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps_actual = frame_count / elapsed if elapsed > 0 else 0
                progress_pct = 100 * frame_count / total_frames
                print(f"   [{progress_pct:5.1f}%] Frame {frame_count:5d}/{total_frames} | "
                      f"FPS: {fps_actual:5.1f} | Vacas: {counts['total_cows']:3d}")

    except KeyboardInterrupt:
        print("\n⏹ Procesamiento interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error durante procesamiento: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpiar recursos
        cap.release()
        writer.release()
        cv2.destroyAllWindows()

    # Resumen final
    elapsed_total = time.time() - start_time
    fps_promedio = frame_count / elapsed_total if elapsed_total > 0 else 0
    
    print(f"\n✅ Procesamiento completado")
    print(f"   Frames procesados: {frame_count}/{total_frames}")
    print(f"   Tiempo total: {elapsed_total:.2f}s")
    print(f"   FPS promedio: {fps_promedio:.2f}")
    print(f"   Vacas contadas: {counts['total_cows']}")
    print(f"   Video guardado: {output_path}")


if __name__ == "__main__":
    main()
