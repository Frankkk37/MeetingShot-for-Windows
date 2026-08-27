import time, threading, os
from pathlib import Path
from datetime import datetime
import mss
from PIL import Image
import cv2
import numpy as np
from dedup import create_selected_pdf

class CaptureEngine:
    def __init__(self):
        self.running=False
        self.last=None
        self.last_save=0
        self.folder=None

    def start(self):
        self.running=True
        self.folder=Path("MeetingShots")/datetime.now().strftime("%Y%m%d_%H%M%S")
        (self.folder/"raw").mkdir(parents=True, exist_ok=True)
        threading.Thread(target=self.loop, daemon=True).start()

    def stop(self):
        self.running=False

    def screenshot(self):
        with mss.mss() as s:
            mon=s.monitors[1]
            img=np.array(s.grab(mon))
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def changed(self,img):
        small=cv2.resize(img,(320,200))
        gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
        if self.last is None:
            self.last=gray
            return True
        diff=np.mean(cv2.absdiff(gray,self.last))
        self.last=gray
        return diff>8

    def save(self,img):
        count=len(list((self.folder/"raw").glob("*.png")))+1
        Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)).save(self.folder/"raw"/f"{count:04}.png")

    def loop(self):
        while self.running:
            img=self.screenshot()
            now=time.time()
            if self.changed(img) or now-self.last_save>30:
                time.sleep(1)
                self.save(img)
                self.last_save=now
            time.sleep(1)

    def create_selected_pdf(self):
        if self.folder:
            create_selected_pdf(self.folder)
