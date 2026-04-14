from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class CameraSettings:
    translation_speed: int
    rotation_speed: int
    fov_change_speed: float
    default_fov: float


class Settings:
    def __init__(self, file_path: str = "settings.toml"):
        with open(Path(file_path), "rb") as f:
            data = tomllib.load(f)

        self.camera = CameraSettings(**data["camera"])


settings = Settings()
