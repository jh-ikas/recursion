from typing import Generator, Any
from ..base import BaseSimulation
from models.simulation_step import SimulationStep

class GCDSimulation(BaseSimulation):
    @staticmethod
    def run(a: int, b: int) -> Generator[SimulationStep, None, Any]:
        func_name = f"gcd({a}, {b})"
        yield SimulationStep("push", {"function": func_name})

        if a < 0 or b < 0:
            yield SimulationStep("result", {
                "result": "오류: 음수 입력",
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return None

        yield SimulationStep("highlight", {
            "keyword": "기저 조건",
            "message": f"b={b} 확인"
        })

        if b == 0:
            yield SimulationStep("result", {
                "result": a,
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return a

        yield SimulationStep("highlight", {
            "keyword": "재귀 호출",
            "message": f"gcd({b}, {a}%{b}) 계산"
        })
        result = yield from GCDSimulation.run(b, a % b)
        
        yield SimulationStep("highlight", {
            "keyword": "반환",
            "message": f"gcd({a}, {b}) = gcd({b}, {a}%{b}) = {result}"
        })
        yield SimulationStep("result", {
            "result": result,
            "function": func_name
        })
        yield SimulationStep("pop", {"function": func_name})
        return result 