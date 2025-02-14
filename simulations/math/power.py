from typing import Generator, Any
from ..base import BaseSimulation
from models.simulation_step import SimulationStep

class PowerSimulation(BaseSimulation):
    @staticmethod
    def run(base: int, exponent: int) -> Generator[SimulationStep, None, Any]:
        func_name = f"power({base}, {exponent})"
        yield SimulationStep("push", {"function": func_name})

        if exponent < 0:
            yield SimulationStep("result", {
                "result": "오류: 음수 지수",
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return None

        yield SimulationStep("highlight", {
            "keyword": "기저 조건",
            "message": f"지수 {exponent} 확인"
        })

        if exponent == 0:
            yield SimulationStep("result", {
                "result": 1,
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return 1

        yield SimulationStep("highlight", {
            "keyword": "재귀 호출",
            "message": f"지수가 {'짝수' if exponent % 2 == 0 else '홀수'}인 경우 처리"
        })

        half = yield from PowerSimulation.run(base, exponent // 2)
        
        if exponent % 2 == 0:
            result = half * half
            yield SimulationStep("highlight", {
                "keyword": "반환",
                "message": f"{base}^{exponent} = ({base}^{exponent//2})^2 = {half}^2 = {result}"
            })
        else:
            result = half * half * base
            yield SimulationStep("highlight", {
                "keyword": "반환",
                "message": f"{base}^{exponent} = ({base}^{exponent//2})^2 × {base} = {half}^2 × {base} = {result}"
            })

        yield SimulationStep("result", {
            "result": result,
            "function": func_name
        })
        yield SimulationStep("pop", {"function": func_name})
        return result 