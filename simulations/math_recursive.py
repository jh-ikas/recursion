from typing import Generator, Any, List, Tuple
from .base import BaseSimulation
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

        # 지수를 반으로 나누어 계산
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