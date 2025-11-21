
from config import FECHA_HOY
from utilidades import box, formato_fecha_valido, comparar_fechas, esta_disponible_en_rango, leer_idx_lista
from usuarios import seleccionar_usuario
from habitaciones import listar_habitaciones, buscar_hab_por_codigo


def reservar_habitacion(habs, usuarios, fecha_actual=FECHA_HOY):
    box("Reservar habitación")

    usuario = seleccionar_usuario(usuarios)
    if usuario is None:
        print("Operación cancelada.")
        return

    try:
        cant_txt = input("¿Cuántas personas? ")
        cantidad_personas = int(cant_txt)
        if cantidad_personas <= 0:
            print("La cantidad debe ser mayor que 0.")
            return
    except ValueError:
        print("Cantidad inválida. Debe ser un número.")
        return

    while True:
        f_ent = input(f"Fecha de ENTRADA (dd/mm/aaaa, desde {fecha_actual}): ").strip()
        if not formato_fecha_valido(f_ent):
            print("Formato inválido.")
        elif comparar_fechas(f_ent, fecha_actual) < 0:
            print("Las reservas no pueden ser en el pasado.")
        else:
            break

    while True:
        f_sal = input("Fecha de SALIDA (dd/mm/aaaa): ").strip()
        if not formato_fecha_valido(f_sal):
            print("Formato inválido.")
        elif comparar_fechas(f_sal, f_ent) <= 0:
            print("La salida debe ser posterior a la entrada.")
        else:
            break

    print("\nTipos: 1-Single | 2-Doble | 3-Suite")
    tipo_op = input("Seleccione tipo (1/2/3): ")
    if tipo_op == "1":
        tipo_sel = "Single"
    elif tipo_op == "2":
        tipo_sel = "Doble"
    elif tipo_op == "3":
        tipo_sel = "Suite"
    else:
        print("Tipo inválido.")
        return

    try:
        amb_txt = input("Ambientes (1/2/3): ")
        if amb_txt not in ("1", "2", "3"):
            raise ValueError("Valor no está en (1,2,3)")
        ambientes_req = int(amb_txt)
    except ValueError:
        print("Valor de ambientes inválido.")
        return

    habs_criterios = list(filter(
        lambda h: (h["tipo"] == tipo_sel and
                   h["ambientes"] == ambientes_req and
                   h["capacidad"] >= cantidad_personas),
        habs
    ))

    disponibles = list(filter(
        lambda h: esta_disponible_en_rango(h, f_ent, f_sal),
        habs_criterios
    ))

    if len(disponibles) == 0:
        print("No hay habitaciones disponibles con esos criterios.")
        return

    print("\nHabitaciones disponibles para tu búsqueda:")
    listar_habitaciones(disponibles, solo_estado=None, fecha_referencia=FECHA_HOY)

    codigo = input("Ingrese CÓDIGO de habitación (ej H005): ").strip().upper()
    hab = None
    for h in disponibles:
        if h["codigo"].upper() == codigo:
            hab = h
            break

    if hab is None:
        print("Código inválido para la selección actual.")
        return

    print("\nForma de pago: 1-Efectivo | 2-Tarjeta | 3-MercadoPago")
    pago_op = input("Seleccione (1/2/3): ")
    if pago_op == "1":
        forma_pago = "Efectivo"
    elif pago_op == "2":
        forma_pago = "Tarjeta"
    elif pago_op == "3":
        forma_pago = "MercadoPago"
    else:
        print("Opción de pago inválida.")
        return

    reserva = {
        "usuario_id": usuario["id"], "usuario_nombre": usuario["nombre"],
        "entrada": f_ent, "salida": f_sal, "precio_noche": hab["precio"],
        "personas": cantidad_personas, "tipo": tipo_sel,
        "ambientes": ambientes_req, "pago": forma_pago
    }

    hab["reservas"].append(reserva)

    box("Reserva confirmada")
    print(f"Hab: {hab['codigo']} | {hab['tipo']} - {hab['ambientes']} amb.")
    print(f"Cliente: {usuario['nombre']} (DNI {usuario['dni']})")
    print(f"Personas: {cantidad_personas}")
    print(f"Estadía: {f_ent} → {f_sal}")
    print(f"Pago: {forma_pago}")


def ver_reservas(habs, fecha_actual=FECHA_HOY):
    box("Reservas vigentes y futuras")
    filas = []

    from utilidades import comparar_fechas  # evitar dependencia circular en módulo

    for h in habs:
        for r in h["reservas"]:
            if comparar_fechas(r["salida"], fecha_actual) > 0:
                filas.append([
                    h["codigo"], r["usuario_nombre"],
                    r["entrada"] + " a " + r["salida"]
                ])

    if len(filas) == 0:
        print("No hay reservas.")
    else:
        from utilidades import print_tabla
        print_tabla(["Hab.", "Cliente", "Fechas"], filas, [6, 20, 23])


def cancelar_reserva(habs, fecha_actual=FECHA_HOY):
    from utilidades import comparar_fechas
    from utilidades import leer_idx_lista
    box("Cancelar reserva")
    print(f"Mostrando habitaciones ocupadas al día de hoy ({fecha_actual}):")
    from habitaciones import listar_habitaciones
    listar_habitaciones(habs, solo_estado="Ocupada", fecha_referencia=fecha_actual)

    cod = input("Código de habitación a cancelar: ").strip().upper()
    from habitaciones import buscar_hab_por_codigo
    h = buscar_hab_por_codigo(habs, cod)

    if h is None:
        print("Código inexistente.")
        return

    reserva_activa_hoy = None
    for r in h["reservas"]:
        if (comparar_fechas(fecha_actual, r["entrada"]) >= 0 and
                comparar_fechas(fecha_actual, r["salida"]) < 0):
            reserva_activa_hoy = r
            break

    if reserva_activa_hoy is not None:
        print(f"Cancelando reserva activa de {reserva_activa_hoy['usuario_nombre']}...")
        h["reservas"].remove(reserva_activa_hoy)
        print("Reserva cancelada para", cod)
        return

    reservas_futuras = list(filter(
        lambda r: comparar_fechas(r["entrada"], fecha_actual) >= 0,
        h["reservas"]
    ))

    if len(reservas_futuras) > 0:
        print(f"La Hab. {cod} no tiene reservas activas hoy. Tiene las siguientes reservas futuras:")
        for i in range(len(reservas_futuras)):
            r = reservas_futuras[i]
            print(f"  {i}) {r['entrada']} a {r['salida']} (Cliente: {r['usuario_nombre']})")

        idx = leer_idx_lista(f"Ingrese Nro de reserva futura a cancelar (0-{len(reservas_futuras)-1}): ",
                             len(reservas_futuras))

        if idx is not None:
            reserva_a_cancelar = reservas_futuras[idx]
            h["reservas"].remove(reserva_a_cancelar)
            print("Reserva futura cancelada.")
            return

    print("No se encontró reserva activa o futura para cancelar.")
