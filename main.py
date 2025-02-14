import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import RecursionVisualizer

def main():
    app = QApplication(sys.argv)
    window = RecursionVisualizer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 