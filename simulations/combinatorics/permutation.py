from typing import Generator, Any, List
from ..base import BaseSimulation
from models.simulation_step import SimulationStep

class PermutationSimulation(BaseSimulation):
    @staticmethod
    def run(elements: List[int], current: List[int] = None) -> Generator[SimulationStep, None, Any]:
        if current is None:
            current = []
        
        func_name = f"permutation({elements}, {current})"
        yield SimulationStep("push", {"function": func_name})

        if not elements:
            yield SimulationStep("highlight", {
                "keyword": "기저 조건",
                "message": "순열 완성"
            })
            yield SimulationStep("result", {
                "result": current,
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return [current]

        results = []
        for i, elem in enumerate(elements):
            yield SimulationStep("highlight", {
                "keyword": "재귀 호출",
                "message": f"원소 {elem} 선택"
            })
            
            new_elements = elements[:i] + elements[i+1:]
            new_current = current + [elem]
            
            sub_results = yield from PermutationSimulation.run(new_elements, new_current)
            results.extend(sub_results)

        yield SimulationStep("result", {
            "result": results,
            "function": func_name
        })
        yield SimulationStep("pop", {"function": func_name})
        return results 