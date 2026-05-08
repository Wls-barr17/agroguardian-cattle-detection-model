"""
train.py
Script para entrenar un modelo YOLOv8 personalizado para detección de vacas.

Uso:
    python train.py --dataset cows --epochs 50 --batch 16

Requisitos:
    - Dataset en: ../datasets/cows/images/{train,val,test}
    - Labels en formato YOLO: ../datasets/cows/labels/{train,val,test}
    - data.yaml configurado en: ../datasets/data.yaml
"""

import argparse
import os
import sys
from pathlib import Path
from ultralytics import YOLO
import torch
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description="Entrenar modelo YOLOv8 para detección de vacas"
    )
    
    # Argumentos de configuración
    parser.add_argument(
        "--dataset",
        type=str,
        default="cows",
        help="Nombre del dataset en ../datasets/"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        choices=["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"],
        help="Modelo base para transfer learning"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Número de epochs de entrenamiento (20-100 recomendado)"
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Tamaño de batch (8-64 recomendado, menor si GPU limitada)"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Tamaño de imagen (416, 640, 1024)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda", "0", "1"],
        help="Dispositivo (cpu o GPU ID)"
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=20,
        help="Early stopping patience (detiene si no mejora en N epochs)"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.35,
        help="Confianza mínima para validación"
    )
    parser.add_argument(
        "--augment",
        action="store_true",
        help="Usar augmentación agresiva (rotación, flip, etc.)"
    )
    
    args = parser.parse_args()
    
    # Verifica dispositivo
    device = args.device
    if device == "cuda" and not torch.cuda.is_available():
        print("⚠️  GPU no disponible, usando CPU")
        device = "cpu"
    else:
        if device == "cuda":
            print(f"✅ GPU disponible: {torch.cuda.get_device_name(0)}")
        else:
            print("ℹ️  Usando CPU (entrenamiento será lento)")
    
    # Rutas
    dataset_path = f"../datasets/{args.dataset}"
    data_yaml = "../datasets/data.yaml"
    model_path = f"../models/{args.model}"
    runs_dir = "../runs"
    trained_models_dir = "../trained_models"
    
    # Validación: verifica que el modelo exista
    if not os.path.exists(model_path):
        print(f"⚠️  Modelo no encontrado: {model_path}")
        print(f"   Disponibles en ../models/:")
        import glob
        available = glob.glob("../models/*.pt")
        for m in available:
            print(f"     - {os.path.basename(m)}")
        print(f"\n   Descargando {args.model} (primera vez)...")
        # YOLO lo descargará automáticamente
    
    # Validación
    if not os.path.exists(data_yaml):
        print(f"❌ No encontrado: {data_yaml}")
        print("   Crea data.yaml con la configuración del dataset")
        sys.exit(1)
    
    if not os.path.exists(dataset_path):
        print(f"❌ No encontrado dataset: {dataset_path}")
        print("   Estructura esperada:")
        print(f"   {dataset_path}/")
        print("   ├── images/")
        print("   │   ├── train/")
        print("   │   ├── val/")
        print("   │   └── test/")
        print("   └── labels/")
        print("       ├── train/")
        print("       ├── val/")
        print("       └── test/")
        sys.exit(1)
    
    # Crea directorios si no existen
    os.makedirs(runs_dir, exist_ok=True)
    os.makedirs(trained_models_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 ENTRENAMIENTO YOLOV8 - DETECCIÓN DE VACAS")
    print("="*60)
    print(f"📊 Dataset: {dataset_path}")
    print(f"🤖 Modelo: {args.model}")
    print(f"📈 Epochs: {args.epochs}")
    print(f"📦 Batch: {args.batch}")
    print(f"🖥️  Dispositivo: {device}")
    print(f"🎯 Tamaño imagen: {args.imgsz}x{args.imgsz}")
    print("="*60 + "\n")
    
    try:
        # Carga modelo base
        print("📥 Cargando modelo base...")
        model = YOLO(model_path)
        
        # Entrena modelo
        print("⏳ Entrenando... (esto puede tomar horas)")
        results = model.train(
            data=data_yaml,
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
            device=device,
            patience=args.patience,
            conf=args.conf,
            
            # Augmentación
            hsv_h=0.015 if args.augment else 0,
            hsv_s=0.7 if args.augment else 0,
            hsv_v=0.4 if args.augment else 0,
            degrees=10 if args.augment else 0,
            translate=0.1 if args.augment else 0,
            scale=0.5 if args.augment else 0,
            flipud=0.5 if args.augment else 0,
            fliplr=0.5 if args.augment else 0,
            
            # Optimización
            optimizer="SGD",
            lr0=0.001,
            lrf=0.01,
            
            # Validación
            val=True,
            save=True,
            save_period=5,
            
            # Logging
            verbose=True,
            project=runs_dir,
            name=f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        )
        
        # Guarda modelo entrenado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_model_path = f"{trained_models_dir}/yolov8_cows_{timestamp}.pt"
        model.save(final_model_path)
        
        print("\n" + "="*60)
        print("✅ ENTRENAMIENTO COMPLETADO")
        print("="*60)
        print(f"💾 Modelo guardado: {final_model_path}")
        print(f"📊 Resultados en: {runs_dir}")
        print("="*60)
        
        # Valida modelo
        print("\n🔍 Validando modelo...")
        metrics = model.val()
        print(f"   mAP50: {metrics.box.map50:.3f}")
        print(f"   mAP50-95: {metrics.box.map:.3f}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Entrenamiento interrumpido por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante entrenamiento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
