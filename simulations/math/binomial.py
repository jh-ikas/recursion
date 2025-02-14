from typing import Generator, Any
from ..base import BaseSimulation
from models.simulation_step import SimulationStep

class BinomialCoefficientSimulation(BaseSimulation):
    @staticmethod
    def run(n: int, k: int) -> Generator[SimulationStep, None, Any]:
        func_name = f"binomial({n}, {k})"
        yield SimulationStep("push", {"function": func_name})

        # 입력값 검증
        if n < 0 or k < 0 or k > n:
            yield SimulationStep("result", {
                "result": "오류: 잘못된 입력",
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return None

        yield SimulationStep("highlight", {
            "keyword": "기저 조건",
            "message": f"n={n}, k={k} 확인"
        })

        # 기저 조건
        if k == 0 or k == n:
            yield SimulationStep("result", {
                "result": 1,
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return 1

        # 재귀 호출: C(n,k) = C(n-1,k-1) + C(n-1,k)
        yield SimulationStep("highlight", {
            "keyword": "재귀 호출",
            "message": f"C({n},{k}) = C({n-1},{k-1}) + C({n-1},{k}) 계산"
        })
        
        left = yield from BinomialCoefficientSimulation.run(n - 1, k - 1)
        right = yield from BinomialCoefficientSimulation.run(n - 1, k)
        
        result = left + right
        yield SimulationStep("highlight", {
            "keyword": "반환",
            "message": f"C({n},{k}) = C({n-1},{k-1}) + C({n-1},{k}) = {left} + {right} = {result}"
        })
        yield SimulationStep("result", {
            "result": result,
            "function": func_name
        })
        yield SimulationStep("pop", {"function": func_name})
        return result 