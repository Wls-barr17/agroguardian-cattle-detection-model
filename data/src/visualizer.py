"""
visualizer.py - Módulo de visualización del sistema

Proporciona interfaz visual (HUD) para mostrar detecciones,
tracking y contadores en tiempo real.

Este módulo actúa como wrapper que puede usar diferentes
estrategias de visualización.
"""

from visualizer_hud import VisualizerHUD


class Visualizer:
    """
    Visualizador principal del sistema.
    
    Actualmente usa HUD profesional.
    Preparado para soportar otros modos de visualización en futuro.
    """
    
    def __init__(self):
        """Inicializa visualizador con HUD"""
        self.hud = VisualizerHUD()
    
    def draw(self, frame, tracks, counts, fps=0, frame_number=0):
        """
        Dibuja visualización completa sobre el frame.
        
        Args:
            frame: Frame de video
            tracks: Objetos rastreados
            counts: Contadores del sistema
            fps: Frames por segundo (opcional)
            frame_number: Número del frame (opcional)
        
        Returns:
            Frame anotado
        """
        return self.hud.draw(frame, tracks, counts, fps, frame_number)