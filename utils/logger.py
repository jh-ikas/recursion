import logging
import logging.handlers
from io import StringIO
from typing import Optional
from config.settings import Settings

class Logger:
    _instance: Optional['Logger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        self.logger = logging.getLogger('RecursionVisualizer')
        self.logger.setLevel(logging.DEBUG)

        # 메모리 기반 로그 핸들러
        self.log_stream = StringIO()
        memory_handler = logging.StreamHandler(self.log_stream)
        memory_handler.setFormatter(logging.Formatter(Settings.LOG.LOG_FORMAT))
        self.logger.addHandler(memory_handler)

        # 파일 핸들러 (임시 파일에 저장)
        import tempfile
        self.temp_log_file = tempfile.NamedTemporaryFile(
            mode='w',
            prefix='recursion_visualizer_',
            suffix='.log',
            delete=False
        )
        file_handler = logging.FileHandler(self.temp_log_file.name)
        file_handler.setFormatter(logging.Formatter(Settings.LOG.LOG_FORMAT))
        self.logger.addHandler(file_handler)

    def get_logs(self) -> str:
        """현재까지의 로그 내용 반환"""
        return self.log_stream.getvalue()

    def cleanup(self):
        """프로그램 종료 시 임시 파일 정리"""
        import os
        try:
            self.temp_log_file.close()
            os.unlink(self.temp_log_file.name)
        except:
            pass
        self.log_stream.close()

    def log_performance(self, operation: str, duration: float):
        self.logger.debug(f"성능 측정 - {operation}: {duration:.3f}초")

    def log_layout_update(self, node_count: int, modified_count: int):
        self.logger.debug(
            f"레이아웃 업데이트 - 전체 노드: {node_count}, "
            f"수정된 노드: {modified_count}"
        )

    def error(self, message: str):
        self.logger.error(message)

    def info(self, message: str):
        self.logger.info(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def log_animation_state(self, widget_id: str, progress: float):
        """애니메이션 상태 로깅"""
        self.logger.debug(f"애니메이션 상태 - 위젯: {widget_id}, 진행도: {progress:.2f}")

    def log_cache_status(self, hit: bool, cache_size: int):
        """캐시 상태 로깅"""
        status = "히트" if hit else "미스"
        self.logger.debug(f"캐시 상태 - {status}, 크기: {cache_size}") 