from typing import Generator, Any, List
from ..base import BaseSimulation
from models.simulation_step import SimulationStep

class CombinationSimulation(BaseSimulation):
    @staticmethod
    def run(elements: List[int], k: int, start: int = 0, current: List[int] = None) -> Generator[SimulationStep, None, Any]:
        if current is None:
            current = []
            
        func_name = f"combination({elements}, {k}, current={current})"
        yield SimulationStep("push", {"function": func_name})

        if len(current) == k:
            yield SimulationStep("highlight", {
                "keyword": "기저 조건",
                "message": "조합 완성"
            })
            yield SimulationStep("result", {
                "result": current,
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return [current]

        if start >= len(elements):
            yield SimulationStep("pop", {"function": func_name})
            return []

        results = []
        for i in range(start, len(elements)):
            yield SimulationStep("highlight", {
                "keyword": "재귀 호출",
                "message": f"원소 {elements[i]} 선택"
            })
            
            new_current = current + [elements[i]]
            sub_results = yield from CombinationSimulation.run(elements, k, i + 1, new_current)
            results.extend(sub_results)

        yield SimulationStep("result", {
            "result": results,
            "function": func_name
        })
        yield SimulationStep("pop", {"function": func_name})
        return results 