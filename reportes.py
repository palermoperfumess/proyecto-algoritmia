
from config import FECHA_HOY
from utilidades import box, leer_fecha_para_reporte, leer_opcion
from habitaciones import listar_habitaciones
from estadisticas import reporte_general


def submenu_reportes(habs):
    while True:
        box("REPORTES")
        print("1) Reporte general")
        print("2) Ver SOLO ocupadas")
        print("3) Ver SOLO libres")
        print("4) Volver")

        op = leer_opcion("> ", ["1", "2", "3", "4"])
        if op is None:
            continue

        fecha_reporte = FECHA_HOY
        if op in ("1", "2", "3"):
            fecha_reporte = leer_fecha_para_reporte()

        if op == "1":
            reporte_general(habs, fecha_reporte)
        elif op == "2":
            listar_habitaciones(habs, solo_estado="Ocupada", fecha_referencia=fecha_reporte)
        elif op == "3":
            listar_habitaciones(habs, solo_estado="Libre", fecha_referencia=fecha_reporte)
        elif op == "4":
            break
