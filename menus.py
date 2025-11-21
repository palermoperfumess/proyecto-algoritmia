
from config import FECHA_HOY
from utilidades import box, leer_opcion
from habitaciones import listar_habitaciones
from usuarios import listar_usuarios, agregar_usuario
from estadisticas import submenu_estadisticas
from reportes import submenu_reportes
from reservas import reservar_habitacion, ver_reservas, cancelar_reserva
from persistencia import guardar_datos


def mostrar_menu_principal():
    box("HOTEL (Gestión Única)")
    print(f"Fecha del sistema: {FECHA_HOY}")
    print("1) Ver habitaciones (estado de hoy)")
    print("2) Ver habitaciones LIBRES (hoy)")
    print("3) Reservar habitación")
    print("4) Ver reservas (vigentes y futuras)")
    print("5) Cancelar reserva")
    print("6) Estadísticas")
    print("7) Reportes")
    print("8) Usuarios")
    print("0) Salir")


def submenu_usuarios(usuarios):
    while True:
        box("USUARIOS")
        print("1) Listar usuarios")
        print("2) Agregar usuario")
        print("3) Volver")

        op = leer_opcion("> ", ["1", "2", "3"])
        if op is None:
            continue

        if op == "1":
            listar_usuarios(usuarios)
        elif op == "2":
            agregar_usuario(usuarios)
        elif op == "3":
            break


def ejecutar_menu_principal(habitaciones, usuarios):
    while True:
        mostrar_menu_principal()
        op = leer_opcion("> ", ["1", "2", "3", "4", "5", "6", "7", "8", "0"])

        if op is None:
            continue

        if op == "1":
            box(f"Habitaciones (Todas, estado al {FECHA_HOY})")
            listar_habitaciones(habitaciones, solo_estado=None, fecha_referencia=FECHA_HOY)
        elif op == "2":
            box(f"Habitaciones LIBRES (al {FECHA_HOY})")
            listar_habitaciones(habitaciones, solo_estado="Libre", fecha_referencia=FECHA_HOY)
        elif op == "3":
            reservar_habitacion(habitaciones, usuarios, FECHA_HOY)
            guardar_datos(habitaciones, usuarios)
        elif op == "4":
            ver_reservas(habitaciones, FECHA_HOY)
        elif op == "5":
            cancelar_reserva(habitaciones, FECHA_HOY)
            guardar_datos(habitaciones, usuarios)
        elif op == "6":
            submenu_estadisticas(habitaciones)
        elif op == "7":
            submenu_reportes(habitaciones)
        elif op == "8":
            submenu_usuarios(usuarios)
            guardar_datos(habitaciones, usuarios)
        elif op == "0":
            print("Guardando y saliendo…")
            guardar_datos(habitaciones, usuarios)
            break
