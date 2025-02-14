from typing import Generator, Any
from ..base import BaseSimulation
from models.simulation_step import SimulationStep

class FactorialSimulation(BaseSimulation):
    @staticmethod
    def run(n: int) -> Generator[SimulationStep, None, Any]:
        func_name = f"factorial({n})"
        yield SimulationStep("push", {"function": func_name})

        if n < 0:
            yield SimulationStep("result", {
                "result": "오류: 음수 입력",
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return None

        yield SimulationStep("highlight", {
            "keyword": "기저 조건",
            "message": f"n={n} 확인"
        })

        if n <= 1:
            yield SimulationStep("result", {
                "result": 1,
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return 1

        yield SimulationStep("highlight", {
            "keyword": "재귀 호출",
            "message": f"{n}! = {n} × ({n-1})! 계산"
        })
        prev_factorial = yield from FactorialSimulation.run(n - 1)
        
        total = n * prev_factorial
        yield SimulationStep("highlight", {
            "keyword": "반환",
            "message": f"{n}! = {n} × ({n-1})! = {n} × {prev_factorial} = {total}"
        })
        yield SimulationStep("result", {
            "result": total,
            "function": func_name
        })
        yield SimulationStep("pop", {"function": func_name})
        return total 