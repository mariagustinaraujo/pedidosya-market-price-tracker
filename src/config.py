"""Configuration through environment variables; no personal paths."""
import os
from pathlib import Path

ADB = os.getenv("ADB_PATH", "adb")
DEVICE = os.getenv("DEVICE", "")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(Path(__file__).resolve().parents[1] / "outputs"))).expanduser()
MAX_SCROLLS_PER_SECTION = int(os.getenv("MAX_SCROLLS_PER_SECTION", "220"))
MAX_SECTIONS = int(os.getenv("MAX_SECTIONS", "60"))
SWIPE_START_Y = int(os.getenv("SWIPE_START_Y", "950"))
SWIPE_END_Y = int(os.getenv("SWIPE_END_Y", "620"))
SWIPE_DURATION_MS = 260
WAIT_AFTER_SCROLL = float(os.getenv("WAIT_AFTER_SCROLL", "0.5"))
WAIT_AFTER_SECTION_TAP = 1.2
SAME_SCREEN_LIMIT = 4
MIN_PRINT_DISCOUNT = 40
INITIAL_SECTION = os.getenv("INITIAL_SECTION", "Solo para vos")
OUT_ALL = str(OUTPUT_DIR / "pedidosya_market_promos_todas_secciones.csv")
OUT_50 = str(OUTPUT_DIR / "pedidosya_market_promos_50omas_reales.csv")
OUT_SUMMARY = str(OUTPUT_DIR / "pedidosya_market_resumen.txt")
