from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import path
import numpy as np

@dataclass
class FrameConfig:

    frame_widht: int
    frame_height: int
    half_width: int

@dataclass 
class CameraMatrix:

    left_camera_matrix: np.ndarray
    right_camera_matrix: np.ndarray

    left_dist_coeffs: np.ndarray
    right_dist_coeffs: np.ndarray

    fx: float
    fy: float
    cx: float
    cy: float


@dataclass
class RectificationMatrix:

    rotation: np.ndarray
    translation: np.ndarray

    rectification_left: np.ndarray
    rectification_right: np.ndarray

    projection_left: np.ndarray
    projection_right: np.ndarray

    q_matrix: np.ndarray

    baseline_mm: float

@dataclass
class RopeInsppectionConfig:
    frame: FrameConfig
    camera: CameraMatrix
    stereo: RectificationMatrix

    @classmethod
    def from_json(cls, json_path: str | Path) -> RopeInsppectionConfig:
        with open(json_path, r, encoding) as f:
            data = json.load(f)

        P_L = np.array(data["projection_left"], dtype=np.float64)
        P_R = np.array(data["projection_right"], dtype=np.float64)
        T = np.array(data["translation"], dtype=np.float64)