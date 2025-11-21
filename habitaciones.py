
from config import FECHA_HOY
from utilidades import obtener_estado_en_fecha, print_tabla


def buscar_hab_por_codigo(habs, codigo):
    codigo = codigo.strip().upper()
    for h in habs:
        if h["codigo"].upper() == codigo:
            return h
    return None


def listar_habitaciones(habs, solo_estado=None, fecha_referencia=FECHA_HOY):
    habs_filtradas = habs
    if solo_estado is not None:
        habs_filtradas = list(filter(
            lambda h: obtener_estado_en_fecha(h, fecha_referencia) == solo_estado,
            habs
        ))

    def mapear_fila(h):
        estado_actual = obtener_estado_en_fecha(h, fecha_referencia)
        return [
            h["codigo"], h["tipo"], str(h["ambientes"]),
            str(h["capacidad"]), "$" + str(h["precio"]), estado_actual
        ]

    filas = list(map(mapear_fila, habs_filtradas))

    if len(filas) == 0:
        print("No hay habitaciones para mostrar.")
        return
    print_tabla(
        ["Código", "Tipo", "Amb.", "Cap.", "Precio", "Estado"],
        filas,
        [7, 8, 4, 4, 10, 8]
    )
