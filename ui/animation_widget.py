from typing import Optional, Dict, TYPE_CHECKING
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QLinearGradient, QRadialGradient, 
    QPainterPath, QFont
)

from models.call_tree import CallTreeManager
from models.simulation_step import SimulationStep
from ui.styles import Styles

if TYPE_CHECKING:
    from models.call_tree import Node

class AnimationWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.message = ""
        self.call_tree_manager: Optional[CallTreeManager] = None
        self.dark_mode = False
        
        # 애니메이션 효과를 위한 속성들
        self.highlight_node = None
        self.highlight_alpha = 0
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.updateHighlight)
        self.fade_timer.setInterval(50)  # 20fps
        
        # 노드 스타일 설정
        self.node_radius = 25
        self.node_spacing = 120
        self.level_height = 100
        
        # 애니메이션 상태
        self.animation_progress = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.updateAnimation)
        self.animation_timer.setInterval(16)  # 약 60fps
        
        # 색상 설정
        self.colors = Styles.get_colors(self.dark_mode)

        # 레이아웃 업데이트 타이머 추가
        self.layout_timer = QTimer()
        self.layout_timer.timeout.connect(self.updateLayout)
        self.layout_timer.setInterval(16)  # 60fps
        self.layout_timer.start()

        # 애니메이션 설정
        self.animation_settings = {
            'node_fade_duration': 500,    # ms
            'edge_animation_duration': 300,# ms
            'highlight_duration': 1000,    # ms
            'smooth_factor': 0.1          # 부드러운 이동 계수
        }
        
        # 툴팁 활성화
        self.setToolTip("재귀 호출 트리 시각화")
        self.setMouseTracking(True)  # 마우스 이동 추적

    def setDarkMode(self, enabled: bool):
        self.dark_mode = enabled
        self.colors = Styles.get_colors(enabled)
        self.update()
        
    def updateAnimation(self):
        smooth_factor = self.animation_settings['smooth_factor']
        self.animation_progress = min(1.0, self.animation_progress + smooth_factor)
        self.update()
        if self.animation_progress >= 1.0:
            self.animation_timer.stop()

    def setMessage(self, msg: str):
        self.message = msg
        self.update()

    def setCallTreeManager(self, manager: CallTreeManager):
        self.call_tree_manager = manager
        if manager:
            manager.node_radius = self.node_radius
            manager.update_layout(self.width(), self.height())
        self.animation_progress = 0
        self.animation_timer.start()

    def highlightNode(self, node_id: int):
        self.highlight_node = node_id
        self.highlight_alpha = 255
        self.fade_timer.start()
        
    def updateHighlight(self):
        fade_step = 255 / (self.animation_settings['node_fade_duration'] / 50)
        self.highlight_alpha = max(0, self.highlight_alpha - fade_step)
        if self.highlight_alpha == 0:
            self.fade_timer.stop()
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.call_tree_manager:
            self.call_tree_manager.update_layout(self.width(), self.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        self.drawBackground(painter)
        
        if self.call_tree_manager and self.call_tree_manager.nodes:
            self.drawEdges(painter)
            self.drawNodes(painter)
            self.drawHighlights(painter)
        
        self.drawMessage(painter)

    def drawBackground(self, painter: QPainter):
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self.colors['background_start'])
        gradient.setColorAt(1, self.colors['background_end'])
        painter.fillRect(self.rect(), gradient)
        
        # 그리드 라인
        painter.setPen(QPen(QColor(100, 100, 100, 30), 1, Qt.DashLine))
        grid_size = 50
        for i in range(0, self.width(), grid_size):
            painter.drawLine(i, 0, i, self.height())
        for i in range(0, self.height(), grid_size):
            painter.drawLine(0, i, self.width(), i)

    def drawEdges(self, painter: QPainter):
        if not self.call_tree_manager:
            return
            
        for node in self.call_tree_manager.nodes.values():
            if node.parent is not None:
                parent = self.call_tree_manager.nodes[node.parent]
                
                path = QPainterPath()
                start_x = node.x
                start_y = node.y
                end_x = parent.x
                end_y = parent.y
                
                # 제어점 계산
                ctrl1_x = start_x
                ctrl1_y = start_y - (start_y - end_y) * 0.5
                ctrl2_x = end_x
                ctrl2_y = end_y + (start_y - end_y) * 0.5
                
                path.moveTo(start_x, start_y)
                path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
                
                gradient = QLinearGradient(start_x, start_y, end_x, end_y)
                if node.done:
                    gradient.setColorAt(0, self.colors['edge_inactive'])
                    gradient.setColorAt(1, self.colors['edge_inactive'])
                else:
                    gradient.setColorAt(0, self.colors['edge_active'])
                    gradient.setColorAt(1, self.colors['edge_active'])
                
                pen = QPen()
                pen.setBrush(gradient)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPath(path)

    def drawNodes(self, painter: QPainter):
        if not self.call_tree_manager:
            return
            
        for node in self.call_tree_manager.nodes.values():
            x, y = node.x, node.y
            
            # 노드 그림자
            shadow = QRadialGradient(x, y, self.node_radius + 5)
            shadow.setColorAt(0, QColor(0, 0, 0, 50))
            shadow.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(shadow)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                int(x - self.node_radius - 5),
                int(y - self.node_radius - 5),
                int(2 * (self.node_radius + 5)),
                int(2 * (self.node_radius + 5))
            )
            
            # 노드 본체
            if node.done:
                color = self.colors['node_inactive']
                border_color = QColor(150, 150, 150)
            else:
                color = self.colors['node_active']
                border_color = QColor(255, 255, 255)
            
            # 노드 배경
            painter.setBrush(color)
            painter.setPen(QPen(border_color, 2))
            painter.drawEllipse(
                int(x - self.node_radius),
                int(y - self.node_radius),
                int(2 * self.node_radius),
                int(2 * self.node_radius)
            )
            
            # 텍스트 설정
            text_color = self.colors['text']
            if node.done:
                text_color = QColor(100, 100, 100)
            
            painter.setPen(QPen(text_color, 1))
            
            # 함수 이름과 파라미터 분리
            func_parts = node.function.split('(')
            func_name = func_parts[0]
            params = '(' + func_parts[1] if len(func_parts) > 1 else ''
            
            # 함수 이름 그리기
            font = QFont("Arial", 10)
            font.setBold(True)
            painter.setFont(font)
            name_rect = QRect(
                int(x - self.node_radius),
                int(y - 10),
                int(2 * self.node_radius),
                20
            )
            painter.drawText(name_rect, Qt.AlignCenter, func_name)
            
            # 파라미터 그리기 (작은 폰트)
            if params:
                font.setPointSize(8)
                painter.setFont(font)
                param_rect = QRect(
                    int(x - self.node_radius * 1.5),  # 더 넓은 영역
                    int(y + 5),
                    int(3 * self.node_radius),  # 더 넓은 영역
                    20
                )
                # 파라미터가 너무 길면 줄임
                metrics = painter.fontMetrics()
                params = metrics.elidedText(params, Qt.ElideMiddle, param_rect.width())
                painter.drawText(param_rect, Qt.AlignCenter, params)

    def drawHighlights(self, painter: QPainter):
        if (self.highlight_node is not None and 
            self.highlight_alpha > 0 and 
            self.call_tree_manager):
            
            node = self.call_tree_manager.nodes.get(self.highlight_node)
            if node:
                glow = QRadialGradient(node.x, node.y, self.node_radius * 2)
                # alpha 값을 정수로 변환
                alpha = int(self.highlight_alpha)
                glow_color = QColor(
                    self.colors['highlight'].red(),
                    self.colors['highlight'].green(),
                    self.colors['highlight'].blue(),
                    alpha  # 정수 타입의 alpha 값 사용
                )
                glow.setColorAt(0, glow_color)
                glow.setColorAt(1, QColor(255, 215, 0, 0))
                
                painter.setBrush(glow)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(
                    int(node.x - self.node_radius * 2),
                    int(node.y - self.node_radius * 2),
                    int(4 * self.node_radius),
                    int(4 * self.node_radius)
                )

    def drawMessage(self, painter: QPainter):
        if self.message:
            msg_rect = QRect(10, self.height() - 60, self.width() - 20, 50)
            
            gradient = QLinearGradient(
                msg_rect.topLeft(),
                msg_rect.bottomLeft()
            )
            gradient.setColorAt(0, QColor(0, 0, 0, 200))
            gradient.setColorAt(1, QColor(0, 0, 0, 180))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(msg_rect, 10, 10)
            
            painter.setPen(QPen(Qt.white))
            font = QFont("Arial", 12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(msg_rect, Qt.AlignCenter, self.message)

    def updateLayout(self):
        """주기적으로 레이아웃 업데이트"""
        if self.call_tree_manager and self.call_tree_manager.modified_nodes:
            self.call_tree_manager.update_layout(self.width(), self.height())
            self.update()  # 화면 갱신 

    def mouseMoveEvent(self, event):
        """마우스 이동 시 노드 정보 표시"""
        if not self.call_tree_manager:
            return
        
        pos = event.pos()
        for node in self.call_tree_manager.nodes.values():
            if self._is_point_in_node(pos.x(), pos.y(), node):
                status = "완료" if node.done else "진행 중"
                self.setToolTip(
                    f"함수: {node.function}\n"
                    f"상태: {status}\n"
                    f"깊이: {node.depth}"
                )
                return
        self.setToolTip("재귀 호출 트리 시각화")

    def _is_point_in_node(self, x: int, y: int, node: 'Node') -> bool:
        """주어진 좌표가 노드 영역 내에 있는지 확인"""
        dx = x - node.x
        dy = y - node.y
        return (dx * dx + dy * dy) <= self.node_radius * self.node_radius 