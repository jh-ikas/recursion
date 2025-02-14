from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SimulationStep:
    """시뮬레이션의 각 단계를 나타내는 데이터 클래스"""
    step_type: str  # "push", "pop", "highlight", "animate", "result"
    details: Dict[str, Any] 