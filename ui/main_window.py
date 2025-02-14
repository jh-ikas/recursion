import sys
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QPushButton, QGroupBox, QListWidget,
    QTextEdit, QLabel, QLineEdit, QFormLayout
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from ..models.call_tree import CallTreeManager
from ..models.simulation_step import SimulationStep
from ..simulations import (
    FibonacciSimulation,
    HanoiSimulation,
    AccumulateSumSimulation,
    AccumulateProductSimulation,
    FactorialSimulation,
    BinomialCoefficientSimulation,
    GCDSimulation,
    PowerSimulation,
    PermutationSimulation,
    CombinationSimulation
)
from .animation_widget import AnimationWidget
from .styles import Styles
from ..utils.logger import Logger
from ui.components.tree_view import TreeView
from config.settings import Settings

class RecursionVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.logger.info("RecursionVisualizer 초기화 시작")
        
        self.setWindowTitle("재귀 호출 시각화 도구")
        self.resize(1200, 800)

        # 상태 관리
        self.dark_mode = False
        self.simulation_generator = None
        self.call_tree_manager = CallTreeManager()
        
        # 타이머 초기화
        self.simulation_timer = QTimer(self)
        self.simulation_timer.timeout.connect(self.process_next_step)
        
        self.log_update_timer = QTimer(self)
        self.log_update_timer.timeout.connect(self.update_log_viewer)
        
        self.layout_update_timer = QTimer(self)
        self.layout_update_timer.timeout.connect(self.update_layout)

        self.initUI()
        self._initialize_timers()
        self.applyStyles()
        self.logger.info("RecursionVisualizer 초기화 완료")

    def _initialize_timers(self):
        """타이머 초기화 및 시작"""
        self.log_update_timer.start(Settings.UI.LOG_UPDATE_INTERVAL)
        self.layout_update_timer.start(Settings.UI.LAYOUT_UPDATE_INTERVAL)

    def initUI(self):
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setSpacing(10)
        mainLayout.setContentsMargins(10, 10, 10, 10)

        # === 상단 툴바 ===
        toolBar = self.createToolBar()
        mainLayout.addWidget(toolBar)

        # === 중앙 영역 ===
        centerWidget = QWidget()
        centerLayout = QHBoxLayout(centerWidget)
        
        # 왼쪽 패널
        leftPanel = self.createLeftPanel()
        centerLayout.addWidget(leftPanel, 4)

        # 오른쪽 애니메이션 영역
        rightPanel = self.createRightPanel()
        centerLayout.addWidget(rightPanel, 6)
        
        mainLayout.addWidget(centerWidget)

        # 초기 코드 로드
        self.currentCodeLines = []
        self.loadCodeTemplate()

    def createToolBar(self) -> QWidget:
        toolBar = QWidget()
        toolBarLayout = QHBoxLayout(toolBar)
        toolBarLayout.setContentsMargins(15, 5, 15, 5)

        # 왼쪽 그룹: 알고리즘 선택
        leftGroup = QWidget()
        leftLayout = QHBoxLayout(leftGroup)
        algoLabel = QLabel("알고리즘:")
        algoLabel.setStyleSheet("font-weight: bold;")
        self.algorithmCombo = QComboBox()
        self.algorithmCombo.addItems([
            "피보나치 수열",
            "하노이 탑",
            "누적합",
            "누적곱",
            "팩토리얼",
            "이항계수",
            "최대공약수",
            "거듭제곱",
            "순열",
            "조합"
        ])
        self.algorithmCombo.setFixedWidth(200)
        self.algorithmCombo.currentIndexChanged.connect(self.loadCodeTemplate)
        leftLayout.addWidget(algoLabel)
        leftLayout.addWidget(self.algorithmCombo)
        toolBarLayout.addWidget(leftGroup)

        # 중앙 그룹: 컨트롤
        centerGroup = QWidget()
        centerLayout = QHBoxLayout(centerGroup)
        self.startButton = QPushButton("시작")
        self.pauseButton = QPushButton("일시정지")
        self.resetButton = QPushButton("리셋")
        self.darkModeButton = QPushButton("다크 모드")
        
        for btn in [self.startButton, self.pauseButton, self.resetButton, self.darkModeButton]:
            btn.setFixedWidth(100)
            centerLayout.addWidget(btn)

        self.startButton.clicked.connect(self.startSimulation)
        self.pauseButton.clicked.connect(self.pauseSimulation)
        self.resetButton.clicked.connect(self.resetSimulation)
        self.darkModeButton.clicked.connect(self.toggleDarkMode)
        
        toolBarLayout.addWidget(centerGroup)

        # 오른쪽 그룹: 속도 조절
        rightGroup = QWidget()
        rightLayout = QHBoxLayout(rightGroup)
        speedLabel = QLabel("실행 속도:")
        speedLabel.setStyleSheet("font-weight: bold;")
        self.speedSlider = QSlider(Qt.Horizontal)
        self.speedSlider.setRange(
            Settings.UI.SIMULATION_SPEED_MIN,
            Settings.UI.SIMULATION_SPEED_MAX
        )
        self.speedSlider.setValue(Settings.UI.SIMULATION_SPEED_DEFAULT)
        self.speedSlider.setFixedWidth(150)
        rightLayout.addWidget(speedLabel)
        rightLayout.addWidget(self.speedSlider)
        toolBarLayout.addWidget(rightGroup)

        return toolBar

    def createLeftPanel(self) -> QWidget:
        leftPanel = QWidget()
        leftLayout = QVBoxLayout(leftPanel)
        
        # 입력 파라미터 그룹
        paramGroup = QWidget()
        paramLayout = QFormLayout(paramGroup)
        self.paramEdit = QLineEdit("4")
        self.paramEdit.setFixedWidth(100)
        paramLayout.addRow("입력값 (n):", self.paramEdit)
        leftLayout.addWidget(paramGroup)
        
        # 코드 뷰어
        codeGroup = QGroupBox("소스 코드")
        codeLayout = QVBoxLayout(codeGroup)
        self.codeArea = QTextEdit()
        self.codeArea.setReadOnly(True)
        self.codeArea.setFont(QFont("Consolas", 12))
        codeLayout.addWidget(self.codeArea)
        leftLayout.addWidget(codeGroup)
        
        # 호출 스택
        stackGroup = QGroupBox("호출 스택")
        stackLayout = QVBoxLayout(stackGroup)
        self.callStackList = QListWidget()
        stackLayout.addWidget(self.callStackList)
        leftLayout.addWidget(stackGroup)
        
        return leftPanel

    def createRightPanel(self) -> QWidget:
        rightPanel = QWidget()
        rightLayout = QVBoxLayout(rightPanel)
        
        # 애니메이션 뷰어
        animGroup = QGroupBox("재귀 트리 시각화")
        animLayout = QVBoxLayout(animGroup)
        self.animationWidget = AnimationWidget()
        self.animationWidget.setCallTreeManager(self.call_tree_manager)
        animLayout.addWidget(self.animationWidget)
        rightLayout.addWidget(animGroup)
        
        # 로그 뷰어
        logGroup = QGroupBox("로그")
        logLayout = QVBoxLayout(logGroup)
        self.logViewer = QTextEdit()
        self.logViewer.setReadOnly(True)
        self.logViewer.setMaximumHeight(150)
        logLayout.addWidget(self.logViewer)
        rightLayout.addWidget(logGroup)
        
        # 결과 표시
        resultGroup = QWidget()
        resultLayout = QHBoxLayout(resultGroup)
        self.resultLabel = QLabel("결과: ")
        self.resultLabel.setFont(QFont("Arial", 12))
        resultLayout.addWidget(self.resultLabel)
        rightLayout.addWidget(resultGroup)
        
        return rightPanel

    def toggleDarkMode(self):
        self.dark_mode = not self.dark_mode
        self.applyStyles()
        self.animationWidget.setDarkMode(self.dark_mode)

    def applyStyles(self):
        styles = Styles.get_dark_theme() if self.dark_mode else Styles.get_light_theme()
        self.setStyleSheet(
            styles['main_window'] +
            styles['button'] +
            styles['combo_box'] +
            styles['text_edit'] +
            styles['group_box']
        )

    def loadCodeTemplate(self):
        algo = self.algorithmCombo.currentText()
        if algo == "피보나치 수열":
            code = """def fibonacci(n):
    # 기저 조건: n이 0 또는 1이면 그대로 반환
    if n <= 1:
        return n
    # 재귀 호출: 두 개의 재귀 호출을 통해 결과를 구함
    return fibonacci(n-1) + fibonacci(n-2)
"""
        elif algo == "하노이 탑":
            code = """def hanoi(n, source, target, auxiliary):
    # 기저 조건: 원판이 1개이면 바로 이동
    if n == 1:
        move_disk(source, target)
        return
    # 재귀 호출: n-1개의 원판을 보조 기둥으로 이동
    hanoi(n-1, source, auxiliary, target)
    # 재귀 호출: 가장 큰 원판 이동
    move_disk(source, target)
    # 재귀 호출: 보조 기둥의 원판을 목표 기둥으로 이동
    hanoi(n-1, auxiliary, target, source)
"""
        elif algo == "누적합":
            code = """def accumulate_sum(n):
    # 기저 조건: n이 0이면 0 반환
    if n == 0:
        return 0
    # 재귀 호출: 이전까지의 합에 현재 값을 더함
    return accumulate_sum(n-1) + n
"""
        elif algo == "누적곱":
            code = """def accumulate_product(n):
    # 기저 조건: n이 0이면 1 반환
    if n == 0:
        return 1
    # 재귀 호출: 이전까지의 곱에 현재 값을 곱함
    return accumulate_product(n-1) * n
"""
        elif algo == "팩토리얼":
            code = """def factorial(n):
    # 기저 조건: n이 0 또는 1이면 1 반환
    if n <= 1:
        return 1
    # 재귀 호출: n과 (n-1)!의 곱
    return n * factorial(n-1)
"""
        elif algo == "이항계수":
            code = """def binomial(n, k):
    # 기저 조건: k가 0이거나 n과 같으면 1
    if k == 0 or k == n:
        return 1
    # 재귀 호출: 파스칼의 삼각형 성질 이용
    return binomial(n-1, k-1) + binomial(n-1, k)
"""
        elif algo == "최대공약수":
            code = """def gcd(a, b):
    # 기저 조건: b가 0이면 a가 최대공약수
    if b == 0:
        return a
    # 재귀 호출: 유클리드 호제법
    return gcd(b, a % b)
"""
        elif algo == "거듭제곱":
            code = """def power(base, exponent):
    # 기저 조건: 지수가 0이면 1 반환
    if exponent == 0:
        return 1
    # 재귀 호출: 지수를 반으로 나누어 계산
    half = power(base, exponent // 2)
    if exponent % 2 == 0:
        return half * half
    else:
        return half * half * base
"""
        elif algo == "순열":
            code = """def permutation(elements, current=[]):
    # 기저 조건: 모든 원소를 사용했으면 현재 순열 반환
    if not elements:
        return [current]
    # 재귀 호출: 각 원소를 선택하여 순열 생성
    results = []
    for i, elem in enumerate(elements):
        remaining = elements[:i] + elements[i+1:]
        for p in permutation(remaining, current + [elem]):
            results.append(p)
    return results
"""
        else:  # 조합
            code = """def combination(elements, k, start=0, current=[]):
    # 기저 조건: k개를 모두 선택했으면 현재 조합 반환
    if len(current) == k:
        return [current]
    # 더 이상 선택할 원소가 없으면 빈 리스트 반환
    if start >= len(elements):
        return []
    # 재귀 호출: 현재 원소를 선택하거나 건너뛰기
    results = []
    for i in range(start, len(elements)):
        results.extend(combination(
            elements, k, i + 1, current + [elements[i]]
        ))
    return results
"""
        
        self.currentCodeLines = code.splitlines()
        self.showCodeWithHighlight("")

    def showCodeWithHighlight(self, keyword: str):
        highlightedText = "<div style='font-family:Consolas;'>"
        for i, line in enumerate(self.currentCodeLines, 1):
            safe_line = line.replace(' ', '&nbsp;')
            if keyword in line:
                # 키워드를 포함한 전체 라인 하이라이트
                safe_line = (
                    f"<div style='background-color: #FFE4B5'>"
                    f"<span style='color: #666'>{i:>3}</span> {safe_line}"
                    f"</div>"
                )
            else:
                safe_line = f"<span style='color: #666'>{i:>3}</span> {safe_line}"
            highlightedText += safe_line + "<br>"
        highlightedText += "</div>"
        self.codeArea.setHtml(highlightedText)

    def startSimulation(self):
        self.logger.info("시뮬레이션 시작")
        self.resetSimulation()
        algo = self.algorithmCombo.currentText()
        
        try:
            n = int(self.paramEdit.text())
            
            if algo == "피보나치 수열":
                self.simulation_generator = FibonacciSimulation.run(n)
            
            elif algo == "하노이 탑":
                self.simulation_generator = HanoiSimulation.run(n, "A", "C", "B")
            
            elif algo == "누적합":
                self.simulation_generator = AccumulateSumSimulation.run(n)
            
            elif algo == "누적곱":
                self.simulation_generator = AccumulateProductSimulation.run(n)
            
            elif algo == "팩토리얼":
                self.simulation_generator = FactorialSimulation.run(n)
            
            elif algo == "이항계수":
                k = min(n // 2, n)  # 기본값으로 n과 n//2 중 작은 값 사용
                self.simulation_generator = BinomialCoefficientSimulation.run(n, k)
            
            elif algo == "최대공약수":
                b = n // 2  # 기본값으로 n/2 사용
                self.simulation_generator = GCDSimulation.run(n, b)
            
            elif algo == "거듭제곱":
                exponent = 2  # 기본값으로 제곱 사용
                self.simulation_generator = PowerSimulation.run(n, exponent)
            
            elif algo == "순열":
                elements = list(range(1, n + 1))  # 1부터 n까지의 숫자로 순열 생성
                self.simulation_generator = PermutationSimulation.run(elements)
            
            elif algo == "조합":
                elements = list(range(1, n + 1))
                k = min(n // 2, n)  # 기본값으로 n과 n//2 중 작은 값 사용
                self.simulation_generator = CombinationSimulation.run(elements, k)

            self.simulation_timer.setInterval(self.speedSlider.value())
            self.simulation_timer.start()
            self.pauseButton.setText("일시정지")
            
        except ValueError as e:
            self.logger.error(f"입력값 오류: {str(e)}")
            self.resultLabel.setText("결과: 유효한 정수를 입력하세요.")
        except Exception as e:
            self.logger.error(f"시뮬레이션 시작 오류: {str(e)}")
            self.resultLabel.setText(f"결과: 오류 발생 - {str(e)}")
            self.simulation_timer.stop()

    def pauseSimulation(self):
        if self.simulation_timer.isActive():
            self.logger.info("시뮬레이션 일시정지")
            self.simulation_timer.stop()
            self.pauseButton.setText("재개")
        else:
            self.logger.info("시뮬레이션 재개")
            self.simulation_timer.start()
            self.pauseButton.setText("일시정지")

    def resetSimulation(self):
        self.logger.info("시뮬레이션 리셋")
        self.simulation_timer.stop()
        self.simulation_generator = None
        self.callStackList.clear()
        self.call_tree_manager = CallTreeManager()
        self.animationWidget.setCallTreeManager(self.call_tree_manager)
        self.animationWidget.setMessage("")
        self.resultLabel.setText("결과: ")
        self.showCodeWithHighlight("")
        self.pauseButton.setText("일시정지")

    def process_next_step(self):
        try:
            step = next(self.simulation_generator)
            self.handle_simulation_step(step)
        except StopIteration:
            self.logger.info("시뮬레이션 완료")
            self.simulation_generator = None
            self.simulation_timer.stop()
        except Exception as e:
            self.logger.error(f"시뮬레이션 단계 처리 오류: {str(e)}")
            self.resultLabel.setText(f"결과: 에러 발생 - {str(e)}")
            self.simulation_timer.stop()

    def handle_simulation_step(self, step: SimulationStep):
        try:
            if step.step_type == "push":
                func_name = step.details.get("function", "")
                self.callStackList.addItem(func_name)
                node_id = self.call_tree_manager.push(func_name)
                self.animationWidget.highlightNode(node_id)
                self.logger.debug(f"함수 호출 추가: {func_name}")

            elif step.step_type == "pop":
                func_name = step.details.get("function", "")
                for row in range(self.callStackList.count() - 1, -1, -1):
                    if self.callStackList.item(row).text() == func_name:
                        self.callStackList.takeItem(row)
                        break
                self.call_tree_manager.pop()
                self.logger.debug(f"함수 호출 완료: {func_name}")

            elif step.step_type == "highlight":
                keyword = step.details.get("keyword", "")
                self.showCodeWithHighlight(keyword)
                msg = step.details.get("message", "")
                self.animationWidget.setMessage(msg)
                self.logger.debug(f"코드 하이라이트: {keyword}")

            elif step.step_type == "animate":
                msg = step.details.get("message", "")
                self.animationWidget.setMessage(msg)
                self.logger.debug(f"애니메이션 메시지: {msg}")

            elif step.step_type == "result":
                result = step.details.get("result", "")
                func_name = step.details.get("function", "")
                self.resultLabel.setText(f"결과: {func_name} = {result}")
                self.logger.debug(f"결과 업데이트: {func_name} = {result}")

            self.animationWidget.update()
        except Exception as e:
            self.logger.error(f"시뮬레이션 단계 처리 중 오류: {str(e)}")
            raise

    def update_layout(self):
        """레이아웃 업데이트"""
        try:
            self.animationWidget.call_tree.update_layout(
                self.animationWidget.width(),
                self.animationWidget.height()
            )
            self.animationWidget.update()
        except Exception as e:
            self.logger.error(f"레이아웃 업데이트 실패: {str(e)}")

    def update_log_viewer(self):
        """로그 뷰어 업데이트"""
        try:
            current_text = self.logViewer.toPlainText()
            new_text = self.logger.get_logs()
            
            if current_text != new_text:
                self.logViewer.setText(new_text)
                scrollbar = self.logViewer.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                
        except Exception as e:
            self.logger.error(f"로그 뷰어 업데이트 실패: {str(e)}")

    def closeEvent(self, event):
        self.logger.info("프로그램 종료")
        self.logger.cleanup()
        super().closeEvent(event) 