"""
test_system.py
Script de validación del sistema AgroGuardian.
Verifica que todos los componentes estén correctamente instalados y configurados.
"""

import sys
import os

def test_imports():
    """Verifica que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    packages = {
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'ultralytics': 'YOLO (ultralytics)',
        'deep_sort_realtime': 'DeepSORT',
    }
    
    missing = []
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} NO INSTALADO")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Faltan dependencias: {', '.join(missing)}")
        print("Instala con: pip install -r requirements.txt")
        return False
    
    print("✓ Todas las dependencias instaladas\n")
    return True

def test_config():
    """Verifica que config.py sea válido"""
    print("🔧 Verificando configuración...")
    
    try:
        from config import (
            CONFIDENCE_THRESHOLD, IOU_THRESHOLD, IMGSZ, DEVICE,
            CLASSES, MODEL_PATH, MAX_AGE_TRACKER, N_INIT_TRACKER,
            MOVE_THRESH, STATIONARY_FRAMES
        )
        
        # Validación de valores
        assert 0 < CONFIDENCE_THRESHOLD < 1, "CONFIDENCE_THRESHOLD inválido"
        assert 0 < IOU_THRESHOLD < 1, "IOU_THRESHOLD inválido"
        assert IMGSZ > 0, "IMGSZ inválido"
        assert DEVICE in ['cpu', 'cuda'], "DEVICE debe ser 'cpu' o 'cuda'"
        assert isinstance(CLASSES, list), "CLASSES debe ser lista"
        assert MAX_AGE_TRACKER > 0, "MAX_AGE_TRACKER inválido"
        assert N_INIT_TRACKER > 0, "N_INIT_TRACKER inválido"
        assert MOVE_THRESH > 0, "MOVE_THRESH inválido"
        assert STATIONARY_FRAMES > 0, "STATIONARY_FRAMES inválido"
        
        print(f"  ✓ CONFIDENCE_THRESHOLD: {CONFIDENCE_THRESHOLD}")
        print(f"  ✓ IOU_THRESHOLD: {IOU_THRESHOLD}")
        print(f"  ✓ IMGSZ: {IMGSZ}")
        print(f"  ✓ DEVICE: {DEVICE}")
        print(f"  ✓ CLASSES: {CLASSES}")
        print(f"  ✓ MODEL_PATH: {MODEL_PATH}")
        print(f"  ✓ MAX_AGE_TRACKER: {MAX_AGE_TRACKER}")
        print(f"  ✓ N_INIT_TRACKER: {N_INIT_TRACKER}")
        print(f"  ✓ MOVE_THRESH: {MOVE_THRESH}")
        print(f"  ✓ STATIONARY_FRAMES: {STATIONARY_FRAMES}")
        
        print("✓ Configuración válida\n")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}\n")
        return False

def test_model_loading():
    """Verifica que el modelo YOLO pueda cargar"""
    print("📦 Verificando modelo YOLO...")
    
    try:
        from ultralytics import YOLO
        from config import MODEL_PATH
        
        if not os.path.exists(MODEL_PATH):
            print(f"  ⚠ Modelo no encontrado: {MODEL_PATH}")
            print(f"  ℹ Se descargará automáticamente en primera ejecución")
            print("✓ YOLO está listo para descargar modelo\n")
            return True
        else:
            model = YOLO(MODEL_PATH)
            print(f"  ✓ Modelo cargado: {MODEL_PATH}")
            print(f"  ✓ Clases disponibles: {len(model.names)}")
            print("✓ Modelo YOLO funcional\n")
            return True
            
    except Exception as e:
        print(f"❌ Error con YOLO: {e}\n")
        return False

def test_modules():
    """Verifica que todos los módulos principales puedan importarse"""
    print("📚 Verificando módulos del sistema...")
    
    modules = ['detector', 'tracker', 'counter', 'visualizer', 'utils']
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}.py")
        except ImportError as e:
            print(f"  ✗ {module}.py: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Módulos fallidos: {', '.join(failed)}\n")
        return False
    
    print("✓ Todos los módulos importan correctamente\n")
    return True

def main():
    """Ejecuta todos los tests"""
    print("=" * 50)
    print("🧪 VALIDACIÓN DEL SISTEMA AGROGUARDIAN")
    print("=" * 50 + "\n")
    
    results = {
        "Dependencias": test_imports(),
        "Configuración": test_config(),
        "Modelo YOLO": test_model_loading(),
        "Módulos": test_modules(),
    }
    
    print("=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test}")
    
    print(f"\nResultado: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n✅ ¡Sistema listo para usar!")
        print("Ejecuta: python main.py --video ../videos/input.mp4")
        return 0
    else:
        print("\n❌ Hay problemas. Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
