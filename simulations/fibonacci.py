from typing import Generator, Any
from .base import BaseSimulation
from models.simulation_step import SimulationStep

class FibonacciSimulation(BaseSimulation):
    @staticmethod
    def run(n: int) -> Generator[SimulationStep, None, Any]:
        func_name = f"fibonacci({n})"
        yield SimulationStep("push", {"function": func_name})

        if n < 0:
            yield SimulationStep("result", {
                "result": "오류: 음수 입력",
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return None

        # 기저 조건 먼저 확인
        yield SimulationStep("highlight", {
            "keyword": "기저 조건",
            "message": f"n={n} 확인"
        })
        
        if n <= 1:
            yield SimulationStep("result", {
                "result": n,
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return n

        # 첫 번째 재귀 호출 (n-1)
        yield SimulationStep("highlight", {
            "keyword": "재귀 호출",
            "message": f"fibonacci({n-1}) 계산"
        })
        result1 = yield from FibonacciSimulation.run(n - 1)

        # 두 번째 재귀 호출 (n-2)
        yield SimulationStep("highlight", {
            "keyword": "재귀 호출",
            "message": f"fibonacci({n-2}) 계산"
        })
        result2 = yield from FibonacciSimulation.run(n - 2)

        # 결과 계산 및 반환
        total = result1 + result2
        yield SimulationStep("highlight", {
            "keyword": "반환",
            "message": f"fibonacci({n}) = fibonacci({n-1}) + fibonacci({n-2}) = {result1} + {result2} = {total}"
        })
        yield SimulationStep("result", {
            "result": total,
            "function": func_name
        })
        yield SimulationStep("pop", {"function": func_name})
        return total 