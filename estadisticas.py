
from datetime import date
from functools import reduce

from config import FECHA_HOY
from utilidades import box, obtener_estado_en_fecha, comparar_fechas, parse_fecha_datetime, es_numero
from utilidades import print_tabla
from utilidades import leer_fecha_para_reporte


def contar_reservas_recursivo(habitaciones, indice=0):
    if indice >= len(habitaciones):
        return 0
    return len(habitaciones[indice]["reservas"]) + contar_reservas_recursivo(habitaciones, indice + 1)


def generar_matriz_ocupacion(habitaciones, anio, mes):
    try:
        primero = date(anio, mes, 1)
    except ValueError:
        raise ValueError("Mes o año inválidos")

    if mes == 12:
        primero_sig = date(anio + 1, 1, 1)
    else:
        primero_sig = date(anio, mes + 1, 1)
    cant_dias = (primero_sig - primero).days

    codigos = [h["codigo"] for h in habitaciones]

    matriz = [
        [
            ("O" if obtener_estado_en_fecha(h, f"{d:02d}/{mes:02d}/{anio}") == "Ocupada" else "L")
            for d in range(1, cant_dias + 1)
        ]
        for h in habitaciones
    ]

    return codigos, matriz


def mostrar_matriz_ocupacion(habitaciones, anio, mes):
    if not habitaciones:
        print("No hay habitaciones para mostrar.")
        return
    try:
        codigos, matriz = generar_matriz_ocupacion(habitaciones, anio, mes)
    except ValueError as e:
        print(str(e))
        return

    cant_dias = len(matriz[0]) if matriz else 0
    if cant_dias == 0:
        print("No hay días para mostrar.")
        return

    box(f"Ocupación {mes:02d}/{anio} (L=Libre, O=Ocupada)")

    encabezado = "Hab\\Día "
    for d in range(1, cant_dias + 1):
        encabezado += f"{d:02d} "
    print(encabezado)

    for i, codigo in enumerate(codigos):
        fila_str = f"{codigo:>6} "
        for estado in matriz[i]:
            fila_str += f" {estado} "
        print(fila_str)


def resumen_general(habs, fecha_actual=FECHA_HOY):
    total = len(habs)
    if total == 0:
        print("No hay habitaciones.")
        return

    libres_lista = list(filter(
        lambda h: obtener_estado_en_fecha(h, fecha_actual) == "Libre",
        habs
    ))
    libres = len(libres_lista)
    ocup = total - libres

    total_reservas = contar_reservas_recursivo(habs)

    tipos = {h["tipo"] for h in habs}
    formas_pago = {r["pago"] for h in habs for r in h["reservas"]}

    box(f"Resumen (al {fecha_actual})")
    print("Total habitaciones:", total)
    print(f"Libres: {libres} ({round((libres * 100) / total)}%)")
    print(f"Ocupadas: {ocup} ({round((ocup * 100) / total)}%)")
    print("Total de reservas (cálculo recursivo):", total_reservas)
    print("Tipos de habitación:", ", ".join(sorted(tipos)) if tipos else "(ninguno)")
    if formas_pago:
        print("Formas de pago registradas:", ", ".join(sorted(formas_pago)))
    else:
        print("Formas de pago registradas: (ninguna aún)")


def ocupacion(habs, fecha_actual=FECHA_HOY):
    from habitaciones import listar_habitaciones
    box(f"Ocupación (al {fecha_actual})")
    print("- Ocupadas:")
    listar_habitaciones(habs, solo_estado="Ocupada", fecha_referencia=fecha_actual)
    print("\n- Libres:")
    listar_habitaciones(habs, solo_estado="Libre", fecha_referencia=fecha_actual)


def reporte_general(habs, fecha_actual=FECHA_HOY):
    box(f"Reporte general (al {fecha_actual})")
    filas = []

    for h in habs:
        estado = obtener_estado_en_fecha(h, fecha_actual)
        fechas = "-"

        if estado == "Ocupada":
            for r in h["reservas"]:
                if (comparar_fechas(fecha_actual, r["entrada"]) >= 0 and
                        comparar_fechas(fecha_actual, r["salida"]) < 0):
                    fechas = r["entrada"] + " a " + r["salida"]
                    break
        filas.append([h["codigo"], h["tipo"], estado, fechas])

    print_tabla(["Hab.", "Tipo", "Estado", "Fechas (si aplica)"], filas, [6, 8, 8, 23])


def calcular_recaudacion_total(habs):
    box("Recaudación Total (Reservas Futuras)")

    reservas_totales = []
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

    if not reservas_futuras:
        print("No hay reservas futuras para calcular la recaudación.")
        return

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

    total_recaudado = reduce(
        lambda total, importe: total + importe,
        lista_de_importes,
        0
    )

    print(f"Total de {len(lista_de_importes)} reservas futuras encontradas.")
    print(f"Recaudación total (real): ${total_recaudado:,.0f}")
    print("(Se ha calculado precio_noche * noches por reserva)")


def submenu_estadisticas(habs):
    while True:
        box("ESTADÍSTICAS")
        print("1) Resumen general")
        print("2) Ocupación (listas)")
        print("3) Recaudación total (ejemplo reduce)")
        print("4) Calendario de ocupación (matriz)")
        print("5) Volver")

        from utilidades import leer_opcion
        op = leer_opcion("> ", ["1", "2", "3", "4", "5"])
        if op is None:
            continue

        fecha_reporte = FECHA_HOY
        if op == "1" or op == "2":
            fecha_reporte = leer_fecha_para_reporte()

        if op == "1":
            resumen_general(habs, fecha_reporte)
        elif op == "2":
            ocupacion(habs, fecha_reporte)
        elif op == "3":
            calcular_recaudacion_total(habs)
        elif op == "4":
            anio_txt = input("Año para el calendario (ej 2025): ").strip()
            mes_txt = input("Mes para el calendario (1-12): ").strip()
            if not (es_numero(anio_txt) and es_numero(mes_txt)):
                print("Debe ingresar números válidos para año y mes.")
                continue
            anio = int(anio_txt)
            mes = int(mes_txt)
            if mes < 1 or mes > 12:
                print("El mes debe estar entre 1 y 12.")
                continue
            mostrar_matriz_ocupacion(habs, anio, mes)
        elif op == "5":
            break
