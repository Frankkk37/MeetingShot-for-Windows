import os
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

import cv2
import mss
import numpy as np
from PIL import Image

from dedup import create_selected_pdf


def meeting_root() -> Path:
    candidates = [
        Path.home() / "Pictures" / "MeetingShots",
        Path.home() / "MeetingShots",
    ]
    errors = []
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
    raise RuntimeError("无法创建截图保存目录：" + " | ".join(errors))


class CaptureEngine:
    def __init__(self):
        self.running = False
        self.last = None
        self.last_save = 0.0
        self.folder = None
        self.base_folder = None
        self.thread = None
        self.saved_count = 0
        self.last_error = None
        self.error_log_path = None

    def _write_error_log(self, context, exc):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = (
            f"[{stamp}] {context}\n"
            f"{type(exc).__name__}: {exc}\n"
            f"{traceback.format_exc()}\n"
        )
        targets = []
        if self.base_folder:
            targets.append(self.base_folder / "MeetingShot-error.log")
        targets.append(Path.home() / "MeetingShot-error.log")
        for target in targets:
            try:
                with target.open("a", encoding="utf-8") as fh:
                    fh.write(text)
                self.error_log_path = target
                break
            except Exception:
                pass

    def start(self):
        if self.running:
            return
        self.last_error = None
        self.last = None
        self.saved_count = 0
        try:
            self.base_folder = meeting_root()
            self.folder = self.base_folder / datetime.now().strftime("%Y%m%d_%H%M%S")
            (self.folder / "raw").mkdir(parents=True, exist_ok=True)

            # 同步验证截图API和写权限；失败时按钮点击会直接报出真实错误。
            first = self.screenshot()
            self.last = self.analysis_frame(first)
            self.save(first)
            self.last_save = time.time()

            self.running = True
            self.thread = threading.Thread(target=self.loop, daemon=True)
            self.thread.start()
        except Exception as exc:
            self.running = False
            self.last_error = f"启动失败：{exc}"
            self._write_error_log("start_capture", exc)
            raise RuntimeError(self.last_error) from exc

    def stop(self):
        self.running = False

    def screenshot(self):
        with mss.mss() as sct:
            if len(sct.monitors) < 2:
                raise RuntimeError("未检测到可截图显示器")
            monitor = sct.monitors[1]
            image = np.array(sct.grab(monitor))
            return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    def analysis_frame(self, image):
        small = cv2.resize(image, (320, 200))
        return cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

    def changed(self, image):
        gray = self.analysis_frame(image)
        if self.last is None:
            self.last = gray
            return True
        diff = float(np.mean(cv2.absdiff(gray, self.last)))
        self.last = gray
        return diff > 8

    def save(self, image):
        if self.folder is None:
            raise RuntimeError("截图目录尚未创建")
        self.saved_count += 1
        target = self.folder / "raw" / f"{self.saved_count:04}.png"
        Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).save(target)
        return target

    def loop(self):
        try:
            while self.running:
                image = self.screenshot()
                now = time.time()
                if self.changed(image) or now - self.last_save > 30:
                    time.sleep(1)
                    self.save(image)
                    self.last_save = now
                time.sleep(1)
        except Exception as exc:
            self.running = False
            self.last_error = f"截图失败：{exc}"
            self._write_error_log("capture_loop", exc)

    def create_selected_pdf(self):
        if not self.folder:
            raise RuntimeError("尚无可整理的截图")
        return create_selected_pdf(self.folder)
