from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar


TipoValor = TypeVar("TipoValor")


@dataclass(slots=True)
class NodoPila(Generic[TipoValor]):
    valor: TipoValor
    siguiente: NodoPila[TipoValor] | None = None


class Pila(Generic[TipoValor]):
    def __init__(self) -> None:
        self._tope: NodoPila[TipoValor] | None = None
        self._longitud = 0

    def __len__(self) -> int:
        return self._longitud

    def __iter__(self) -> Iterator[TipoValor]:
        nodo_actual = self._tope
        while nodo_actual is not None:
            yield nodo_actual.valor
            nodo_actual = nodo_actual.siguiente

    def esta_vacia(self) -> bool:
        return self._tope is None

    def apilar(self, valor: TipoValor) -> None:
        self._tope = NodoPila(valor=valor, siguiente=self._tope)
        self._longitud += 1

    def desapilar(self) -> TipoValor:
        if self._tope is None:
            raise IndexError("La pila esta vacia.")
        valor = self._tope.valor
        self._tope = self._tope.siguiente
        self._longitud -= 1
        return valor

    def ver_tope(self) -> TipoValor:
        if self._tope is None:
            raise IndexError("La pila esta vacia.")
        return self._tope.valor
