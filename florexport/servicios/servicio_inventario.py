from __future__ import annotations

from typing import Iterable

from ..estructuras import ListaEnlazada, Pila
from ..excepciones import ErrorInventario
from ..modelos import FlorInventario, MovimientoInventario
from ..utilidades import a_decimal, normalizar_texto
from ..validaciones import validar_cantidad_positiva, validar_texto_obligatorio


class ServicioInventario:
    def __init__(self, flores_iniciales: Iterable[FlorInventario] | None = None) -> None:
        self._inventario: ListaEnlazada[FlorInventario] = ListaEnlazada()
        self._indice_por_codigo: dict[str, FlorInventario] = {}
        self._indice_por_clave: dict[tuple[str, str], FlorInventario] = {}
        self._historial_movimientos: Pila[MovimientoInventario] = Pila()
        self._siguiente_codigo = 1
        if flores_iniciales is not None:
            for flor in flores_iniciales:
                self._registrar_flor_existente(flor)

    def listar_inventario(self) -> list[FlorInventario]:
        return list(self._inventario)

    def total_stock(self) -> int:
        return sum(flor.stock for flor in self._inventario)

    def obtener_alertas_stock_bajo(self) -> list[FlorInventario]:
        return [flor for flor in self._inventario if flor.stock <= flor.stock_minimo]

    def obtener_historial_movimientos(self, limite: int = 10) -> list[MovimientoInventario]:
        movimientos: list[MovimientoInventario] = []
        for indice, movimiento in enumerate(self._historial_movimientos):
            if indice >= limite:
                break
            movimientos.append(movimiento)
        return movimientos

    def buscar_flores(self, nombre: str = "", color: str = "") -> list[FlorInventario]:
        nombre_normalizado = normalizar_texto(nombre) if nombre else ""
        color_normalizado = normalizar_texto(color) if color else ""
        resultados = []
        for flor in self._inventario:
            if nombre_normalizado and nombre_normalizado not in normalizar_texto(flor.nombre):
                continue
            if color_normalizado and color_normalizado not in normalizar_texto(flor.color):
                continue
            resultados.append(flor)
        return resultados

    def obtener_flor(self, nombre: str, color: str) -> FlorInventario | None:
        clave = self._construir_clave(nombre, color)
        return self._indice_por_clave.get(clave)

    def obtener_flor_por_codigo(self, codigo: str) -> FlorInventario | None:
        return self._indice_por_codigo.get(codigo.strip().upper())

    def registrar_lote(
        self,
        nombre: str,
        color: str,
        cantidad: int,
        precio_unitario: str | int | float | None = None,
    ) -> tuple[FlorInventario, MovimientoInventario]:
        nombre_limpio = validar_texto_obligatorio("nombre de flor", nombre)
        color_limpio = validar_texto_obligatorio("color", color)
        cantidad_limpia = validar_cantidad_positiva("cantidad de lote", cantidad)
        flor = self.obtener_flor(nombre_limpio, color_limpio)

        if flor is None:
            if precio_unitario is None:
                raise ErrorInventario(
                    "Error: Debe indicar un precio unitario al registrar una flor nueva en inventario."
                )
            flor = FlorInventario(
                codigo=self._generar_codigo(),
                nombre=nombre_limpio,
                color=color_limpio,
                stock=0,
                precio_unitario=a_decimal(precio_unitario),
            )
            self._registrar_flor_existente(flor)
        elif precio_unitario is not None:
            flor.precio_unitario = a_decimal(precio_unitario)

        stock_anterior = flor.stock
        flor.stock += cantidad_limpia
        movimiento = self._registrar_movimiento(
            tipo="Entrada de lote",
            flor=flor,
            cantidad=cantidad_limpia,
            stock_anterior=stock_anterior,
            stock_nuevo=flor.stock,
        )
        return flor, movimiento

    def actualizar_stock_manual(
        self,
        referencia: str,
        color: str,
        ajuste: int,
        motivo: str,
    ) -> tuple[FlorInventario, MovimientoInventario]:
        if ajuste == 0:
            raise ErrorInventario("Error: El ajuste manual debe ser diferente de cero.")
        motivo_limpio = validar_texto_obligatorio("motivo del ajuste", motivo)
        flor = self._resolver_flor(referencia=referencia, color=color)
        stock_nuevo = flor.stock + ajuste
        if stock_nuevo < 0:
            raise ErrorInventario(
                f"Error: El ajuste solicitado deja stock negativo para {flor.nombre} {flor.color}."
            )

        stock_anterior = flor.stock
        flor.stock = stock_nuevo
        movimiento = self._registrar_movimiento(
            tipo=motivo_limpio,
            flor=flor,
            cantidad=ajuste,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
        )
        return flor, movimiento

    def verificar_disponibilidad(self, requerimientos: list[tuple[str, str, int]]) -> None:
        for nombre, color, cantidad in requerimientos:
            cantidad_limpia = validar_cantidad_positiva("cantidad solicitada", cantidad)
            flor = self.obtener_flor(nombre, color)
            if flor is None:
                raise ErrorInventario(
                    f"Error: No existe inventario registrado para {nombre} de color {color}."
                )
            if flor.stock < cantidad_limpia:
                raise ErrorInventario(
                    f"Error: La cantidad solicitada excede el inventario disponible. "
                    f"Solo quedan {flor.stock} {flor.nombre.lower()}s {flor.color.lower()} en stock."
                )

    def reservar_requerimientos(self, requerimientos: list[tuple[str, str, int]], motivo: str) -> None:
        if not requerimientos:
            return
        self.verificar_disponibilidad(requerimientos)
        cambios_aplicados: list[tuple[FlorInventario, int]] = []

        try:
            for nombre, color, cantidad in requerimientos:
                flor = self.obtener_flor(nombre, color)
                if flor is None:
                    raise ErrorInventario(
                        f"Error: No fue posible reservar {nombre} {color} porque no existe en inventario."
                    )
                stock_anterior = flor.stock
                flor.stock -= cantidad
                cambios_aplicados.append((flor, stock_anterior))
                self._registrar_movimiento(
                    tipo=motivo,
                    flor=flor,
                    cantidad=-cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=flor.stock,
                )
        except Exception as error:
            for flor, stock_anterior in reversed(cambios_aplicados):
                flor.stock = stock_anterior
            raise ErrorInventario("Error: No fue posible completar la reserva de inventario.") from error

    def liberar_requerimientos(self, requerimientos: list[tuple[str, str, int]], motivo: str) -> None:
        for nombre, color, cantidad in requerimientos:
            flor = self.obtener_flor(nombre, color)
            if flor is None:
                raise ErrorInventario(
                    f"Error: No fue posible liberar inventario para {nombre} {color}."
                )
            stock_anterior = flor.stock
            flor.stock += cantidad
            self._registrar_movimiento(
                tipo=motivo,
                flor=flor,
                cantidad=cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=flor.stock,
            )

    def _registrar_flor_existente(self, flor: FlorInventario) -> None:
        self._inventario.agregar_al_final(flor)
        self._indice_por_codigo[flor.codigo] = flor
        self._indice_por_clave[self._construir_clave(flor.nombre, flor.color)] = flor
        self._actualizar_contador_codigo(flor.codigo)

    def _registrar_movimiento(
        self,
        tipo: str,
        flor: FlorInventario,
        cantidad: int,
        stock_anterior: int,
        stock_nuevo: int,
    ) -> MovimientoInventario:
        movimiento = MovimientoInventario(
            tipo=tipo,
            nombre_flor=flor.nombre,
            color=flor.color,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
        )
        self._historial_movimientos.apilar(movimiento)
        return movimiento

    def _resolver_flor(self, referencia: str, color: str) -> FlorInventario:
        referencia_limpia = validar_texto_obligatorio("referencia de flor", referencia)
        flor = self.obtener_flor_por_codigo(referencia_limpia)
        if flor is not None:
            return flor
        flor = self.obtener_flor(referencia_limpia, color)
        if flor is None:
            raise ErrorInventario("Error: La flor indicada no existe en el inventario.")
        return flor

    def _generar_codigo(self) -> str:
        codigo = f"F{self._siguiente_codigo:03d}"
        self._siguiente_codigo += 1
        return codigo

    def _actualizar_contador_codigo(self, codigo: str) -> None:
        try:
            numero_actual = int(codigo.replace("F", "")) + 1
        except ValueError:
            numero_actual = self._siguiente_codigo
        self._siguiente_codigo = max(self._siguiente_codigo, numero_actual)

    @staticmethod
    def _construir_clave(nombre: str, color: str) -> tuple[str, str]:
        return normalizar_texto(nombre), normalizar_texto(color)
