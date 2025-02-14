from dataclasses import dataclass
from pathlib import Path

@dataclass
class UISettings:
    NODE_RADIUS: int = 25
    MIN_NODE_DISTANCE: int = 100  # NODE_RADIUS * 4
    VERTICAL_SPACING: int = 75    # NODE_RADIUS * 3
    ANIMATION_SPEED: float = 0.1
    LAYOUT_UPDATE_INTERVAL: float = 0.016  # ~60fps
    LOG_UPDATE_INTERVAL: float = 1000      # 1초
    SIMULATION_SPEED_MIN: int = 100        # 최소 시뮬레이션 속도 (ms)
    SIMULATION_SPEED_MAX: int = 2000       # 최대 시뮬레이션 속도 (ms)
    SIMULATION_SPEED_DEFAULT: int = 1000   # 기본 시뮬레이션 속도 (ms)

@dataclass
class LogSettings:
    LOG_DIR: Path = Path.home() / '.recursion_visualizer' / 'logs'
    MAX_LOG_FILES: int = 10
    MAX_LOG_SIZE: int = 1024 * 1024  # 1MB
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

@dataclass
class CacheSettings:
    CACHE_DIR: Path = Path.home() / '.recursion_visualizer' / 'cache'
    MAX_CACHE_AGE_DAYS: int = 7
    MAX_CACHE_SIZE: int = 100 * 1024 * 1024  # 100MB

class Settings:
    UI = UISettings()
    LOG = LogSettings()
    CACHE = CacheSettings() 