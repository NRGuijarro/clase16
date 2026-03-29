from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from itertools import count


def a_decimal(valor: Decimal | float | int | str) -> Decimal:
    return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def formatear_moneda(valor: Decimal) -> str:
    return f"${a_decimal(valor)}"


def formatear_fecha(valor: date | None) -> str:
    if valor is None:
        return "N/D"
    return valor.strftime("%d/%m/%Y")


def formatear_fecha_hora(valor: datetime | None) -> str:
    if valor is None:
        return "N/D"
    return valor.strftime("%d/%m/%Y %H:%M:%S")


def normalizar_texto(texto: str) -> str:
    return texto.strip().lower()


class GeneradorIdentificadores:
    def __init__(self, inicio_pedidos: int = 1022, inicio_envios: int = 87654320) -> None:
        self._contador_pedidos = count(inicio_pedidos)
        self._contador_envios = count(inicio_envios)

    def siguiente_pedido(self) -> str:
        return f"P-{next(self._contador_pedidos)}"

    def siguiente_seguimiento(self, transportista: str) -> str:
        prefijos = {
            "DHL Express": "DHL",
            "FedEx International": "FDX",
            "UPS Global": "UPS",
        }
        prefijo = prefijos.get(transportista, "ENV")
        return f"{prefijo}-{next(self._contador_envios)}"
