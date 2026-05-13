"""
verify_and_cleanup.py - Verificar sistema y limpiar archivos innecesarios
Valida que todo esté correcto y elimina yolov8s.pt si no se usa
"""

import os
import sys
from pathlib import Path

def verify_structure():
    """Verifica la estructura del proyecto"""
    print("=" * 70)
    print("🔍 VERIFICANDO ESTRUCTURA DEL PROYECTO")
    print("=" * 70)
    
    base_dir = Path("..").resolve()
    
    # Directorios esperados
    required_dirs = {
        'datasets': base_dir / "datasets",
        'datasets/cows': base_dir / "datasets" / "cows",
        'datasets/cows/images': base_dir / "datasets" / "cows" / "images",
        'datasets/cows/labels': base_dir / "datasets" / "cows" / "labels",
        'models': base_dir / "models",
        'trained_models': base_dir / "trained_models",
        'videos': base_dir / "videos",
        'outputs': base_dir / "outputs",
        'runs': base_dir / "runs",
    }
    
    print("\n📁 Directorios:")
    all_exist = True
    for name, path in required_dirs.items():
        if path.exists():
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} (FALTA)")
            all_exist = False
    
    return all_exist

def check_dataset_files():
    """Verifica archivos del dataset"""
    print("\n" + "=" * 70)
    print("📊 VERIFICANDO DATASET")
    print("=" * 70)
    
    base_dir = Path("..").resolve()
    cows_dir = base_dir / "datasets" / "cows"
    
    dataset_ok = True
    
    # Verificar imágenes (estructura: train/images, valid/images, test/images)
    print("\n🖼️  Imágenes:")
    for split in [('train', 'train'), ('val', 'valid'), ('test', 'test')]:
        display_name, folder_name = split
        img_dir = cows_dir / folder_name / "images"
        if img_dir.exists():
            images = list(img_dir.glob("*"))
            print(f"  {display_name}: {len(images)} imágenes")
        else:
            print(f"  {display_name}: ⚠️  Directorio NO EXISTE")
            dataset_ok = False
    
    # Verificar etiquetas (estructura: train/labels, valid/labels, test/labels)
    print("\n🏷️  Etiquetas (YOLO format):")
    for split in [('train', 'train'), ('val', 'valid'), ('test', 'test')]:
        display_name, folder_name = split
        label_dir = cows_dir / folder_name / "labels"
        if label_dir.exists():
            labels = list(label_dir.glob("*.txt"))
            print(f"  {display_name}: {len(labels)} archivos .txt")
        else:
            print(f"  {display_name}: ⚠️  Directorio NO EXISTE")
            dataset_ok = False
    
    # Verificar data.yaml
    print("\n⚙️  Configuración:")
    yaml_file = base_dir / "datasets" / "data.yaml"
    if yaml_file.exists():
        print(f"  ✓ data.yaml existe ({yaml_file.stat().st_size} bytes)")
        
        # Mostrar contenido
        try:
            import yaml
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)
            print(f"    - Dataset path: {config.get('path', 'NO DEFINIDA')}")
            print(f"    - Train: {config.get('train', 'NO DEFINIDA')}")
            print(f"    - Val: {config.get('val', 'NO DEFINIDA')}")
            print(f"    - Classes: {config.get('nc', 0)}")
        except Exception as e:
            print(f"    ⚠️  Error leyendo YAML: {e}")
    else:
        print(f"  ✗ data.yaml NO EXISTE")
        dataset_ok = False
    
    return dataset_ok

def check_models():
    """Verifica modelos disponibles"""
    print("\n" + "=" * 70)
    print("🤖 VERIFICANDO MODELOS")
    print("=" * 70)
    
    base_dir = Path("..").resolve()
    models_dir = base_dir / "models"
    
    print("\n📦 Modelos en models/:")
    
    yolov8n = models_dir / "yolov8n.pt"
    yolov8s = models_dir / "yolov8s.pt"
    
    n_exists = yolov8n.exists()
    s_exists = yolov8s.exists()
    
    if n_exists:
        size_mb = yolov8n.stat().st_size / (1024*1024)
        print(f"  ✓ yolov8n.pt ({size_mb:.1f} MB) - USAR ESTE")
    else:
        print(f"  ⚠️  yolov8n.pt NO EXISTE (se descargará automáticamente)")
    
    if s_exists:
        size_mb = yolov8s.stat().st_size / (1024*1024)
        print(f"  ⚠️  yolov8s.pt ({size_mb:.1f} MB) - ELIMINAR")
    else:
        print(f"  ✓ yolov8s.pt NO existe")
    
    return n_exists

def check_trained_models():
    """Verifica modelos entrenados"""
    print("\n" + "=" * 70)
    print("🎯 VERIFICANDO MODELOS ENTRENADOS")
    print("=" * 70)
    
    base_dir = Path("..").resolve()
    trained_dir = base_dir / "trained_models"
    
    print("\n📦 Modelos entrenados:")
    if trained_dir.exists():
        models = list(trained_dir.glob("*.pt"))
        if models:
            for model in models:
                size_mb = model.stat().st_size / (1024*1024)
                print(f"  ✓ {model.name} ({size_mb:.1f} MB)")
        else:
            print(f"  (ninguno aún - se generarán después del entrenamiento)")
    else:
        print(f"  (directorio se creará durante entrenamiento)")

def cleanup_yolov8s():
    """Elimina yolov8s.pt si existe"""
    print("\n" + "=" * 70)
    print("🗑️  LIMPIEZA")
    print("=" * 70)
    
    base_dir = Path("..").resolve()
    yolov8s = base_dir / "models" / "yolov8s.pt"
    
    if yolov8s.exists():
        try:
            size_mb = yolov8s.stat().st_size / (1024*1024)
            yolov8s.unlink()
            print(f"\n✓ yolov8s.pt eliminado ({size_mb:.1f} MB liberados)")
            return True
        except Exception as e:
            print(f"\n✗ Error al eliminar yolov8s.pt: {e}")
            return False
    else:
        print(f"\n✓ yolov8s.pt no existe (nada que limpiar)")
        return True

def main():
    """Ejecutar verificación completa"""
    
    print("\n" + "=" * 70)
    print("🚀 VERIFICACIÓN DEL PROYECTO AGROGUARDIAN")
    print("=" * 70)
    
    # Cambiar a directorio src si no estamos allá
    current_dir = Path.cwd()
    if current_dir.name != "src":
        print(f"\n⚠️  No estás en el directorio src")
        print(f"   Ejecuta desde: data/src")
        print(f"   Current dir: {current_dir}")
        return 1
    
    # Ejecutar validaciones
    struct_ok = verify_structure()
    dataset_ok = check_dataset_files()
    models_ok = check_models()
    check_trained_models()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📋 RESUMEN")
    print("=" * 70)
    
    print(f"\n✓ Estructura: {'OK' if struct_ok else 'ERROR'}")
    print(f"{'✓' if dataset_ok else '✗'} Dataset: {'OK' if dataset_ok else 'INCOMPLETO'}")
    print(f"{'✓' if models_ok else '⚠️ '} Modelos: {'LISTO' if models_ok else 'SE DESCARGARÁ'}")
    
    # Preguntar si limpiar
    if Path("../models/yolov8s.pt").exists():
        print("\n" + "=" * 70)
        response = input("¿Eliminar yolov8s.pt? (s/n): ").strip().lower()
        if response in ['s', 'si', 'yes', 'y']:
            cleanup_yolov8s()
        else:
            print("No se eliminó yolov8s.pt")
    
    # Mostrar próximos pasos
    print("\n" + "=" * 70)
    print("✅ PRÓXIMOS PASOS")
    print("=" * 70)
    print("\n1. Descargar dataset desde Roboflow:")
    print("   - Ir a roboflow.com")
    print("   - Crear proyecto 'cattle-detection'")
    print("   - Anotar vacas y exportar en formato YOLO v8")
    print("   - Extraer en: data/datasets/cows/")
    
    print("\n2. Entrenar modelo:")
    print("   python train.py --model yolov8n.pt --epochs 50 --batch 16")
    
    print("\n3. Procesar videos:")
    print("   python main.py --video ../videos/cows.mp4 --output ../outputs/resultado.mp4")
    
    print("\n" + "=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
