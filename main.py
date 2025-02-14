import sys
import os
from pathlib import Path
import logging
import tempfile
import traceback

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 모든 로깅을 임시 파일로 리다이렉션
temp_log_file = tempfile.NamedTemporaryFile(
    mode='w',
    prefix='recursion_visualizer_',
    suffix='.log',
    delete=False
)

# 루트 로거 설정
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# 기존 핸들러 제거
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# 파일 핸들러 추가
file_handler = logging.FileHandler(temp_log_file.name, encoding='utf-8')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
root_logger.addHandler(file_handler)

# sys.stderr도 파일로 리다이렉션 (utf-8 인코딩 사용)
sys.stderr = open(temp_log_file.name, 'a', encoding='utf-8')

# 예외 처리기 설정
def custom_excepthook(exc_type, exc_value, exc_traceback):
    """모든 처리되지 않은 예외를 로그 파일로 리다이렉션"""
    root_logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = custom_excepthook

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import RecursionVisualizer

def cleanup():
    """프로그램 종료 시 임시 파일 정리"""
    try:
        sys.stderr.close()
        temp_log_file.close()
        os.unlink(temp_log_file.name)
    except:
        pass

def main():
    try:
        app = QApplication(sys.argv)
        window = RecursionVisualizer()
        window.show()
        app.exec_()
    finally:
        cleanup()

if __name__ == "__main__":
    main() 