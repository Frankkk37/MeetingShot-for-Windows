import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QMessageBox
)

from capture_engine import CaptureEngine


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = CaptureEngine()
        self.setWindowTitle("MeetingShot v0.4.1")
        self.resize(430, 280)

        self.title = QLabel("MeetingShot")
        self.title.setStyleSheet("font-size: 24px; font-weight: 700;")
        self.status = QLabel("● 尚未开始")
        self.detail = QLabel("点击“开始截图”后会先验证截图权限和保存目录。")
        self.detail.setWordWrap(True)

        self.start_btn = QPushButton("开始截图")
        self.stop_btn = QPushButton("停止截图")
        self.open_btn = QPushButton("打开文件夹")
        self.pdf_btn = QPushButton("生成精选PDF")

        self.stop_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.pdf_btn.setEnabled(False)

        self.start_btn.clicked.connect(self.start_capture)
        self.stop_btn.clicked.connect(self.stop_capture)
        self.open_btn.clicked.connect(self.open_folder)
        self.pdf_btn.clicked.connect(self.create_pdf)

        layout = QVBoxLayout()
        for widget in [
            self.title, self.status, self.detail,
            self.start_btn, self.stop_btn,
            self.open_btn, self.pdf_btn
        ]:
            layout.addWidget(widget)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(1000)

    def start_capture(self):
        self.start_btn.setEnabled(False)
        self.status.setText("● 正在启动…")
        QApplication.processEvents()

        try:
            self.engine.start()
        except Exception as exc:
            self.start_btn.setEnabled(True)
            self.status.setText("● 启动失败")
            self.detail.setText(str(exc))
            log = ""
            if self.engine.error_log_path:
                log = f"\n\n错误日志：\n{self.engine.error_log_path}"
            QMessageBox.critical(self, "MeetingShot 启动失败", f"{exc}{log}")
            return

        self.status.setText("● 正在截图 · 已保存 1 张")
        self.detail.setText(f"保存位置：{self.engine.folder}")
        self.stop_btn.setEnabled(True)
        self.open_btn.setEnabled(True)

    def stop_capture(self):
        self.engine.stop()
        self.status.setText(f"● 已停止 · 已保存 {self.engine.saved_count} 张")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pdf_btn.setEnabled(self.engine.saved_count > 0)

    def refresh_status(self):
        if self.engine.last_error:
            self.status.setText("● 截图异常")
            text = self.engine.last_error
            if self.engine.error_log_path:
                text += f"\n错误日志：{self.engine.error_log_path}"
            self.detail.setText(text)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        elif self.engine.running:
            self.status.setText(f"● 正在截图 · 已保存 {self.engine.saved_count} 张")

    def open_folder(self):
        folder = self.engine.folder or self.engine.base_folder
        if folder:
            os.startfile(str(folder))

    def create_pdf(self):
        try:
            target = self.engine.create_selected_pdf()
            QMessageBox.information(self, "完成", f"精选PDF已生成：\n{target}")
        except Exception as exc:
            QMessageBox.critical(self, "生成失败", str(exc))


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
