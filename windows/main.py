from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from capture_engine import CaptureEngine
import sys

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = CaptureEngine()
        self.setWindowTitle("MeetingShot v0.4")
        self.label = QLabel("未开始")
        self.start = QPushButton("开始截图")
        self.stop = QPushButton("停止截图")
        self.dedup = QPushButton("生成精选PDF")
        self.start.clicked.connect(self.start_capture)
        self.stop.clicked.connect(self.stop_capture)
        self.dedup.clicked.connect(self.engine.create_selected_pdf)
        layout = QVBoxLayout()
        for x in [self.label, self.start, self.stop, self.dedup]:
            layout.addWidget(x)
        self.setLayout(layout)

    def start_capture(self):
        self.engine.start()
        self.label.setText("截图中")

    def stop_capture(self):
        self.engine.stop()
        self.label.setText("已停止")

app = QApplication(sys.argv)
w = Window()
w.show()
sys.exit(app.exec())
