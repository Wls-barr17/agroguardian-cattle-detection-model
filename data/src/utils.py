
"""
utils.py
Funciones utilitarias comunes.
La configuración principal del sistema está en config.py
"""

import argparse
from config import MOVE_THRESH, STATIONARY_FRAMES


def parse_args():
    parser = argparse.ArgumentParser(description="AgroGuardian YOLO surveillance prototype")
    parser.add_argument("--video", type=str, default="../data/videos/input.mp4", help="path to input video")
    parser.add_argument("--output", type=str, default="../outputs/output.mp4", help="path to save processed video")
    parser.add_argument("--move-thresh", type=float, default=MOVE_THRESH, help="movement threshold in pixels (from config.py)")
    parser.add_argument("--stationary-frames", type=int, default=STATIONARY_FRAMES, help="frames threshold for counting (from config.py)")
    return parser.parse_args()
