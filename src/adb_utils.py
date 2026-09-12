import subprocess
import time
import xml.etree.ElementTree as ET
from .config import ADB, DEVICE, SWIPE_START_Y, SWIPE_END_Y, SWIPE_DURATION_MS

def run_adb(*args):
    return subprocess.run(
        [ADB, "-s", DEVICE, *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        timeout=30
    )

def tap(x, y):
    run_adb("shell", "input", "tap", str(int(x)), str(int(y)))

def swipe(start_y=SWIPE_START_Y, end_y=SWIPE_END_Y, duration=SWIPE_DURATION_MS):
    run_adb(
        "shell", "input", "swipe",
        "360", str(start_y), "360", str(end_y), str(duration)
    )

def adb_state():
    """
    Devuelve el estado del emulador según ADB.
    """
    try:
        r = subprocess.run(
            [ADB, "-s", DEVICE, "get-state"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=10,
        )
        return (r.stdout or "").strip().lower()
    except Exception:
        return ""

def try_reconnect_adb():
    """
    Intenta recuperar ADB si BlueStacks/emulador quedó momentáneamente offline.
    """
    try:
        subprocess.run(
            [ADB, "-s", DEVICE, "reconnect"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=15,
        )
    except Exception:
        pass

    time.sleep(1.0)

def dump_ui_fast(local_xml):
    """
    MODO RÁPIDO:
    - Normalmente hace dump + lectura en UNA sola llamada ADB.
    - Si esa llamada falla, usa un fallback robusto con reintentos.

    Esto reduce muchísimo la cantidad de llamadas ADB por pantalla.
    """
    # Camino rápido: una única llamada.
    try:
        cmd = (
            "uiautomator dump --compressed /sdcard/market.xml >/dev/null "
            "&& cat /sdcard/market.xml"
        )

        result = subprocess.run(
            [ADB, "-s", DEVICE, "shell", cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=25,
        )

        if result.returncode == 0:
            text = result.stdout or ""
            start = text.find("<?xml")

            if start != -1:
                text = text[start:]
                ET.fromstring(text)

                with open(local_xml, "w", encoding="utf-8") as f:
                    f.write(text)

                return

    except Exception:
        pass

    # --------------------------------------------------------
    # FALLBACK ROBUSTO
    # Solo se usa si el camino rápido falla.
    # --------------------------------------------------------
    last_error = ""

    for attempt in range(1, 4):
        try:
            state = adb_state()

            if state != "device":
                print(
                    f"⚠ ADB está '{state or 'sin respuesta'}'. "
                    f"Reconectando... ({attempt}/3)"
                )
                try_reconnect_adb()

                if adb_state() != "device":
                    time.sleep(0.6)
                    continue

            dump = subprocess.run(
                [
                    ADB, "-s", DEVICE,
                    "shell", "uiautomator", "dump",
                    "--compressed", "/sdcard/market.xml"
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=25,
            )

            if dump.returncode != 0:
                last_error = (
                    (dump.stderr or "").strip()
                    or (dump.stdout or "").strip()
                    or f"uiautomator código {dump.returncode}"
                )
                time.sleep(0.5)
                continue

            cat = subprocess.run(
                [ADB, "-s", DEVICE, "shell", "cat", "/sdcard/market.xml"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=15,
            )

            if cat.returncode != 0:
                last_error = (
                    (cat.stderr or "").strip()
                    or (cat.stdout or "").strip()
                    or f"cat código {cat.returncode}"
                )
                time.sleep(0.5)
                continue

            text = cat.stdout or ""
            pos = text.find("<?xml")

            if pos == -1:
                last_error = "XML incompleto"
                time.sleep(0.5)
                continue

            text = text[pos:]
            ET.fromstring(text)

            with open(local_xml, "w", encoding="utf-8") as f:
                f.write(text)

            return

        except Exception as e:
            last_error = str(e)
            time.sleep(0.5)

    raise RuntimeError(
        "No pude obtener la UI. "
        f"Último error: {last_error}"
    )

def select_device():
    """Select one connected device, or validate the configured serial."""
    global DEVICE
    result = subprocess.run([ADB, "devices"], check=True, capture_output=True,
                            text=True, encoding="utf-8", timeout=15)
    connected = [parts[0] for line in result.stdout.splitlines()
                 if len(parts := line.split()) == 2 and parts[1] == "device"]
    if DEVICE:
        if DEVICE not in connected:
            raise RuntimeError("DEVICE no está conectado. Revisá adb devices.")
    elif len(connected) == 1:
        DEVICE = connected[0]
    else:
        raise RuntimeError("Conectá un dispositivo o configurá DEVICE si hay varios.")
    return DEVICE
