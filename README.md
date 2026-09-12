# PedidosYa Market Price Tracker

Scraper en Python que recolecta promociones visibles en la aplicación Android de PedidosYa Market mediante ADB y UIAutomator. Calcula descuentos efectivos, exporta CSV y genera un resumen de cada ejecución.

## Funcionalidades

- Recorrido por secciones mediante el botón «Continuar a».
- Desplazamiento solapado de 330 píxeles y reintentos de lectura.
- Extracción de producto, sección, precios, etiqueta promocional y detalle por unidad.
- Promociones de 40% efectivo o más en la consola; CSV separado para las de 50% o más.
- Eliminación de duplicados por nombre, precio actual y promoción.
- Guardado parcial ante errores durante el recorrido o interrupción con Ctrl+C.

| Etiqueta | Descuento efectivo |
|---|---:|
| 70% OFF | 70% |
| 2do al 70% OFF | 35% al comprar dos unidades del mismo precio |
| 2x1 | 50% |
| 3x2 | 33,33% |

El descuento efectivo se interpreta desde la etiqueta. La diferencia entre precios se conserva en otra columna y no se combina automáticamente con la promoción.

## Requisitos

- Python 3.10 o posterior. No requiere paquetes de terceros.
- Android Platform Tools (ADB) instalado y disponible en PATH, o configurado con `ADB_PATH`.
- Dispositivo Android o emulador con depuración ADB habilitada y autorizada.
- PedidosYa abierto en **Market → Promociones → Todas las promociones**, al inicio de la primera sección.

## Ejecutar

Desde la carpeta del repositorio:

```powershell
python -m pip install -r requirements.txt
adb devices
# Si hay varios dispositivos, elegir el identificador que muestra adb devices:
$env:DEVICE = "emulator-5554"
# Solo si ADB no está en PATH:
$env:ADB_PATH = "C:\Android\platform-tools\adb.exe"
python -m src.scraper
```

En Linux/macOS se configuran las mismas variables con `export DEVICE=...` y se ejecuta `python3 -m src.scraper`. Si hay un único dispositivo conectado se selecciona automáticamente. Con varios, `DEVICE` es obligatorio.

`.env.example` es una referencia de configuración: el programa **no carga archivos .env automáticamente**. Exportá las variables en la terminal antes de ejecutarlo.

## Resultados locales

Por defecto se guardan en `outputs/` dentro del repositorio:

- `pedidosya_market_promos_todas_secciones.csv`
- `pedidosya_market_promos_50omas_reales.csv`
- `pedidosya_market_resumen.txt`

CSV con separador `;` y UTF-8 con BOM para facilitar su apertura en Excel. Cada ejecución reemplaza estos archivos; para conservar corridas usá un `OUTPUT_DIR` distinto. Los CSV, bases de datos, capturas, XML y configuraciones locales están excluidos de Git.

## Estructura

```text
src/
  scraper.py       Coordinación del recorrido
  config.py        Variables de entorno y valores por defecto
  adb_utils.py     Dispositivo, gestos y lectura de UI
  ui_parser.py     Tarjetas, secciones y deduplicación
  promo_parser.py  Descuentos y precios
  reporting.py     CSV y resumen
tests/             Pruebas sin dispositivo
docs/              Funcionamiento y limitaciones
data/              Reservado para datos locales
outputs/           Resultados locales
```

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

## Alcance y limitaciones

La interfaz se interpreta con reglas y coordenadas de la configuración original (pantalla de aproximadamente 720 × 1280). Cambios de resolución, diseño o etiquetas pueden requerir ajustes en `ui_parser.py`. El solapamiento reduce omisiones, pero no garantiza cubrir todo el catálogo. Solo extrae promociones reconocibles de tarjetas con nombre y precio visibles; no consulta una API ni realiza compras.

Ver [funcionamiento y configuración](docs/funcionamiento.md). Proyecto independiente, sin afiliación con PedidosYa.

## Próximos pasos

- [ ] Historial de precios en SQLite.
- [ ] Registro temporal por producto y sucursal.
- [ ] Análisis de evolución de promociones.
- [ ] Dashboard y evaluación de modelos predictivos.

Estas funciones todavía no están implementadas.
