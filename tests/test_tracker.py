import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from src import scraper
from src.promo_parser import classify_promo, ar_price_to_float
from src.reporting import build_summary


def product():
    return dict(seccion='Prueba', producto='Producto sintético', promo_texto='2x1',
                tipo_promocion='2x1', descuento_etiqueta='', descuento_efectivo=50,
                precio_actual='$ 1.000', precio_anterior='',
                descuento_calculado_precio='', ventas='', detalle_unidad='')


class TrackerTests(unittest.TestCase):
    def test_promotions(self):
        for label, expected in [('70% OFF', 70), ('2do al 70% OFF', 35),
                                ('segunda unidad al 80% OFF', 40),
                                ('2x1', 50), ('3x2', 33.33)]:
            with self.subTest(label=label):
                self.assertEqual(classify_promo(label)[2], expected)
        self.assertEqual(classify_promo('sin oferta')[2], '')
        self.assertEqual(classify_promo('2x3')[2], '')

    def test_argentine_prices(self):
        self.assertEqual(ar_price_to_float('$ 1.234,56'), 1234.56)
        self.assertIsNone(ar_price_to_float('sin precio'))

    def test_summary_lists_products(self):
        self.assertIn('Producto sintético', build_summary([product()], ['Prueba'], 1, 1))
        self.assertIn('Promociones únicas encontradas: 0', build_summary([], [], 0, 0))

    def test_partial_results_survive_adb_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            with patch.multiple(scraper, OUTPUT_DIR=output,
                                OUT_ALL=str(output / 'all.csv'),
                                OUT_50=str(output / '50.csv'),
                                OUT_SUMMARY=str(output / 'summary.txt')), \
                 patch('builtins.input', return_value=''), \
                 patch.object(scraper, 'select_device'), \
                 patch.object(scraper, 'dump_ui_fast', side_effect=[None, RuntimeError('offline')]), \
                 patch.object(scraper, 'visible_product_cards', return_value=[product()]), \
                 patch.object(scraper, 'find_continue_anywhere', return_value=None), \
                 patch.object(scraper, 'screen_signature', return_value=('screen',)), \
                 patch.object(scraper, 'swipe'), \
                 patch.object(scraper.time, 'sleep'), redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    scraper.main()
                self.assertEqual(caught.exception.code, 1)
            with (output / 'all.csv').open(encoding='utf-8-sig') as handle:
                rows = list(csv.DictReader(handle, delimiter=';'))
            self.assertEqual(rows[0]['producto'], 'Producto sintético')
            self.assertIn('RESULTADOS PARCIALES', (output / 'summary.txt').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
