"""
counter.py
Cuenta vacas individuales y detecta movimiento.
Una vaca se cuenta solo cuando está estacionaria por un tiempo (N frames consecutivos).
"""

from collections import defaultdict, deque
import numpy as np

class Counter:
    """
    Contador de vacas con detección de movimiento.
    Estrategia: Solo contar vacas que se mantienen ESTACIONARIAS por N frames,
    para evitar duplicados y asegurar una cuenta confiable.
    """
    def __init__(self, move_thresh=5.0, stationary_frames=10):
        """
        Args:
            move_thresh: Umbral de movimiento en píxeles (si se mueve más, no está estacionario)
            stationary_frames: Número de frames consecutivos sin movimiento para contar
        """
        # Umbral de movimiento en píxeles
        self.move_thresh = move_thresh
        # Número de frames consecutivos para confirmar estacionariedad
        self.stationary_frames = stationary_frames

        # Diccionario: track_id -> deque de centros del bounding box
        self.positions = defaultdict(lambda: deque(maxlen=stationary_frames))
        
        # Set de track_ids que ya fueron contados (para no contar duplicados)
        self.counted_stationary = set()
        
        # Contadores totales
        self.total_cows = 0
        self.people_count = 0
        self.active_cows = 0

    def _is_stationary(self, track_id):
        """
        Verifica si una vaca ha estado estacionaria en los últimos N frames.
        
        Args:
            track_id: ID del track
        
        Returns:
            True si la vaca está estacionaria, False caso contrario
        """
        if track_id not in self.positions:
            return False
        
        positions_list = list(self.positions[track_id])
        if len(positions_list) < self.stationary_frames:
            return False
        
        # Calcula la distancia desde la posición inicial
        positions_array = np.array(positions_list)
        initial_pos = positions_array[0]
        distances = np.linalg.norm(positions_array - initial_pos, axis=1)
        max_distance = np.max(distances)
        
        return max_distance < self.move_thresh

    def update(self, tracks):
        """
        Actualiza contadores con los tracks actuales.
        
        Args:
            tracks: Lista de dicts con keys: bbox, confidence, class_id, track_id
        
        Returns:
            Dict con contadores: total_cows, stationary_cows, active_cows, people
        """
        # Actualiza conjunto de IDs activos
        active_ids = {t["track_id"] for t in tracks}
        
        # Limpia tracks que desaparecieron
        for tid in list(self.positions.keys()):
            if tid not in active_ids:
                del self.positions[tid]

        # Reinicia contadores de este frame
        self.people_count = 0
        self.active_cows = 0
        
        # Procesa cada track
        for t in tracks:
            cls = int(t["class_id"])
            tid = t["track_id"]
            
            if cls == 0: # Vaca (modelo actual)
                self.active_cows += 1
                
                # Calcula centro del bounding box
                l, top, r, b = t["bbox"]
                cx = (l + r) / 2.0
                cy = (top + b) / 2.0

                # Agregar posición al historial
                self.positions[tid].append((cx, cy))

                # Verifica si esta vaca debe contarse
                if tid not in self.counted_stationary and self._is_stationary(tid):
                    self.counted_stationary.add(tid)
                    self.total_cows += 1
                    
                elif cls == 1:
                # Persona (reservado para futuro)
                    self.people_count += 1
        
        return {
            "total_cows": self.total_cows,
            "stationary_cows": len(self.counted_stationary),
            "active_cows": self.active_cows,
            "people": self.people_count,
            "stationary_ids": self.counted_stationary.copy(),  # IDs de vacas estacionarias
        }

    def reset(self):
        """
        Reinicia todos los contadores.
        Útil para resetear entre videos o sesiones.
        """
        self.positions.clear()
        self.counted_stationary.clear()
        self.total_cows = 0
        self.people_count = 0
        self.active_cows = 0
