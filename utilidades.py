import re
from datetime import datetime, date
from config import FECHA_HOY


def box(titulo: str) -> None:
    ancho = len(titulo) + 4
    print("┌" + "─"*ancho + "┐")
    print("│  " + titulo + "  │")
    print("└" + "─"*ancho + "┘")


def es_numero(cad: str) -> bool:
    if cad == "":
        return False
    return bool(re.match(r'^\d+$', cad))


def formato_fecha_valido(f: str) -> bool:
    # dd/mm/aaaa
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', f):
        return False
    try:
        dt = parse_fecha_datetime(f)
        return dt is not None
    except Exception:
        return False


def parse_fecha(f: str):
    try:
        dt = datetime.strptime(f, "%d/%m/%Y").date()
        return (dt.year, dt.month, dt.day)
    except Exception:
        return None


def parse_fecha_datetime(f: str):
    try:
        return datetime.strptime(f, "%d/%m/%Y").date()
    except Exception:
        return None


def comparar_fechas(f1: str, f2: str) -> int:
    d1 = parse_fecha_datetime(f1)
    d2 = parse_fecha_datetime(f2)
    if d1 is None or d2 is None:
        raise ValueError("Formato de fecha inválido")
    if d1 < d2:
        return -1
    if d1 > d2:
        return 1
    return 0


def leer_fecha_para_reporte() -> str:
    print(f"\nIngresar fecha para el reporte (dd/mm/aaaa)")
    f = input(f"(Dejar en blanco para usar la fecha del sistema: {FECHA_HOY}): ")
    if f == "":
        return FECHA_HOY
    if not formato_fecha_valido(f):
        print("Formato inválido. Usando fecha del sistema.")
        return FECHA_HOY
    return f


def fechas_se_solapan(f1_ent, f1_sal, f2_ent, f2_sal) -> bool:
    try:
        condicion1 = comparar_fechas(f1_ent, f2_sal) < 0
        condicion2 = comparar_fechas(f1_sal, f2_ent) > 0
        return condicion1 and condicion2
    except ValueError:
        return False


def esta_disponible_en_rango(habitacion, f_ent, f_sal) -> bool:
    for r in habitacion["reservas"]:
        if fechas_se_solapan(f_ent, f_sal, r["entrada"], r["salida"]):
            return False
    return True


def obtener_estado_en_fecha(habitacion, fecha: str) -> str:
    for r in habitacion["reservas"]:
        if (comparar_fechas(fecha, r["entrada"]) >= 0 and
                comparar_fechas(fecha, r["salida"]) < 0):
            return "Ocupada"
    return "Libre"


def leer_opcion(msg, validas):
    op = input(msg)
    for v in validas:
        if op == v:
            return op
    print("Opción inválida.")
    return None


def leer_idx_lista(msg, largo):
    cad = input(msg)
    try:
        val = int(cad)
        if val < 0 or val >= largo:
            print("Índice fuera de rango.")
            return None
        return val
    except ValueError:
        print("Debe ingresar un número entero.")
        return None


def print_tabla(headers, filas, widths):
    sep = "+"
    for w in widths:
        sep += "-" * (w + 2) + "+"
    if len(filas) == 0:
        print("No hay datos para mostrar.")
        return
    print(sep)
    linea = "|"
    for i in range(len(headers)):
        h = headers[i]
        espacio = " " * (widths[i] - len(h))
        linea += " " + h + espacio + " |"
    print(linea)
    print(sep)
    for fila in filas:
        linea = "|"
        for c in range(len(widths)):
            txt = str(fila[c])  # CORREGIDO: Convertir a string
            if len(txt) > widths[c]:
                txt = txt[0:widths[c] - 1] + "…"
            espacio = " " * (widths[c] - len(txt))
            linea += " " + txt + espacio + " |"
        print(linea)
    print(sep)
