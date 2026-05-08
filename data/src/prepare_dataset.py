"""
prepare_dataset.py
Prepara dataset automáticamente a partir de imágenes PNG.

1. Detecta vacas en tus imágenes usando YOLO
2. Genera anotaciones en formato YOLO (.txt)
3. Organiza todo en train/val/test

Uso:
    python prepare_dataset.py --input path/to/images --split 0.7 0.15 0.15
"""

import argparse
import os
import sys
import random
import shutil
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

def detect_and_annotate(image_path, model, confidence=0.35):
    """
    Detecta vacas en una imagen y retorna anotaciones en formato YOLO.
    
    Retorna:
        list: [(x_center, y_center, width, height), ...] normalizados (0-1)
    """
    try:
        # Realiza detección
        results = model.predict(image_path, conf=confidence, verbose=False)
        
        # Lee imagen para obtener dimensiones
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        h, w = img.shape[:2]
        
        annotations = []
        for result in results:
            if result.boxes is None:
                continue
            
            for box in result.boxes:
                # Extrae coordenadas
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                
                # Convierte a formato YOLO (centro normalizado)
                x_center = ((x1 + x2) / 2) / w
                y_center = ((y1 + y2) / 2) / h
                box_width = (x2 - x1) / w
                box_height = (y2 - y1) / h
                
                # Solo guarda si es vaca (clase 16 en COCO)
                if cls == 16:
                    annotations.append((0, x_center, y_center, box_width, box_height))
        
        return annotations
    except Exception as e:
        print(f"⚠️  Error procesando {image_path}: {e}")
        return []

def save_annotations(txt_path, annotations):
    """Guarda anotaciones en formato YOLO."""
    with open(txt_path, 'w') as f:
        for ann in annotations:
            cls, x, y, w, h = ann
            f.write(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Preparar dataset de vacas con anotaciones automáticas"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        default="./temp_images",
        help="Carpeta con tus imágenes PNG"
    )
    parser.add_argument(
        "--split",
        type=float,
        nargs=3,
        default=[0.7, 0.15, 0.15],
        help="Split train/val/test (ej: 0.7 0.15 0.15)"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.35,
        help="Confianza mínima para detectar (0-1)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="../models/yolov8s.pt",
        help="Ruta al modelo YOLO"
    )
    
    args = parser.parse_args()
    
    input_dir = args.input
    dataset_dir = "../datasets/cows"
    
    # Validar
    if not os.path.exists(input_dir):
        print(f"❌ No encontrado: {input_dir}")
        print("   Crea una carpeta con tus imágenes PNG y ejecuta de nuevo:")
        print(f"   python prepare_dataset.py --input /ruta/a/tus/imagenes")
        sys.exit(1)
    
    # Busca imágenes
    image_files = list(Path(input_dir).glob("*.png")) + \
                  list(Path(input_dir).glob("*.jpg")) + \
                  list(Path(input_dir).glob("*.jpeg"))
    
    if not image_files:
        print(f"❌ No hay imágenes en: {input_dir}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🖼️  PREPARANDO DATASET")
    print("="*60)
    print(f"📁 Imágenes encontradas: {len(image_files)}")
    print(f"🤖 Modelo: {args.model}")
    print(f"🎯 Confianza: {args.conf}")
    print(f"📊 Split: train={args.split[0]:.0%} val={args.split[1]:.0%} test={args.split[2]:.0%}")
    print("="*60 + "\n")
    
    # Carga modelo
    print("📥 Cargando modelo YOLO...")
    try:
        model = YOLO(args.model)
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        sys.exit(1)
    
    # Detecta y anota
    print(f"🔍 Detectando vacas en {len(image_files)} imágenes...\n")
    
    image_annotations = []
    for i, img_path in enumerate(image_files, 1):
        print(f"   [{i}/{len(image_files)}] {img_path.name}...", end=" ")
        
        annotations = detect_and_annotate(str(img_path), model, args.conf)
        
        if annotations:
            print(f"✓ {len(annotations)} vaca(s)")
            image_annotations.append((img_path, annotations))
        else:
            print("✗ Sin vacas (descartada)")
    
    if not image_annotations:
        print("\n❌ No se encontraron vacas en ninguna imagen")
        sys.exit(1)
    
    # Divide en train/val/test
    print(f"\n📊 Dividiendo en train/val/test...")
    random.shuffle(image_annotations)
    
    n = len(image_annotations)
    n_train = int(n * args.split[0])
    n_val = int(n * args.split[1])
    
    train_data = image_annotations[:n_train]
    val_data = image_annotations[n_train:n_train + n_val]
    test_data = image_annotations[n_train + n_val:]
    
    print(f"   Train: {len(train_data)} ({len(train_data)/n*100:.0f}%)")
    print(f"   Val:   {len(val_data)} ({len(val_data)/n*100:.0f}%)")
    print(f"   Test:  {len(test_data)} ({len(test_data)/n*100:.0f}%)")
    
    # Copia archivos
    print(f"\n💾 Guardando dataset en {dataset_dir}...\n")
    
    splits = [
        ("train", train_data),
        ("val", val_data),
        ("test", test_data)
    ]
    
    for split_name, split_data in splits:
        print(f"   {split_name.upper()}:")
        
        for i, (img_path, annotations) in enumerate(split_data, 1):
            # Copia imagen
            dest_img = os.path.join(
                dataset_dir, "images", split_name, img_path.name
            )
            shutil.copy2(img_path, dest_img)
            
            # Crea anotación
            txt_name = img_path.stem + ".txt"
            dest_txt = os.path.join(
                dataset_dir, "labels", split_name, txt_name
            )
            save_annotations(dest_txt, annotations)
            
            if i % 10 == 0 or i == len(split_data):
                print(f"      {i}/{len(split_data)} imágenes procesadas")
    
    print("\n" + "="*60)
    print("✅ DATASET LISTO")
    print("="*60)
    print(f"📁 {len(image_annotations)} imágenes organizadas")
    print(f"📊 Estructura:")
    print(f"   {dataset_dir}/")
    print(f"   ├── images/train/  ({len(train_data)} imágenes)")
    print(f"   ├── images/val/    ({len(val_data)} imágenes)")
    print(f"   ├── labels/train/  ({len(train_data)} anotaciones)")
    print(f"   └── labels/val/    ({len(val_data)} anotaciones)")
    print("\n🚀 Ahora entrena:")
    print("   python train.py --epochs 50 --augment")
    print("="*60)

if __name__ == "__main__":
    main()
