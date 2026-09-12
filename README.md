# PedidosYa Market Price Tracker

A Python scraper that collects visible promotions from the PedidosYa Market Android app using ADB and UIAutomator. It calculates effective discounts, exports CSV files, and generates a summary of each run.

## Features

- Navigates between sections using the app's “Continuar a” (“Continue to”) button.
- Uses overlapping 330-pixel scrolls and retries failed UI reads.
- Extracts product names, sections, prices, promotional labels, and unit details.
- Displays promotions with effective discounts of 40% or more in the console and exports a separate CSV for discounts of 50% or more.
- Removes duplicates based on product name, current price, and promotion.
- Saves partial results if an error occurs during collection or the run is interrupted with Ctrl+C.

| Promotional label | Effective discount |
|---|---:|
| 70% OFF | 70% |
| 2do al 70% OFF (70% off the second item) | 35% when buying two items with the same base price |
| 2x1 (buy two, pay for one) | 50% |
| 3x2 (buy three, pay for two) | 33.33% |

The effective discount is interpreted from the promotional label. The difference between displayed prices is stored in a separate column and is not automatically combined with the promotion.

## Requirements

- Python 3.10 or later. No third-party Python packages are required.
- Android Platform Tools (ADB), available on PATH or configured through `ADB_PATH`.
- An Android device or emulator with ADB debugging enabled and authorized.
- PedidosYa open at **Market → Promociones → Todas las promociones**, at the beginning of the first section.

## Running the scraper

From the repository directory:

```powershell
python -m pip install -r requirements.txt
adb devices
# If multiple devices are connected, choose an ID listed by adb devices:
$env:DEVICE = "emulator-5554"
# Only needed if ADB is not on PATH:
$env:ADB_PATH = "C:\Android\platform-tools\adb.exe"
python -m src.scraper
```

On Linux/macOS, set the same variables with `export DEVICE=...` and run `python3 -m src.scraper`. A single connected device is selected automatically. If multiple devices are connected, `DEVICE` is required.

`.env.example` is a configuration reference: the program **does not load .env files automatically**. Set the environment variables in your terminal before running it.

## Local output

By default, results are saved in the repository's `outputs/` directory:

- `pedidosya_market_promos_todas_secciones.csv` — all collected promotions.
- `pedidosya_market_promos_50omas_reales.csv` — promotions with effective discounts of 50% or more.
- `pedidosya_market_resumen.txt` — run summary.

CSV files use a semicolon (`;`) delimiter and UTF-8 with BOM for easier opening in Excel. Each run overwrites these files; use a different `OUTPUT_DIR` to preserve separate runs. CSV files, databases, screenshots, XML files, and local configuration files are excluded from Git.

## Project structure

```text
src/
  scraper.py       Collection workflow
  config.py        Environment variables and defaults
  adb_utils.py     Device selection, gestures, and UI reads
  ui_parser.py     Product cards, sections, and deduplication
  promo_parser.py  Discounts and prices
  reporting.py     CSV exports and summaries
tests/             Tests that do not require a device
docs/              Operation and limitations
data/              Reserved for local data
outputs/           Local results
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Scope and limitations

The UI is interpreted using rules and coordinates from the original setup (a screen of approximately 720 × 1280 pixels). Changes to screen resolution, layout, or labels may require adjustments in `ui_parser.py`. Overlapping scrolls reduce omissions but do not guarantee full catalog coverage. The scraper only extracts recognizable promotions from cards with visible names and prices; it does not query an API or make purchases.

See [operation and configuration (in Spanish)](docs/funcionamiento.md). This is an independent project with no affiliation with PedidosYa.

## Roadmap

- [ ] Price history stored in SQLite.
- [ ] Time-stamped records by product and store.
- [ ] Analysis of promotion trends.
- [ ] Dashboard and evaluation of predictive models.

These features are not implemented yet.
