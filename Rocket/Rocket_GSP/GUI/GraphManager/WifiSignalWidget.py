import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import QTimer
from .ProgressWidget import ProgressWidget

from PyQt5.QtCore import Qt

class WifiSignalWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 레이아웃 설정
        layout = QVBoxLayout()

        # Wi-Fi 신호 강도 표시 라벨
        self.label = QLabel('Wi-Fi Signal Strength', self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Wi-Fi 신호 강도 표시 Progress Bar
        self.progressBar = ProgressWidget()
        layout.addWidget(self.progressBar)

        # Refresh 버튼
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.update_signal_strength)
        layout.addWidget(self.refresh_button)

        # 타이머 설정 (5초마다 자동 업데이트)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_signal_strength)
        self.timer.start(5000)

        # 레이아웃 적용
        self.setLayout(layout)

        # 기본 윈도우 설정
        self.setWindowTitle('Wi-Fi Signal Strength')
        self.resize(300, 100)
        self.show()

        # 초기 신호 강도 업데이트
        self.update_signal_strength()

    def update_signal_strength(self):
        # 신호 강도 가져오기 (Windows)
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
            output = result.stdout

            # 신호 강도 파싱
            for line in output.split('\n'):
                if '신호' in line:
                    # 예: Signal : 77%
                    signal_strength = int(line.split(':')[1].strip().replace('%', ''))
                    break
            else:
                signal_strength = 0  # 기본값 (신호 없음)

            # Progress Bar 업데이트
            self.progressBar.setValue(signal_strength)
            self.label.setText(f'Wi-Fi Signal Strength: {signal_strength}%')

        except Exception as e:
            print(f"Error retrieving Wi-Fi signal strength: {e}")
            self.label.setText('Error retrieving Wi-Fi signal strength')
            self.progressBar.setValue(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WifiSignalWidget()
    sys.exit(app.exec_())
