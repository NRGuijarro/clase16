from __future__ import annotations

import re
from datetime import date
from typing import Iterable

from .excepciones import ErrorValidacion
from .modelos import ESTADOS_PEDIDO_VALIDOS


PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_TELEFONO = re.compile(r"^\+?\d{10,15}$")


def validar_texto_obligatorio(nombre_campo: str, valor: str) -> str:
    texto = valor.strip()
    if not texto:
        raise ErrorValidacion(f"Error: El campo '{nombre_campo}' es obligatorio.")
    return texto


def validar_correo(correo: str) -> str:
    correo_limpio = validar_texto_obligatorio("correo", correo)
    if not PATRON_CORREO.match(correo_limpio):
        raise ErrorValidacion(
            "Error: El correo ingresado no es valido. Debe tener un formato como usuario@dominio.com."
        )
    return correo_limpio


def validar_telefono(telefono: str) -> str:
    telefono_limpio = validar_texto_obligatorio("telefono", telefono)
    if not PATRON_TELEFONO.match(telefono_limpio):
        raise ErrorValidacion(
            "Error: El numero de telefono ingresado no es valido. Debe contener entre 10 y 15 digitos numericos."
        )
    return telefono_limpio


def validar_cantidad_positiva(nombre_campo: str, valor: int) -> int:
    if valor <= 0:
        raise ErrorValidacion(f"Error: El campo '{nombre_campo}' debe ser mayor que cero.")
    return valor


def validar_lista_no_vacia(nombre_campo: str, elementos: Iterable[object]) -> None:
    if not list(elementos):
        raise ErrorValidacion(f"Error: Debe proporcionar al menos un elemento en '{nombre_campo}'.")


def validar_fecha_futura(nombre_campo: str, valor: date) -> date:
    if valor < date.today():
        raise ErrorValidacion(f"Error: La '{nombre_campo}' no puede estar en el pasado.")
    return valor


def validar_estado_pedido(estado: str) -> str:
    estado_limpio = validar_texto_obligatorio("estado", estado).lower()
    if estado_limpio not in ESTADOS_PEDIDO_VALIDOS:
        raise ErrorValidacion(
            "Error: El estado del pedido no es valido. Use uno de los estados permitidos."
        )
    return estado_limpio


def validar_prioridad(prioridad: int) -> int:
    if prioridad not in (1, 2):
        raise ErrorValidacion("Error: La prioridad debe ser 1 para urgente o 2 para regular.")
    return prioridad
