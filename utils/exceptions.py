class RecursionVisualizerError(Exception):
    """기본 예외 클래스"""
    pass

class LayoutError(RecursionVisualizerError):
    """레이아웃 계산 관련 예외"""
    pass

class SimulationError(RecursionVisualizerError):
    """시뮬레이션 실행 관련 예외"""
    pass 