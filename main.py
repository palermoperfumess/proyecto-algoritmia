
from persistencia import cargar_datos
from menus import ejecutar_menu_principal


def main():
    habitaciones, usuarios = cargar_datos()
    ejecutar_menu_principal(habitaciones, usuarios)


if __name__ == "__main__":
    main()
