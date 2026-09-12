import re
import xml.etree.ElementTree as ET
from .promo_parser import ANY_PERCENT_OFF_RE, SECOND_UNIT_RE, NXM_RE, PRICE_RE, SALES_RE, classify_promo, ar_price_to_float

def parse_bounds(s):
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", s or "")
    return tuple(map(int, m.groups())) if m else None

def node_text(node):
    t = (node.attrib.get("text") or "").strip()

    if t:
        return t

    return (node.attrib.get("content-desc") or "").strip()

def all_texts(node):
    out = []

    for d in node.iter("node"):
        t = (d.attrib.get("text") or "").strip()
        if t:
            out.append(t)

        cd = (d.attrib.get("content-desc") or "").strip()

        if cd and cd.startswith("$"):
            out.append(cd)

    return out

def visible_product_cards(xml_path, section_name):
    root = ET.parse(xml_path).getroot()
    products = []

    for node in root.iter("node"):
        if node.attrib.get("clickable") != "true":
            continue

        bounds = parse_bounds(node.attrib.get("bounds"))

        if not bounds:
            continue

        x1, y1, x2, y2 = bounds

        # Tarjeta de producto suficientemente grande.
        if (x2 - x1) < 250 or (y2 - y1) < 180:
            continue

        texts = all_texts(node)

        promo_text = next(
            (
                t for t in texts
                if ANY_PERCENT_OFF_RE.search(t) or NXM_RE.search(t)
            ),
            None
        )

        if not promo_text:
            continue

        tipo_promo, descuento_etiqueta, descuento_efectivo = classify_promo(
            promo_text
        )

        sales = next((t for t in texts if SALES_RE.match(t)), "")
        prices = [t for t in texts if PRICE_RE.match(t)]

        current_price_text = prices[0] if prices else ""
        old_price_text = prices[1] if len(prices) > 1 else ""

        unit_text = next(
            (t for t in texts if "·" in t and "$" in t),
            ""
        )

        excluded = {
            promo_text,
            sales,
            "Aprox",
            current_price_text,
            old_price_text,
            unit_text,
            ""
        }

        candidates = []

        for t in texts:
            if t in excluded:
                continue

            if PRICE_RE.match(t):
                continue

            if SALES_RE.match(t):
                continue

            if ANY_PERCENT_OFF_RE.search(t) or NXM_RE.search(t):
                continue

            if t.lower() in {"agregar", "quitar"}:
                continue

            if t.lower().startswith("continuar a"):
                continue

            candidates.append(t)

        name = candidates[0] if candidates else ""

        # Si la tarjeta está cortada, no adivinamos.
        # Como V7 hace scroll solapado, debería aparecer completa después.
        if not name or not current_price_text:
            continue

        current = ar_price_to_float(current_price_text)
        old = ar_price_to_float(old_price_text)

        calc_discount = ""

        if current is not None and old not in (None, 0):
            calc_discount = round((1 - current / old) * 100, 2)

        products.append({
            "seccion": section_name,
            "producto": name,
            "promo_texto": promo_text,
            "tipo_promocion": tipo_promo,
            "descuento_etiqueta": descuento_etiqueta,
            "descuento_efectivo": descuento_efectivo,
            "precio_actual": current_price_text,
            "precio_anterior": old_price_text,
            "descuento_calculado_precio": calc_discount,
            "ventas": sales,
            "detalle_unidad": unit_text,
        })

    return products

def screen_signature(xml_path):
    root = ET.parse(xml_path).getroot()

    body = None

    for node in root.iter("node"):
        if node.attrib.get("resource-id") == "bodyColumn":
            body = node
            break

    if body is None:
        return ()

    sig = []

    for d in body.iter("node"):
        t = (d.attrib.get("text") or "").strip()
        b = parse_bounds(d.attrib.get("bounds"))

        if not t or not b:
            continue

        x1, y1, x2, y2 = b

        if y2 <= 1117:
            sig.append((t, x1, y1, x2, y2))

    return tuple(sig)

def find_continue_anywhere(xml_path):
    root = ET.parse(xml_path).getroot()
    nodes = list(root.iter("node"))
    continue_nodes = []

    for node in nodes:
        t = node_text(node)

        if t.lower().startswith("continuar a"):
            b = parse_bounds(node.attrib.get("bounds"))

            if b:
                continue_nodes.append((node, t, b))

    if not continue_nodes:
        return None

    continue_nodes.sort(key=lambda item: item[2][1], reverse=True)

    node, t, b = continue_nodes[0]
    x1, y1, x2, y2 = b

    next_section = re.sub(
        r"^\s*continuar a\s*",
        "",
        t,
        flags=re.I
    ).strip()

    if not next_section:
        nearby = []

        for other in nodes:
            if other is node:
                continue

            ot = node_text(other)
            ob = parse_bounds(other.attrib.get("bounds"))

            if not ot or not ob:
                continue

            ox1, oy1, ox2, oy2 = ob

            if abs(oy1 - y1) <= 95 or (y1 <= oy1 <= y2 + 95):
                low = ot.lower()

                if (
                    low != "continuar a"
                    and not PRICE_RE.match(ot)
                    and not ANY_PERCENT_OFF_RE.search(ot)
                    and not NXM_RE.search(ot)
                    and "ventas" not in low
                    and len(ot) > 2
                ):
                    nearby.append((abs(oy1 - y1), ot))

        if nearby:
            nearby.sort(key=lambda x: x[0])
            next_section = nearby[0][1].strip()

    return {
        "x": 360,
        "y": max(80, min(1100, (y1 + y2) // 2 + 18)),
        "next_section": next_section or "Siguiente sección",
    }

def product_key(p):
    return (
        re.sub(r"\s+", " ", p["producto"].strip().lower()),
        p["precio_actual"],
        p["promo_texto"].lower(),
    )
