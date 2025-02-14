from typing import Dict, Optional, List, Set
from dataclasses import dataclass
import math
import time

@dataclass
class Node:
    """호출 트리의 노드를 나타내는 데이터 클래스"""
    id: int
    function: str
    parent: Optional[int]
    children: List[int]
    depth: int
    done: bool
    x: float = 0.0
    y: float = 0.0
    target_x: float = 0.0  # 애니메이션을 위한 목표 x 좌표

class CallTreeManager:
    def __init__(self):
        self.call_id_counter = 0
        self.stack: List[int] = []
        self.nodes: Dict[int, Node] = {}
        self.node_radius = 25
        self.min_node_distance = self.node_radius * 4  # 간격 증가
        self.vertical_spacing = self.node_radius * 3   # 수직 간격 추가
        self.modified_nodes: Set[int] = set()  # 변경된 노드 추적
        self._layout_cache: Dict[int, Dict[str, float]] = {}  # 레이아웃 캐시
        self._cache_invalidated = False
        self._last_update = 0.0

    def invalidate_cache(self):
        """레이아웃 캐시 무효화"""
        self._layout_cache.clear()
        self._cache_invalidated = True

    def push(self, function_name: str) -> int:
        self.invalidate_cache()
        """새로운 함수 호출을 트리에 추가"""
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
        # 업데이트가 필요한지 확인
        if not self._should_update_layout():
            return

        try:
            # 캐시된 레이아웃이 있고 무효화되지 않았다면 사용
            if self._layout_cache and not self._cache_invalidated:
                self._restore_from_cache()
                return
            
            start_time = time.time()
            
            if not self.nodes:
                return

            # 여백 설정
            margin_x = self.node_radius * 2
            margin_y = self.node_radius * 2
            available_width = width - 2 * margin_x
            available_height = height - 2 * margin_y

            # 레벨별 너비와 노드 수 계산
            level_widths: Dict[int, float] = {}
            nodes_per_level: Dict[int, int] = {}
            root_nodes = [nid for nid, node in self.nodes.items() if node.depth == 0]
            
            # 각 레벨의 노드 수 계산
            for node in self.nodes.values():
                nodes_per_level[node.depth] = nodes_per_level.get(node.depth, 0) + 1

            # 최대 깊이와 가장 많은 노드를 가진 레벨 찾기
            max_depth = max(node.depth for node in self.nodes.values())
            max_nodes_in_level = max(nodes_per_level.values())

            # 동적 간격 계산
            horizontal_spacing = min(
                available_width / max_nodes_in_level,
                self.min_node_distance * 2
            )
            vertical_spacing = available_height / (max_depth + 1)

            # 각 레벨의 전체 너비 계산
            for depth in range(max_depth + 1):
                level_width = horizontal_spacing * nodes_per_level.get(depth, 1)
                level_widths[depth] = level_width

            # 노드 배치
            for depth in range(max_depth + 1):
                nodes_at_depth = [node for node in self.nodes.values() if node.depth == depth]
                nodes_at_depth.sort(key=lambda n: n.id)
                
                # 현재 레벨의 전체 너비
                level_width = level_widths[depth]
                
                # 시작 x 좌표 계산 (중앙 정렬)
                start_x = (width - level_width) / 2 + horizontal_spacing / 2

                # 각 노드의 x 좌표 계산
                for i, node in enumerate(nodes_at_depth):
                    target_x = start_x + i * horizontal_spacing
                    
                    if node.id in self.modified_nodes:
                        # 부드러운 이동을 위한 보간
                        if abs(node.x - target_x) < 1:
                            node.x = target_x
                        else:
                            node.x += (target_x - node.x) * 0.1
                        node.target_x = target_x
                    
                    # y 좌표 계산
                    node.y = margin_y + depth * vertical_spacing

            # 부모-자식 관계에 따른 위치 최적화
            for node_id in self.nodes:
                node = self.nodes[node_id]
                if node.parent is not None:
                    parent = self.nodes[node.parent]
                    siblings = [self.nodes[c] for c in parent.children]
                    if len(siblings) > 1:
                        # 부모 노드를 자식들의 중앙에 위치시키기
                        avg_x = sum(s.x for s in siblings) / len(siblings)
                        if parent.id in self.modified_nodes:
                            parent.target_x = avg_x
                            if abs(parent.x - avg_x) < 1:
                                parent.x = avg_x
                            else:
                                parent.x += (avg_x - parent.x) * 0.1

            # 화면 범위 제한
            for node in self.nodes.values():
                node.x = max(margin_x, min(width - margin_x, node.x))
                node.target_x = max(margin_x, min(width - margin_x, node.target_x))

            # 레이아웃 최적화 추가
            self._optimize_layout()
            
            # 서브트리 위치 최적화
            for root_id in root_nodes:
                self._optimize_subtree_positions(root_id, level_widths)

            # 성능 로깅 추가
            duration = time.time() - start_time
            from utils.logger import Logger
            Logger().log_performance("레이아웃 업데이트", duration)
            Logger().log_layout_update(
                node_count=len(self.nodes),
                modified_count=len(self.modified_nodes)
            )

            self.modified_nodes.clear()

            # 새로운 레이아웃을 캐시에 저장
            self._cache_layout()
            self._cache_invalidated = False
        except Exception as e:
            Logger().error(f"레이아웃 업데이트 실패: {str(e)}")
            self._apply_fallback_layout(width, height)

    def _apply_fallback_layout(self, width: int, height: int) -> None:
        """레이아웃 계산 실패 시 기본 레이아웃 적용"""
        margin = self.node_radius * 2
        for node in self.nodes.values():
            node.x = width / 2
            node.y = margin + node.depth * (self.node_radius * 4)

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

    def _should_update_layout(self) -> bool:
        """레이아웃 업데이트 필요 여부 확인"""
        if not self.modified_nodes:
            return False
        
        # 마지막 업데이트 이후 시간 체크
        current_time = time.time()
        if hasattr(self, '_last_update'):
            if current_time - self._last_update < 0.016:  # 약 60fps
                return False
        self._last_update = current_time
        return True

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