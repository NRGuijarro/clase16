from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterator, TypeVar


TipoValor = TypeVar("TipoValor")


@dataclass(slots=True)
class NodoCola(Generic[TipoValor]):
    valor: TipoValor
    prioridad: int
    siguiente: NodoCola[TipoValor] | None = None


class ColaPrioridadDinamica(Generic[TipoValor]):
    def __init__(self) -> None:
        self._cabeza: NodoCola[TipoValor] | None = None
        self._longitud = 0

    def __len__(self) -> int:
        return self._longitud

    def __iter__(self) -> Iterator[TipoValor]:
        nodo_actual = self._cabeza
        while nodo_actual is not None:
            yield nodo_actual.valor
            nodo_actual = nodo_actual.siguiente

    def esta_vacia(self) -> bool:
        return self._cabeza is None

    def encolar(self, valor: TipoValor, prioridad: int) -> None:
        nuevo_nodo = NodoCola(valor=valor, prioridad=prioridad)
        if self._cabeza is None or prioridad < self._cabeza.prioridad:
            nuevo_nodo.siguiente = self._cabeza
            self._cabeza = nuevo_nodo
            self._longitud += 1
            return

        actual = self._cabeza
        while actual.siguiente is not None and actual.siguiente.prioridad <= prioridad:
            actual = actual.siguiente

        nuevo_nodo.siguiente = actual.siguiente
        actual.siguiente = nuevo_nodo
        self._longitud += 1

    def desencolar(self) -> TipoValor:
        if self._cabeza is None:
            raise IndexError("La cola esta vacia.")
        valor = self._cabeza.valor
        self._cabeza = self._cabeza.siguiente
        self._longitud -= 1
        return valor

    def listar(self) -> list[TipoValor]:
        return list(self)

    def remover_si(self, predicado: Callable[[TipoValor], bool]) -> TipoValor | None:
        anterior: NodoCola[TipoValor] | None = None
        actual = self._cabeza
        while actual is not None:
            if predicado(actual.valor):
                if anterior is None:
                    self._cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                self._longitud -= 1
                return actual.valor
            anterior = actual
            actual = actual.siguiente
        return None
