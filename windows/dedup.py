from PIL import Image
import imagehash


def create_selected_pdf(folder):
    raw = folder / "raw"
    selected = []
    last_hash = None

    for file in sorted(raw.glob("*.png")):
        with Image.open(file) as source:
            current_hash = imagehash.phash(source)
        if last_hash is None or abs(current_hash - last_hash) > 5:
            selected.append(file)
            last_hash = current_hash

    out = folder / "selected"
    out.mkdir(exist_ok=True)

    images = []
    for index, file in enumerate(selected, 1):
        with Image.open(file) as source:
            image = source.convert("RGB")
            image.save(out / f"{index:04}.png")
            images.append(image.copy())

    if not images:
        raise RuntimeError("没有可用于生成PDF的截图")

    target = folder / "精选会议.pdf"
    images[0].save(target, save_all=True, append_images=images[1:])
    return target
