from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Iterator, TypeVar


TipoValor = TypeVar("TipoValor")


@dataclass(slots=True)
class NodoLista(Generic[TipoValor]):
    valor: TipoValor
    siguiente: NodoLista[TipoValor] | None = None


class ListaEnlazada(Generic[TipoValor]):
    def __init__(self, elementos: Iterable[TipoValor] | None = None) -> None:
        self.cabeza: NodoLista[TipoValor] | None = None
        self.cola: NodoLista[TipoValor] | None = None
        self._longitud = 0
        if elementos is not None:
            for elemento in elementos:
                self.agregar_al_final(elemento)

    def __len__(self) -> int:
        return self._longitud

    def __iter__(self) -> Iterator[TipoValor]:
        nodo_actual = self.cabeza
        while nodo_actual is not None:
            yield nodo_actual.valor
            nodo_actual = nodo_actual.siguiente

    def esta_vacia(self) -> bool:
        return self.cabeza is None

    def agregar_al_inicio(self, valor: TipoValor) -> None:
        nuevo_nodo = NodoLista(valor=valor, siguiente=self.cabeza)
        self.cabeza = nuevo_nodo
        if self.cola is None:
            self.cola = nuevo_nodo
        self._longitud += 1

    def agregar_al_final(self, valor: TipoValor) -> None:
        nuevo_nodo = NodoLista(valor=valor)
        if self.cola is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self._longitud += 1

    def buscar(self, predicado: Callable[[TipoValor], bool]) -> TipoValor | None:
        for valor in self:
            if predicado(valor):
                return valor
        return None

    def filtrar(self, predicado: Callable[[TipoValor], bool]) -> list[TipoValor]:
        return [valor for valor in self if predicado(valor)]

    def eliminar_primero(self, predicado: Callable[[TipoValor], bool]) -> TipoValor | None:
        anterior: NodoLista[TipoValor] | None = None
        actual = self.cabeza
        while actual is not None:
            if predicado(actual.valor):
                if anterior is None:
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                if actual is self.cola:
                    self.cola = anterior
                self._longitud -= 1
                return actual.valor
            anterior = actual
            actual = actual.siguiente
        return None

    def limpiar(self) -> None:
        self.cabeza = None
        self.cola = None
        self._longitud = 0
