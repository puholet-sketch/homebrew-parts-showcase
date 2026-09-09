"""White-out baked-in fact bars at the bottom of SKU PNGs."""
from pathlib import Path

from PIL import Image, ImageDraw

IMG_DIR = Path(__file__).resolve().parents[1] / "assets" / "img"
RENDERS = Path(r"D:\projects\стартап\ideas\renders\partner-sku-top20")


def clean(path: Path) -> None:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if w != h:
        side = max(w, h)
        canvas = Image.new("RGB", (side, side), (255, 255, 255))
        canvas.paste(im, ((side - w) // 2, (side - h) // 2))
        im = canvas
        w, h = im.size
    draw = ImageDraw.Draw(im)
    y0 = int(h * 0.78)
    draw.rectangle([0, y0, w, h], fill=(255, 255, 255))
    im.save(path, format="PNG", optimize=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    im.save(RENDERS / path.name, format="PNG", optimize=True)
    print(f"{path.name} {w}x{h}")


def main() -> None:
    files = sorted(IMG_DIR.glob("sku-*.png"))
    for p in files:
        clean(p)
    print(f"cleaned={len(files)}")


if __name__ == "__main__":
    main()
