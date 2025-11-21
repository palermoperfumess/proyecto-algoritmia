
from config import FILE_HABITACIONES, FILE_USUARIOS
from typing import List, Dict


def crear_habitaciones() -> List[Dict]:
    habs = []
    for i in range(1, 26):
        codigo = "H" + ("00" + str(i))[-3:]
        if i <= 10:
            tipo = "Single"; ambientes = 1; capacidad = 1; precio = 60_000
        elif i <= 20:
            tipo = "Doble"; ambientes = 2; capacidad = 2; precio = 85_000
        else:
            tipo = "Suite"; ambientes = 3; capacidad = 4; precio = 140_000
        habs.append({
            "id": i, "codigo": codigo, "tipo": tipo, "ambientes": ambientes,
            "capacidad": capacidad, "precio": precio, "reservas": []
        })
    return habs


def crear_usuarios_base() -> List[Dict]:
    return [
        {"id": 1, "nombre": "Ana Pérez", "dni": "30123456"},
        {"id": 2, "nombre": "Luis Gómez", "dni": "28999888"}
    ]


# ======================
# SERIALIZACIÓN RESERVAS
# ======================

def serializar_reservas(reservas: List[Dict]) -> str:
    """
    Convierte la lista de reservas en un string usando el formato:
    usuario,entrada,salida,precio,personas,tipo,ambientes,pago;...
    """
    partes = []
    for r in reservas:
        item = ",".join([
            r["usuario_nombre"],
            r["entrada"],
            r["salida"],
            str(r["precio_noche"]),
            str(r["personas"]),
            r["tipo"],
            str(r["ambientes"]),
            r["pago"]
        ])
        partes.append(item)
    return ";".join(partes)


def deserializar_reservas(cadena: str) -> List[Dict]:
    """
    Convierte el string de reservas del archivo en una lista de diccionarios.
    """
    cadena = cadena.strip()
    if not cadena:
        return []

    items = cadena.split(";")
    reservas = []

    for item in items:
        campos = item.split(",")
        if len(campos) != 8:
            continue  # línea corrupta, se ignora

        usuario_nombre, entrada, salida, precio, personas, tipo, ambientes, pago = campos

        try:
            reservas.append({
                "usuario_nombre": usuario_nombre,
                "entrada": entrada,
                "salida": salida,
                "precio_noche": int(precio),
                "personas": int(personas),
                "tipo": tipo,
                "ambientes": int(ambientes),
                "pago": pago
            })
        except ValueError:
            # Si algún campo numérico no es válido, se descarta esa reserva
            continue

    return reservas


# ======================
# GUARDAR / CARGAR
# ======================

def guardar_datos(habitaciones: List[Dict], usuarios: List[Dict]) -> None:
    try:
        # Guardar usuarios
        with open(FILE_USUARIOS, "w", encoding="utf-8") as f:
            for u in usuarios:
                linea = f"{u['id']}|{u['nombre']}|{u['dni']}\n"
                f.write(linea)

        # Guardar habitaciones
        with open(FILE_HABITACIONES, "w", encoding="utf-8") as f:
            for h in habitaciones:
                reservas_serializadas = serializar_reservas(h["reservas"])
                linea = "|".join([
                    str(h["id"]),
                    h["codigo"],
                    h["tipo"],
                    str(h["ambientes"]),
                    str(h["capacidad"]),
                    str(h["precio"]),
                    reservas_serializadas
                ]) + "\n"
                f.write(linea)

        print("\n[Datos guardados exitosamente.]")

    except Exception as e:
        print(f"[Error crítico al guardar]: {e}")


def cargar_datos():
    try:
        usuarios: List[Dict] = []
        habitaciones: List[Dict] = []

        # Cargar usuarios
        with open(FILE_USUARIOS, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split("|")
                if len(partes) != 3:
                    continue
                id_, nombre, dni = partes
                try:
                    usuarios.append({
                        "id": int(id_),
                        "nombre": nombre,
                        "dni": dni
                    })
                except ValueError:
                    continue

        # Cargar habitaciones
        with open(FILE_HABITACIONES, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split("|")
                if len(partes) < 7:
                    continue

                id_, codigo, tipo, amb, cap, precio, reservas_str = partes[:7]

                try:
                    hab = {
                        "id": int(id_),
                        "codigo": codigo,
                        "tipo": tipo,
                        "ambientes": int(amb),
                        "capacidad": int(cap),
                        "precio": int(precio),
                        "reservas": deserializar_reservas(reservas_str)
                    }
                    habitaciones.append(hab)
                except ValueError:
                    continue

        print("[Datos cargados exitosamente.]")
        return habitaciones, usuarios

    except FileNotFoundError:
        print("[No existen archivos de datos. Creando datos base...]")
        habitaciones = crear_habitaciones()
        usuarios = crear_usuarios_base()
        guardar_datos(habitaciones, usuarios)
        return habitaciones, usuarios

    except Exception as e:
        print(f"[Error inesperado al cargar datos]: {e}")
        habitaciones = crear_habitaciones()
        usuarios = crear_usuarios_base()
        guardar_datos(habitaciones, usuarios)
        return habitaciones, usuarios
