import logging
import logging.handlers
from pathlib import Path
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

        # 로그 디렉토리 생성
        Settings.LOG.LOG_DIR.mkdir(parents=True, exist_ok=True)

        # 파일 핸들러 설정 (로그 로테이션 포함)
        file_handler = logging.handlers.RotatingFileHandler(
            Settings.LOG.LOG_DIR / 'recursion_visualizer.log',
            maxBytes=Settings.LOG.MAX_LOG_SIZE,
            backupCount=Settings.LOG.MAX_LOG_FILES
        )
        file_handler.setFormatter(logging.Formatter(Settings.LOG.LOG_FORMAT))
        self.logger.addHandler(file_handler)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(Settings.LOG.LOG_FORMAT))
        self.logger.addHandler(console_handler)

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

    def cleanup(self):
        """프로그램 종료 시 로그 파일 삭제"""
        if self.logger:
            for handler in self.logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    log_file = handler.baseFilename
                    handler.close()
                    self.logger.removeHandler(handler)
                    if log_file.exists():
                        log_file.unlink()
            
            # 로그 디렉토리가 비어있으면 삭제
            log_dir = Settings.LOG.LOG_DIR
            if log_dir.exists() and not list(log_dir.iterdir()):
                log_dir.rmdir()

    def log_animation_state(self, widget_id: str, progress: float):
        """애니메이션 상태 로깅"""
        self.logger.debug(f"애니메이션 상태 - 위젯: {widget_id}, 진행도: {progress:.2f}")

    def log_cache_status(self, hit: bool, cache_size: int):
        """캐시 상태 로깅"""
        status = "히트" if hit else "미스"
        self.logger.debug(f"캐시 상태 - {status}, 크기: {cache_size}") 