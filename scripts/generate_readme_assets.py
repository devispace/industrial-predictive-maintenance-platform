import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
PHASE1 = OUTPUTS / "phase1"


def generate_shap_chart() -> None:
    with (PHASE1 / "shap_feature_importance.csv").open(encoding="utf-8", newline="") as source:
        values = [(row["feature"], float(row["mean_abs_shap"])) for row in csv.DictReader(source)]

    def clean_label(value: str) -> str:
        return value.replace("num__", "").replace("cat__Type_", "Machine type: ")

    width, height = 1530, 935
    background, foreground, muted, accent, grid = "#081116", "#edf5f3", "#91a39f", "#7ee2b8", "#23343a"
    chart = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(chart)

    font_candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]

    def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        candidate = next((path for path in font_candidates if path.exists()), None)
        return ImageFont.truetype(str(candidate), size) if candidate else ImageFont.load_default()

    title_font, label_font, value_font, foot_font = font(44), font(25), font(23), font(22)
    draw.text((70, 55), "Global SHAP feature importance", font=title_font, fill=foreground)
    draw.text((70, 118), "Balanced Random Forest · mean absolute contribution · 1,000 samples", font=foot_font, fill=muted)

    left, right, top, row_height = 430, 1460, 205, 76
    maximum = max(value for _, value in values)
    for tick in range(6):
        x = left + int((right - left) * tick / 5)
        draw.line((x, top - 10, x, top + row_height * len(values) - 20), fill=grid, width=2)
        draw.text((x - 18, top + row_height * len(values) - 4), f"{maximum * tick / 5:.2f}", font=foot_font, fill=muted)

    for index, (feature, value) in enumerate(values):
        y = top + index * row_height
        label = clean_label(feature)
        draw.text((70, y + 10), label, font=label_font, fill=foreground)
        bar_width = int((right - left) * value / maximum)
        draw.rounded_rectangle((left, y + 8, left + bar_width, y + 43), radius=12, fill=accent)
        draw.text((min(left + bar_width + 14, right - 70), y + 10), f"{value:.3f}", font=value_font, fill=foreground)

    draw.text((left, height - 50), "Mean |SHAP value|", font=foot_font, fill=muted)
    chart.save(PHASE1 / "shap_feature_importance.png", optimize=True)


def generate_demo_gif() -> None:
    frame_paths = [
        OUTPUTS / "dashboard-overview.png",
        OUTPUTS / "dashboard-prediction.png",
        OUTPUTS / "public-demo.png",
    ]
    size = (1280, 720)
    frames = []
    for path in frame_paths:
        with Image.open(path) as source:
            frame = ImageOps.fit(source.convert("RGB"), size, method=Image.Resampling.LANCZOS)
            frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=192))

    frames[0].save(
        OUTPUTS / "demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[1700, 2400, 2400],
        loop=0,
        optimize=True,
        disposal=2,
    )


if __name__ == "__main__":
    generate_shap_chart()
    generate_demo_gif()
    print("Generated SHAP chart and dashboard demo GIF.")
