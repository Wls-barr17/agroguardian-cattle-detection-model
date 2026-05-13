"""
main.py
Punto de entrada del sistema de detección y conteo de ganado bovino.
Orquesta detector, tracker, counter y visualizer para procesar video.
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
    Función principal que procesa video y genera salida anotada.
    Pipeline: Lectura -> Detección -> Tracking -> Conteo -> Visualización -> Escritura
    """
    args = parse_args()
    video_path = os.path.abspath(args.video)
    output_path = os.path.abspath(args.output)

    # Valida que el video existe
    if not os.path.exists(video_path):
        print(f"❌ Error: Video no encontrado en {video_path}")
        sys.exit(1)

    # Intenta abrir el video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: No se pudo abrir el video {video_path}")
        sys.exit(1)

    # Extrae propiedades del video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps is None:
        fps = 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"📹 Video: {os.path.basename(video_path)}")
    print(f"   Resolución: {width}x{height}")
    print(f"   FPS: {fps:.1f}")
    print(f"   Frames totales: {total_frames}")

    # Crea writer para video de salida
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not writer.isOpened():
        print(f"❌ Error: No se pudo crear el video de salida {output_path}")
        cap.release()
        sys.exit(1)

    # Inicializa componentes del sistema
    try:
        print("\n🔧 Inicializando componentes...")
        detector = Detector()
        print("   ✓ Detector YOLO cargado")
        
        tracker = Tracker()
        print("   ✓ Tracker DeepSORT inicializado")
        
        counter = Counter(
            move_thresh=args.move_thresh,
            stationary_frames=args.stationary_frames
        )
        print("   ✓ Counter inicializado")
        
        visualizer = Visualizer()
        print("   ✓ Visualizer listo")
        
    except Exception as e:
        print(f"❌ Error inicializando componentes: {e}")
        cap.release()
        writer.release()
        sys.exit(1)

    # Pipeline de procesamiento
    print("\n▶ Procesando video...")
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Paso 1: Detección
            detections = detector.predict(frame)
            if frame_count % 30 == 0:
                print(f"Frame {frame_count} | detections={len(detections)}")

            # Paso 2: Tracking
            tracks = tracker.update(detections, frame)

            # Paso 3: Conteo
            counts = counter.update(tracks)

            # Paso 4: Visualización
            vis_frame = visualizer.draw(frame, tracks, counts)

            # Mostrar en pantalla
            cv2.imshow("AgroGuardian - Detección de Ganado", vis_frame)
            
            # Escribir frame procesado al video de salida
            writer.write(vis_frame)

            # Manejo de entrada
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("\n⏹ Procesamiento detenido por usuario (ESC)")
                break

            # Información de progreso cada 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps_actual = frame_count / elapsed if elapsed > 0 else 0
                print(f"   Frame {frame_count}/{total_frames} ({100*frame_count/total_frames:.1f}%) | "
                      f"FPS: {fps_actual:.1f} | Vacas totales: {counts['total_cows']}")

    except KeyboardInterrupt:
        print("\n⏹ Procesamiento interrumpido")
    except Exception as e:
        print(f"\n❌ Error durante procesamiento: {e}")
    finally:
        # Limpieza
        cap.release()
        writer.release()
        cv2.destroyAllWindows()

    # Resumen final
    elapsed_total = time.time() - start_time
    fps_promedio = frame_count / elapsed_total if elapsed_total > 0 else 0
    
    print(f"\n✅ Procesamiento completado")
    print(f"   Frames procesados: {frame_count}")
    print(f"   Tiempo total: {elapsed_total:.2f}s")
    print(f"   FPS promedio: {fps_promedio:.2f}")
    print(f"   Vacas detectadas: {counts['total_cows']}")
    print(f"   Archivo de salida: {output_path}")


if __name__ == "__main__":
    main()
