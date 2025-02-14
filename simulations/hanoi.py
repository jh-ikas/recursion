from typing import Generator, Any
from .base import BaseSimulation
from models.simulation_step import SimulationStep

class HanoiSimulation(BaseSimulation):
    @staticmethod
    def run(n: int, source: str, target: str, auxiliary: str) -> Generator[SimulationStep, None, Any]:
        func_name = f"hanoi({n}, {source}, {target}, {auxiliary})"
        yield SimulationStep("push", {"function": func_name})

        # 입력값 검증
        if n <= 0:
            yield SimulationStep("result", {
                "result": "오류: 0 이하의 원판 수",
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return None

        # 기저 조건 확인
        yield SimulationStep("highlight", {
            "keyword": "기저 조건",
            "message": f"원판 개수 n={n} 확인"
        })

        if n == 1:
            # 단일 원판 이동
            yield SimulationStep("highlight", {
                "keyword": "기저 조건",
                "message": f"원판 1개를 {source}에서 {target}으로 직접 이동"
            })
            yield SimulationStep("animate", {
                "message": f"원판 이동: {source} → {target}",
                "disk": 1,
                "from": source,
                "to": target
            })
            yield SimulationStep("result", {
                "result": f"원판 1 이동 완료: {source} → {target}",
                "function": func_name
            })
            yield SimulationStep("pop", {"function": func_name})
            return

        # 1단계: n-1개 원판을 보조 기둥으로 이동
        yield SimulationStep("highlight", {
            "keyword": "재귀 호출",
            "message": f"{n-1}개 원판을 {source}에서 {auxiliary}로 이동 (보조 기둥 {target} 사용)"
        })
        yield from HanoiSimulation.run(n - 1, source, auxiliary, target)

        # 2단계: 가장 큰 원판을 목표 기둥으로 이동
        yield SimulationStep("highlight", {
            "keyword": "원판 이동",
            "message": f"가장 큰 원판 {n}을 {source}에서 {target}으로 이동"
        })
        yield SimulationStep("animate", {
            "message": f"원판 {n} 이동: {source} → {target}",
            "disk": n,
            "from": source,
            "to": target
        })

        # 3단계: n-1개 원판을 보조 기둥에서 목표 기둥으로 이동
        yield SimulationStep("highlight", {
            "keyword": "재귀 호출",
            "message": f"{n-1}개 원판을 {auxiliary}에서 {target}으로 이동 (보조 기둥 {source} 사용)"
        })
        yield from HanoiSimulation.run(n - 1, auxiliary, target, source)

        # 완료 메시지
        yield SimulationStep("result", {
            "result": f"{n}개 원판 이동 완료",
            "function": func_name
        })
        yield SimulationStep("pop", {"function": func_name}) 