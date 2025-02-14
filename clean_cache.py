# 표준 라이브러리
import os
import shutil
import time
from pathlib import Path

class CacheCleaner:
    def __init__(self):
        self.cache_dir = Path.home() / '.sorting_visualizer' / 'cache'
        self.log_dir = Path.home() / '.sorting_visualizer' / 'logs'

    def clean_old_files(self, max_age_days=7):
        try:
            for directory in [self.cache_dir, self.log_dir]:
                if directory.exists():
                    for file in directory.glob('*'):
                        if file.stat().st_mtime < time.time() - (max_age_days * 86400):
                            file.unlink()
        except Exception:
            pass

    def clear_all_cache(self):
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True)
        except Exception:
            pass

    def clean_all(self):
        try:
            self._clean_temp_files()
            self._clean_logs()
            self._clean_performance_data()
        except Exception:
            pass  # 조용히 실패

def clean_cache():
    """프로젝트의 캐시 파일들을 제거하는 함수"""
    
    # 제거할 디렉토리 패턴들
    cache_patterns = [
        '__pycache__',
        '.pytest_cache',
        'build',
        'dist',
        '.coverage',
        '.mypy_cache',
        '.tox',
        '.eggs',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        'env',
        'venv',
        'ENV',
        'env.bak',
        'venv.bak',
    ]

    current_dir = Path.cwd()
    
    # 모든 하위 디렉토리 탐색
    for pattern in cache_patterns:
        if '*' in pattern:
            # 파일 패턴 처리
            for item in current_dir.rglob(pattern):
                try:
                    if item.is_file():
                        item.unlink()
                except Exception:
                    pass
        else:
            # 디렉토리 패턴 처리
            for item in current_dir.rglob(pattern):
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                except Exception:
                    pass

if __name__ == "__main__":
    clean_cache() 