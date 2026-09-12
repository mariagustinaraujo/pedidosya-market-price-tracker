"""Interpretación de etiquetas y precios argentinos."""
import re

ANY_PERCENT_OFF_RE = re.compile(r"(\d+)\s*%\s*OFF", re.I)

SECOND_UNIT_RE = re.compile(
    r"(?:2\s*(?:do|da|º|°|ª)?|segunda?|segundo?)"
    r"(?:\s+unidad)?\s*(?:al|con)?\s*(\d+)\s*%\s*OFF",
    re.I
)

NXM_RE = re.compile(r"\b(\d+)\s*[xX]\s*(\d+)\b")

PRICE_RE = re.compile(r"^\$\s*[\d\.\,]+$")
SALES_RE = re.compile(r"^\+\S+\s+ventas$", re.I)

def ar_price_to_float(s):
    if not s:
        return None

    try:
        return float(
            s.replace("$", "")
             .replace(" ", "")
             .replace(".", "")
             .replace(",", ".")
        )
    except ValueError:
        return None

def classify_promo(text):
    """
    Ejemplos:
      70% OFF        -> 70% efectivo
      2do al 70% OFF -> 35% efectivo comprando 2
      2x1            -> 50% efectivo
      3x2            -> 33.33% efectivo
    """
    text = (text or "").strip()

    m = SECOND_UNIT_RE.search(text)

    if m:
        nominal = float(m.group(1))
        return "segunda_unidad", nominal, round(nominal / 2, 2)

    m = NXM_RE.search(text)

    if m:
        llevas = int(m.group(1))
        pagas = int(m.group(2))

        if llevas > 0 and 0 <= pagas < llevas:
            efectivo = round((llevas - pagas) / llevas * 100, 2)
            return f"{llevas}x{pagas}", "", efectivo

    m = ANY_PERCENT_OFF_RE.search(text)

    if m:
        nominal = float(m.group(1))
        return "descuento_directo", nominal, nominal

    return "otra", "", ""

def effective_discount_value(p):
    try:
        return float(p["descuento_efectivo"])
    except (TypeError, ValueError):
        return -1
