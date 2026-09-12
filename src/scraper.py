import os
import tempfile
import time
from .config import *
from .adb_utils import select_device, tap, swipe, dump_ui_fast
from .ui_parser import visible_product_cards, product_key, find_continue_anywhere, screen_signature
from .promo_parser import effective_discount_value
from .reporting import save_csv, build_summary

def main():
    print("PedidosYa Market Price Tracker")
    print("-----------------------------------------")
    print("Prioridad: NO saltarse productos.")
    print()
    print("Mejoras:")
    print("- scroll con solapamiento")
    print("- espera suficiente para renderizar")
    print("- mantiene dump ADB rápido")
    print("- pasa automáticamente entre secciones")
    print("- distingue descuento directo / segunda unidad / NxM")
    print("- descuento efectivo real")
    print("- resumen final completo")
    print()
    print("Abrí:")
    print("Market > Promociones > Todas las promociones")
    print("y dejalo al comienzo de la primera sección.")
    input("Cuando estés lista, presioná ENTER...")

    select_device()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    start_time = time.time()

    all_products = {}
    visited_sections = []
    current_section = INITIAL_SECTION
    total_scrolls = 0

    failure = None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            xml_path = os.path.join(tmp, "market.xml")

            for section_number in range(1, MAX_SECTIONS + 1):
                print()
                print("=" * 68)
                print(f"SECCIÓN {section_number}: {current_section}")
                print("=" * 68)

                if current_section in visited_sections:
                    print("La sección ya fue recorrida. Evito un bucle.")
                    break

                visited_sections.append(current_section)

                previous_signature = None
                same_screen_count = 0
                moved_to_next = False

                for scroll_number in range(1, MAX_SCROLLS_PER_SECTION + 1):
                    try:
                        dump_ui_fast(xml_path)

                    except Exception as e:
                        print()
                        print("❌ No pude obtener la UI después de varios reintentos.")
                        print(f"Detalle: {e}")
                        print("Detengo esta corrida para no repetir el mismo error cientos de veces.")
                        print("Los resultados recolectados hasta acá se conservarán.")
                        raise RuntimeError("Recorrido interrumpido por un error de ADB") from e

                    products = visible_product_cards(
                        xml_path,
                        current_section
                    )

                    new_count = 0

                    for prod in products:
                        key = product_key(prod)

                        if key not in all_products:
                            all_products[key] = prod
                            new_count += 1

                            efectivo = effective_discount_value(prod)
                            if efectivo >= MIN_PRINT_DISCOUNT:
                                print(
                                    f"🔥 {efectivo:g}% EFECTIVO | "
                                    f"{prod['producto']} | "
                                    f"{prod['promo_texto']} | "
                                    f"{prod['precio_actual']} | "
                                    f"{current_section}"
                                )

                    print(
                        f"{current_section} | "
                        f"pantalla {scroll_number} | "
                        f"+{new_count} nuevos | "
                        f"visibles completos {len(products)} | "
                        f"total {len(all_products)}"
                    )

                    continue_info = find_continue_anywhere(xml_path)

                    if continue_info:
                        next_name = continue_info["next_section"]

                        print(
                            f">>> Fin de '{current_section}' "
                            f"-> '{next_name}'"
                        )

                        tap(
                            continue_info["x"],
                            continue_info["y"]
                        )

                        time.sleep(WAIT_AFTER_SECTION_TAP)

                        current_section = next_name
                        moved_to_next = True
                        break

                    signature = screen_signature(xml_path)

                    if (
                        previous_signature is not None
                        and signature == previous_signature
                        and signature
                    ):
                        same_screen_count += 1
                    else:
                        same_screen_count = 0

                    previous_signature = signature

                    if same_screen_count >= SAME_SCREEN_LIMIT:
                        print(
                            "La pantalla parece repetida. "
                            "Busco el final con mini-scrolls..."
                        )

                        found = False

                        for _ in range(4):
                            swipe(920, 700, 230)
                            total_scrolls += 1
                            time.sleep(0.35)

                            dump_ui_fast(xml_path)

                            # También recolectamos productos en los mini-scrolls.
                            rescue_products = visible_product_cards(
                                xml_path,
                                current_section
                            )

                            for prod in rescue_products:
                                key = product_key(prod)

                                if key not in all_products:
                                    all_products[key] = prod

                                    efectivo = effective_discount_value(prod)
                                    if efectivo >= MIN_PRINT_DISCOUNT:
                                        print(
                                            f"🔥 RESCATE {efectivo:g}% EFECTIVO | "
                                            f"{prod['producto']} | "
                                            f"{prod['promo_texto']} | "
                                            f"{prod['precio_actual']} | "
                                            f"{current_section}"
                                        )

                            continue_info = find_continue_anywhere(xml_path)

                            if continue_info:
                                next_name = continue_info["next_section"]

                                print(
                                    f">>> Fin de '{current_section}' "
                                    f"-> '{next_name}'"
                                )

                                tap(
                                    continue_info["x"],
                                    continue_info["y"]
                                )

                                time.sleep(WAIT_AFTER_SECTION_TAP)

                                current_section = next_name
                                moved_to_next = True
                                found = True
                                break

                        if found:
                            break

                        print("No encontré otra sección. Final del recorrido.")
                        current_section = None
                        break

                    swipe()
                    total_scrolls += 1
                    time.sleep(WAIT_AFTER_SCROLL)

                if current_section is None:
                    break

                if not moved_to_next:
                    print("No se pudo pasar a otra sección.")
                    break

    except (Exception, KeyboardInterrupt) as exc:
        failure = exc
        print(f"Recorrido interrumpido: {exc}. Guardando resultados parciales.")

    rows = sorted(
        all_products.values(),
        key=lambda p: (
            p["seccion"].lower(),
            -effective_discount_value(p),
            p["producto"].lower()
        )
    )

    rows_50 = [
        p for p in rows
        if effective_discount_value(p) >= 50
    ]

    save_csv(OUT_ALL, rows)
    save_csv(OUT_50, rows_50)

    elapsed = time.time() - start_time

    summary = build_summary(
        rows,
        visited_sections,
        elapsed,
        total_scrolls
    )

    if failure is not None:
        summary = "RESULTADOS PARCIALES - RECORRIDO INTERRUMPIDO\n" + summary

    with open(
        OUT_SUMMARY,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(summary)

    print()
    print(summary)
    if failure is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
