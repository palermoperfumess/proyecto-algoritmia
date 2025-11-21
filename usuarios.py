
import re
from utilidades import box, print_tabla


def listar_usuarios(usuarios):
    filas = list(map(
        lambda u: [str(u["id"]), u["nombre"], u["dni"]],
        usuarios
    ))
    print_tabla(["ID", "Nombre", "DNI"], filas, [4, 20, 12])


def agregar_usuario(usuarios):
    print("\nNuevo usuario:")
    nombre = input("Nombre y apellido: ").strip()
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s'\.-]+$", nombre):
        print("Nombre inválido. Use solo letras, espacios, apóstrofes, guiones o puntos.")
        return None

    dni = input("DNI (7 a 9 números): ").strip()
    if not re.match(r'^\d{7,9}$', dni):
        print("DNI inválido. Debe contener solo 7 a 9 números.")
        return None

    if not usuarios:
        nuevo_id = 1
    else:
        nuevo_id = max(u["id"] for u in usuarios) + 1

    nuevo = {"id": nuevo_id, "nombre": nombre, "dni": dni}
    usuarios.append(nuevo)
    print("Usuario agregado con ID", nuevo_id)
    return nuevo


def seleccionar_usuario(usuarios):
    while True:
        box("Seleccionar Usuario")
        listar_usuarios(usuarios)
        print("Opciones: [E]legir por ID | [N]uevo usuario | [V]olver")
        op = input("> ").lower()

        if op == "e":
            cad = input("Ingrese ID: ")
            try:
                val = int(cad)
                usuario_encontrado = None
                for u in usuarios:
                    if u["id"] == val:
                        usuario_encontrado = u
                        break
                if usuario_encontrado:
                    return usuario_encontrado
                else:
                    print("No existe ese ID.")
            except ValueError:
                print("ID inválido. Debe ser un número.")
        elif op == "n":
            u = agregar_usuario(usuarios)
            if u is not None:
                return u
        elif op == "v":
            return None
        else:
            print("Opción inválida.")
