from pathlib import Path
from PIL import Image
import imagehash

def create_selected_pdf(folder):
    raw=folder/"raw"
    selected=[]
    last_hash=None
    for f in sorted(raw.glob("*.png")):
        h=imagehash.phash(Image.open(f))
        if last_hash is None or abs(h-last_hash)>5:
            selected.append(f)
            last_hash=h
    out=folder/"selected"
    out.mkdir(exist_ok=True)
    imgs=[]
    for i,f in enumerate(selected,1):
        img=Image.open(f).convert("RGB")
        img.save(out/f"{i:04}.png")
        imgs.append(img)
    if imgs:
        imgs[0].save(folder/"精选会议.pdf", save_all=True, append_images=imgs[1:])
