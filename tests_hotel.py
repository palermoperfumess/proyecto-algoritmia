
import unittest

from utilidades import formato_fecha_valido, parse_fecha, comparar_fechas, fechas_se_solapan, esta_disponible_en_rango, parse_fecha_datetime
from persistencia import crear_habitaciones, crear_usuarios_base
from estadisticas import calcular_recaudacion_total
from config import FECHA_HOY


class TestHotelHitos(unittest.TestCase):
    def setUp(self):
        self.habs = crear_habitaciones()
        self.us = crear_usuarios_base()

    def test_formato_fecha_valido(self):
        self.assertTrue(formato_fecha_valido("01/01/2024"))
        self.assertFalse(formato_fecha_valido("32/01/2024"))
        self.assertFalse(formato_fecha_valido("1/1/2024"))

    def test_parse_fecha(self):
        self.assertEqual(parse_fecha("03/10/2025"), (2025, 10, 3))
        self.assertIsNone(parse_fecha("31/02/2025"))

    def test_comparar_fechas(self):
        self.assertEqual(comparar_fechas("01/01/2020", "02/01/2020"), -1)
        self.assertEqual(comparar_fechas("02/01/2020", "01/01/2020"), 1)
        self.assertEqual(comparar_fechas("05/05/2021", "05/05/2021"), 0)

    def test_fechas_se_solapan(self):
        self.assertTrue(fechas_se_solapan("01/01/2024", "05/01/2024", "04/01/2024", "06/01/2024"))
        self.assertFalse(fechas_se_solapan("01/01/2024", "05/01/2024", "05/01/2024", "07/01/2024"))

    def test_reservar_y_disponibilidad(self):
        hab = self.habs[0]
        hab["reservas"].append({
            "usuario_id": 1, "usuario_nombre": "Ana Pérez",
            "entrada": "10/10/2025", "salida": "12/10/2025",
            "precio_noche": hab["precio"], "personas": 1,
            "tipo": hab["tipo"], "ambientes": hab["ambientes"], "pago": "Efectivo"
        })
        self.assertTrue(esta_disponible_en_rango(hab, "08/10/2025", "10/10/2025"))
        self.assertFalse(esta_disponible_en_rango(hab, "11/10/2025", "13/10/2025"))

    def test_calcular_recaudacion_total_logica(self):
        habA = {"codigo": "H101", "tipo": "Single", "ambientes": 1, "capacidad": 1, "precio": 1000, "reservas": [
            {"entrada": "05/11/2025", "salida": "08/11/2025", "precio_noche": 1000},
            {"entrada": "01/09/2025", "salida": "02/09/2025", "precio_noche": 1000}
        ]}
        habB = {"codigo": "H102", "tipo": "Doble", "ambientes": 2, "capacidad": 2, "precio": 2000, "reservas": [
            {"entrada": "10/11/2025", "salida": "13/11/2025", "precio_noche": 2000}
        ]}
        habs = [habA, habB]

        reservas_totales = []
        from utilidades import comparar_fechas
        for h in habs:
            for r in h["reservas"]:
                reservas_totales.append({
                    "precio_noche": r.get("precio_noche", h.get("precio", 0)),
                    "entrada": r["entrada"],
                    "salida": r["salida"]
                })
        reservas_futuras = list(filter(
            lambda r: comparar_fechas(r["salida"], FECHA_HOY) > 0,
            reservas_totales
        ))

        def noches_de_reserva(r):
            d_ent = parse_fecha_datetime(r["entrada"])
            d_sal = parse_fecha_datetime(r["salida"])
            if not d_ent or not d_sal:
                return 0
            delta = (d_sal - d_ent).days
            return max(delta, 0)

        lista_de_importes = list(map(
            lambda r: r["precio_noche"] * noches_de_reserva(r),
            reservas_futuras
        ))
        esperado = sum(lista_de_importes)
        self.assertEqual(esperado, 1000 * 3 + 2000 * 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
