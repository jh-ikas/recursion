from typing import Dict
from PyQt5.QtGui import QColor

class Styles:
    @staticmethod
    def get_dark_theme() -> Dict[str, str]:
        return {
            'main_window': """
                QMainWindow, QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
            """,
            'button': """
                QPushButton {
                    background-color: #0d47a1;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
            """,
            'combo_box': """
                QComboBox {
                    background-color: #333333;
                    color: white;
                    border: 1px solid #555555;
                    padding: 5px;
                }
            """,
            'text_edit': """
                QTextEdit, QListWidget {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
            """,
            'group_box': """
                QGroupBox {
                    border: 2px solid #555555;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #ffffff;
                }
            """
        }

    @staticmethod
    def get_light_theme() -> Dict[str, str]:
        return {
            'main_window': """
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: #000000;
                }
            """,
            'button': """
                QPushButton {
                    background-color: #1976d2;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
            """,
            'combo_box': """
                QComboBox {
                    background-color: white;
                    border: 1px solid #cccccc;
                    padding: 5px;
                }
            """,
            'text_edit': """
                QTextEdit, QListWidget {
                    background-color: white;
                    border: 1px solid #cccccc;
                }
            """,
            'group_box': """
                QGroupBox {
                    border: 2px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #000000;
                }
            """
        }

    @staticmethod
    def get_colors(dark_mode: bool = False) -> Dict[str, QColor]:
        if dark_mode:
            return {
                'background_start': QColor(40, 44, 52),
                'background_end': QColor(30, 34, 42),
                'node_active': QColor(255, 100, 100),
                'node_inactive': QColor(150, 150, 150),
                'edge_active': QColor(255, 100, 100),
                'edge_inactive': QColor(100, 100, 100),
                'text': QColor(255, 255, 255),
                'highlight': QColor(255, 215, 0)
            }
        else:
            return {
                'background_start': QColor(240, 240, 255),
                'background_end': QColor(255, 255, 255),
                'node_active': QColor(255, 100, 100),
                'node_inactive': QColor(180, 180, 180),
                'edge_active': QColor(200, 50, 50),
                'edge_inactive': QColor(100, 100, 100),
                'text': QColor(0, 0, 0),
                'highlight': QColor(255, 215, 0)
            } 