import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._setup_logger()
        return cls._instance

    @classmethod
    def _setup_logger(cls):
        """로거 초기 설정"""
        cls._logger = logging.getLogger('RecursionVisualizer')
        cls._logger.setLevel(logging.DEBUG)

        # 로그 파일 설정
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(
            log_dir,
            f'recursion_visualizer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        cls._logger.addHandler(file_handler)

    @classmethod
    def debug(cls, message: str):
        if cls._logger:
            cls._logger.debug(message)

    @classmethod
    def info(cls, message: str):
        if cls._logger:
            cls._logger.info(message)

    @classmethod
    def warning(cls, message: str):
        if cls._logger:
            cls._logger.warning(message)

    @classmethod
    def error(cls, message: str):
        if cls._logger:
            cls._logger.error(message)

    @classmethod
    def cleanup(cls):
        """프로그램 종료 시 로그 파일 삭제"""
        if cls._logger:
            for handler in cls._logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    log_file = handler.baseFilename
                    handler.close()
                    cls._logger.removeHandler(handler)
                    if os.path.exists(log_file):
                        os.remove(log_file)
            
            # 로그 디렉토리가 비어있으면 삭제
            log_dir = 'logs'
            if os.path.exists(log_dir) and not os.listdir(log_dir):
                os.rmdir(log_dir)

    def log_performance(self, operation: str, duration: float):
        """성능 관련 로그 기록"""
        self.debug(f"성능 측정 - {operation}: {duration:.3f}초")

    def log_layout_update(self, node_count: int, modified_count: int):
        """레이아웃 업데이트 관련 로그 기록"""
        self.debug(
            f"레이아웃 업데이트 - 전체 노드: {node_count}, "
            f"수정된 노드: {modified_count}"
        )

    def log_animation_state(self, widget_id: str, progress: float):
        """애니메이션 상태 로깅"""
        self.debug(f"애니메이션 상태 - 위젯: {widget_id}, 진행도: {progress:.2f}")

    def log_cache_status(self, hit: bool, cache_size: int):
        """캐시 상태 로깅"""
        status = "히트" if hit else "미스"
        self.debug(f"캐시 상태 - {status}, 크기: {cache_size}") 