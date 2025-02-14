from typing import Dict, Optional, List, Set
from dataclasses import dataclass
import math
import time
from config.settings import Settings
from utils.logger import Logger
from utils.exceptions import LayoutError

@dataclass
class Node:
    """함수 호출 트리의 노드를 표현하는 클래스"""
    id: int
    function: str
    parent: Optional[int]
    children: List[int]
    depth: int
    done: bool
    x: float = 0.0
    y: float = 0.0
    target_x: float = 0.0
    
    def is_position_changed(self, threshold: float = 1.0) -> bool:
        """노드의 위치가 유의미하게 변경되었는지 확인"""
        return abs(self.x - self.target_x) > threshold

class CallTreeManager:
    def __init__(self):
        self.call_id_counter = 0
        self.stack: List[int] = []
        self.nodes: Dict[int, Node] = {}
        self.modified_nodes: Set[int] = set()
        self._layout_cache: Dict[int, Dict[str, float]] = {}
        self._cache_invalidated = False
        self._last_update = 0.0
        self.logger = Logger()

    def invalidate_cache(self):
        """레이아웃 캐시 무효화"""
        self._layout_cache.clear()
        self._cache_invalidated = True

    def push(self, function_name: str) -> int:
        """새로운 함수 호출을 트리에 추가"""
        try:
            self.invalidate_cache()
            parent_id = self.stack[-1] if self.stack else None
            depth = self.nodes[parent_id].depth + 1 if parent_id is not None else 0

            call_id = self.call_id_counter
            self.call_id_counter += 1

            node = Node(
                id=call_id,
                function=function_name,
                parent=parent_id,
                children=[],
                depth=depth,
                done=False
            )
            
            self.nodes[call_id] = node
            if parent_id is not None:
                self.nodes[parent_id].children.append(call_id)
                self.modified_nodes.add(parent_id)
            
            self.modified_nodes.add(call_id)
            self.stack.append(call_id)
            return call_id
        except Exception as e:
            self.logger.error(f"함수 호출 추가 실패: {str(e)}")
            raise

    def pop(self) -> Optional[int]:
        """현재 함수 호출 완료 처리"""
        if not self.stack:
            return None
            
        call_id = self.stack.pop()
        node = self.nodes[call_id]
        node.done = True
        self.modified_nodes.add(call_id)
        
        if node.parent is not None:
            self.modified_nodes.add(node.parent)
        
        return call_id

    def _calculate_subtree_width(self, node_id: int, level_widths: Dict[int, float]) -> float:
        """서브트리의 너비를 계산"""
        node = self.nodes[node_id]
        if not node.children:
            level_widths[node.depth] = max(
                level_widths.get(node.depth, 0),
                self.min_node_distance
            )
            return self.min_node_distance

        children_width = sum(
            self._calculate_subtree_width(child_id, level_widths)
            for child_id in node.children
        )
        width = max(self.min_node_distance, children_width)
        level_widths[node.depth] = max(
            level_widths.get(node.depth, 0),
            width
        )
        return width

    def _optimize_subtree_positions(self, node_id: int, level_widths: Dict[int, float]) -> float:
        """서브트리의 위치를 최적화"""
        node = self.nodes[node_id]
        if not node.children:
            return node.x

        # 자식 노드들의 평균 x 좌표 계산
        children_x = [self._optimize_subtree_positions(child_id, level_widths) 
                     for child_id in node.children]
        avg_x = sum(children_x) / len(children_x)
        
        # 부모 노드를 자식들의 중앙으로 이동
        if node.id in self.modified_nodes:
            node.target_x = avg_x
            if abs(node.x - avg_x) < 1:
                node.x = avg_x
            else:
                node.x += (avg_x - node.x) * 0.1

        return node.x

    def update_layout(self, width: int, height: int) -> None:
        """트리 레이아웃 업데이트"""
        if not self._should_update_layout():
            return

        try:
            start_time = time.time()
            
            if not self.nodes:
                return

            # 여백 계산
            margin_x = Settings.UI.NODE_RADIUS * 2
            margin_y = Settings.UI.NODE_RADIUS * 2
            available_width = width - 2 * margin_x
            available_height = height - 2 * margin_y

            # 레이아웃 최적화
            self._optimize_layout(available_width, available_height, margin_x, margin_y)

            # 성능 로깅
            duration = time.time() - start_time
            self.logger.log_performance("레이아웃 업데이트", duration)
            self.logger.log_layout_update(
                node_count=len(self.nodes),
                modified_count=len(self.modified_nodes)
            )

            self.modified_nodes.clear()
            self._cache_layout()
            self._cache_invalidated = False

        except Exception as e:
            self.logger.error(f"레이아웃 업데이트 실패: {str(e)}")
            self._apply_fallback_layout(width, height)
            raise LayoutError("레이아웃 계산 중 오류 발생")

    def _optimize_layout(self, available_width: float, available_height: float,
                        margin_x: float, margin_y: float) -> None:
        """레이아웃 최적화 수행"""
        try:
            # 각 레벨별 노드 수 계산
            level_nodes: Dict[int, List[Node]] = {}
            for node in self.nodes.values():
                if node.depth not in level_nodes:
                    level_nodes[node.depth] = []
                level_nodes[node.depth].append(node)

            # 각 레벨별 간격 계산
            max_depth = max(level_nodes.keys())
            vertical_spacing = available_height / (max_depth + 1)

            for depth, nodes in level_nodes.items():
                # 수평 간격 계산
                level_width = available_width
                node_spacing = level_width / (len(nodes) + 1)

                # 노드 위치 업데이트
                for i, node in enumerate(nodes, 1):
                    target_x = margin_x + (node_spacing * i)
                    target_y = margin_y + (depth * vertical_spacing)

                    if node.id in self.modified_nodes:
                        if abs(node.x - target_x) < 1:
                            node.x = target_x
                        else:
                            node.x += (target_x - node.x) * Settings.UI.ANIMATION_SPEED
                        node.target_x = target_x
                        node.y = target_y

            # 부모-자식 관계 최적화
            self._optimize_parent_child_positions()

        except Exception as e:
            self.logger.error(f"레이아웃 최적화 실패: {str(e)}")
            raise

    def _optimize_parent_child_positions(self) -> None:
        """부모-자식 노드 간의 위치 관계 최적화"""
        for node_id in self.nodes:
            node = self.nodes[node_id]
            if node.parent is not None:
                parent = self.nodes[node.parent]
                siblings = [self.nodes[c] for c in parent.children]
                if len(siblings) > 1:
                    avg_x = sum(s.x for s in siblings) / len(siblings)
                    if parent.id in self.modified_nodes:
                        parent.target_x = avg_x
                        if abs(parent.x - avg_x) < 1:
                            parent.x = avg_x
                        else:
                            parent.x += (avg_x - parent.x) * Settings.UI.ANIMATION_SPEED

    def _should_update_layout(self) -> bool:
        """레이아웃 업데이트가 필요한지 확인"""
        if not self.modified_nodes:
            return False
        
        current_time = time.time()
        if current_time - self._last_update < Settings.UI.LAYOUT_UPDATE_INTERVAL:
            return False
            
        self._last_update = current_time
        return True

    def _apply_fallback_layout(self, width: int, height: int) -> None:
        """레이아웃 실패 시 기본 레이아웃 적용"""
        margin = Settings.UI.NODE_RADIUS * 2
        for node in self.nodes.values():
            node.x = width / 2
            node.y = margin + node.depth * Settings.UI.VERTICAL_SPACING

    def _balance_subtree(self, node_id: int) -> None:
        """서브트리의 균형을 맞춤"""
        node = self.nodes[node_id]
        if not node.children:
            return

        # 자식 노드들의 위치를 재조정
        children = [self.nodes[child_id] for child_id in node.children]
        total_width = sum(self._calculate_subtree_width(c.id, {}) for c in children)
        current_x = node.x - total_width / 2

        for child in children:
            child_width = self._calculate_subtree_width(child.id, {})
            target_x = current_x + child_width / 2
            child.target_x = target_x
            current_x += child_width
            self._balance_subtree(child.id)

    def _optimize_layout(self) -> None:
        """전체 트리 레이아웃 최적화"""
        root_nodes = [nid for nid, node in self.nodes.items() if node.parent is None]
        for root_id in root_nodes:
            self._balance_subtree(root_id)

    def _cache_layout(self) -> None:
        """현재 레이아웃을 캐시에 저장"""
        for node_id, node in self.nodes.items():
            self._layout_cache[node_id] = {
                'x': node.x,
                'y': node.y,
                'target_x': node.target_x
            } 

    def _restore_from_cache(self) -> None:
        """캐시된 레이아웃을 복원"""
        for node_id, node in self.nodes.items():
            if node_id in self._layout_cache:
                node.x = self._layout_cache[node_id]['x']
                node.y = self._layout_cache[node_id]['y']
                node.target_x = self._layout_cache[node_id]['target_x'] 