import csv
from collections import Counter
from datetime import datetime
from .config import OUT_ALL, OUT_50, OUT_SUMMARY
from .promo_parser import effective_discount_value

def save_csv(path, rows):
    fields = [
        "seccion",
        "producto",
        "promo_texto",
        "tipo_promocion",
        "descuento_etiqueta",
        "descuento_efectivo",
        "precio_actual",
        "precio_anterior",
        "descuento_calculado_precio",
        "ventas",
        "detalle_unidad",
    ]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(
            f,
            fieldnames=fields,
            delimiter=";"
        )

        w.writeheader()
        w.writerows(rows)

def build_summary(rows, visited_sections, elapsed_seconds, total_scrolls):
    direct = [
        p for p in rows
        if p["tipo_promocion"] == "descuento_directo"
    ]

    second = [
        p for p in rows
        if p["tipo_promocion"] == "segunda_unidad"
    ]

    nxm = [
        p for p in rows
        if "x" in p["tipo_promocion"]
        and p["tipo_promocion"] != "descuento_directo"
    ]

    ge50 = [p for p in rows if effective_discount_value(p) >= 50]
    ge70 = [p for p in rows if effective_discount_value(p) >= 70]
    ge80 = [p for p in rows if effective_discount_value(p) >= 80]

    per_section = Counter(p["seccion"] for p in rows)

    todos_ordenados = sorted(
        rows,
        key=lambda p: (
            -effective_discount_value(p),
            p["producto"].lower()
        )
    )

    mins = int(elapsed_seconds // 60)
    secs = int(elapsed_seconds % 60)

    lines = []

    lines.append("=" * 76)
    lines.append("RESUMEN FINAL - PEDIDOSYA MARKET")
    lines.append("=" * 76)
    lines.append(f"Fecha/hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lines.append(f"Duración: {mins} min {secs} s")
    lines.append(f"Secciones recorridas: {len(visited_sections)}")
    lines.append(f"Scrolls realizados: {total_scrolls}")
    lines.append(f"Promociones únicas encontradas: {len(rows)}")
    lines.append("")

    lines.append("TIPOS DE PROMOCIÓN")
    lines.append("-" * 76)
    lines.append(f"Descuento directo: {len(direct)}")
    lines.append(f"Segunda unidad:    {len(second)}")
    lines.append(f"Promos NxM:        {len(nxm)}")
    lines.append("")

    lines.append("PROMOCIONES FUERTES - DESCUENTO EFECTIVO")
    lines.append("-" * 76)
    lines.append(f"50% o más: {len(ge50)}")
    lines.append(f"70% o más: {len(ge70)}")
    lines.append(f"80% o más: {len(ge80)}")
    lines.append("")

    lines.append("POR SECCIÓN")
    lines.append("-" * 76)

    for section in visited_sections:
        lines.append(
            f"{section}: {per_section.get(section, 0)}"
        )

    lines.append("")
    lines.append("TODAS LAS PROMOCIONES ENCONTRADAS")
    lines.append("-" * 76)

    for i, p in enumerate(todos_ordenados, start=1):
        lines.append(
            f"{i:>2}. "
            f"{effective_discount_value(p):>6.2f}% | "
            f"{p['producto']} | "
            f"{p['promo_texto']} | "
            f"{p['seccion']}"
        )

    lines.append("")
    lines.append("ARCHIVOS")
    lines.append("-" * 76)
    lines.append(OUT_ALL)
    lines.append(OUT_50)
    lines.append(OUT_SUMMARY)
    lines.append("=" * 76)

    return "\n".join(lines)
