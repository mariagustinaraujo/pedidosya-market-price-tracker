# Funcionamiento

La base es `v7_rapido_sin_saltar`, la última variante recomendada en la conversación original. Se separó en módulos manteniendo su recorrido de promociones y sus desplazamientos solapados. Las versiones previas permanecen en la carpeta original de la usuaria; no se publican copias redundantes ni archivos con rutas personales.

## Recorrido

1. La persona abre la pantalla de promociones y confirma con Enter.
2. Se valida el dispositivo ADB y se crea la carpeta de resultados.
3. UIAutomator produce un XML temporal; se intenta una lectura rápida y luego reintentos separados si falla.
4. Se identifican tarjetas clickeables con tamaño mínimo, promoción, nombre y precio.
5. Se acumulan productos únicos y se avanza con desplazamientos solapados.
6. El botón «Continuar a» permite cambiar de sección. Pantallas repetidas activan pequeños desplazamientos de rescate.
7. Se generan ambos CSV y el resumen, también si el recorrido se interrumpe por error o Ctrl+C. En ese caso el resumen indica que es parcial y el proceso devuelve código 1.

## Configuración

| Variable | Valor por defecto | Uso |
|---|---|---|
| `ADB_PATH` | `adb` | Ejecutable ADB |
| `DEVICE` | vacío | Selección automática solo si hay un dispositivo |
| `OUTPUT_DIR` | `outputs/` del repositorio | Carpeta de resultados; una ruta relativa se resuelve desde la terminal |
| `INITIAL_SECTION` | `Solo para vos` | Nombre de la sección inicial, sin navegar hacia ella |
| `MAX_SCROLLS_PER_SECTION` | `220` | Límite de pantallas por sección |
| `MAX_SECTIONS` | `60` | Límite de secciones |
| `SWIPE_START_Y` | `950` | Inicio del gesto vertical |
| `SWIPE_END_Y` | `620` | Fin del gesto vertical |
| `WAIT_AFTER_SCROLL` | `0.5` | Espera en segundos |

Los tamaños mínimos, el eje horizontal del gesto y los límites de pantalla continúan en el código de la interfaz. La configuración portable elimina las rutas personales, pero no implica compatibilidad automática con cualquier resolución. Usar valores positivos y un gesto dentro de la pantalla.

## Interpretación de datos

`descuento_etiqueta` es el porcentaje nominal; `descuento_efectivo` representa el descuento promedio cumpliendo la cantidad de la oferta. `descuento_calculado_precio` compara los dos precios visibles. No se deben sumar estas columnas: pueden describir condiciones distintas.

La primera aparición de una combinación producto/precio/promoción determina su sección. El scraper no identifica SKU ni sucursal y no conserva historia entre corridas. Los precios se interpretan con formato argentino: punto de miles y coma decimal.

## Correcciones de consolidación

- Resumen: se utiliza la lista ordenada completa en lugar de una variable inexistente.
- Se guardan resultados parciales ante fallas de lectura, gestos o interrupción.
- Selección de dispositivo validada y tiempos máximos para las llamadas ADB.
- Rutas y parámetros principales configurables desde el entorno.

## Diagnóstico

Si no hay dispositivo, revisar `adb devices`, autorización de depuración y configuración del emulador. Si hay más de uno, configurar `DEVICE`. Un error de UI puede indicar una pantalla incorrecta o un cambio de diseño. Los límites de recorrido y la detección de pantalla repetida son heurísticos: un final sin error no certifica cobertura completa.

Las pruebas utilizan datos sintéticos y ADB simulado. Una corrida real depende de que el emulador esté abierto y ubicado en la pantalla esperada.
