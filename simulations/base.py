from abc import ABC, abstractmethod
from typing import Generator, Any
from models.simulation_step import SimulationStep

class BaseSimulation(ABC):
    """시뮬레이션의 기본 클래스"""
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Generator[SimulationStep, None, Any]:
        """시뮬레이션을 실행하고 각 단계를 생성"""
        pass 