from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from models.call_tree import CallTreeManager
from config.settings import Settings

class TreeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.call_tree = CallTreeManager()
        self.setMinimumSize(600, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 엣지 그리기
        self._draw_edges(painter)
        
        # 노드 그리기
        self._draw_nodes(painter)

    def _draw_edges(self, painter):
        pen = QPen(QColor(100, 100, 100))
        pen.setWidth(2)
        painter.setPen(pen)

        for node in self.call_tree.nodes.values():
            if node.parent is not None:
                parent = self.call_tree.nodes[node.parent]
                painter.drawLine(
                    int(node.x), int(node.y),
                    int(parent.x), int(parent.y)
                )

    def _draw_nodes(self, painter):
        for node in self.call_tree.nodes.values():
            # 노드 배경
            if node.done:
                painter.setBrush(QColor(200, 255, 200))
            else:
                painter.setBrush(QColor(255, 255, 200))

            # 노드 테두리
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)

            # 노드 그리기
            painter.drawEllipse(
                int(node.x - Settings.UI.NODE_RADIUS),
                int(node.y - Settings.UI.NODE_RADIUS),
                Settings.UI.NODE_RADIUS * 2,
                Settings.UI.NODE_RADIUS * 2
            )

            # 텍스트 그리기
            painter.drawText(
                int(node.x - Settings.UI.NODE_RADIUS),
                int(node.y - Settings.UI.NODE_RADIUS),
                Settings.UI.NODE_RADIUS * 2,
                Settings.UI.NODE_RADIUS * 2,
                Qt.AlignCenter,
                node.function
            ) 