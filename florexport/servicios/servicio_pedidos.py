from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime

from ..estructuras import ListaEnlazada, Pila
from ..excepciones import ErrorPedido, ErrorValidacion
from ..modelos import Cliente, DetalleRamillete, FlorPersonalizada, OperacionSistema, Pedido
from ..utilidades import normalizar_texto
from ..validaciones import (
    validar_cantidad_positiva,
    validar_correo,
    validar_estado_pedido,
    validar_fecha_futura,
    validar_prioridad,
    validar_telefono,
    validar_texto_obligatorio,
)


class ServicioPedidos:
    def __init__(self, inventario, generador_identificadores, catalogo_ramilletes) -> None:
        self._inventario = inventario
        self._generador_identificadores = generador_identificadores
        self._pedidos: ListaEnlazada[Pedido] = ListaEnlazada()
        self._indice_pedidos: dict[str, Pedido] = {}
        self._historial_operaciones: Pila[OperacionSistema] = Pila()
        self._catalogo_ordenado = list(catalogo_ramilletes)
        self._catalogo_por_nombre = {
            normalizar_texto(configuracion["nombre"]): configuracion
            for configuracion in self._catalogo_ordenado
        }

    def listar_catalogo_ramilletes(self) -> list[dict[str, object]]:
        return list(self._catalogo_ordenado)

    def listar_pedidos(self) -> list[Pedido]:
        return list(self._pedidos)

    def listar_pedidos_por_estado(self, estado: str) -> list[Pedido]:
        estado_limpio = validar_estado_pedido(estado)
        return [pedido for pedido in self._pedidos if pedido.estado == estado_limpio]

    def obtener_historial_operaciones(self, limite: int = 10) -> list[OperacionSistema]:
        operaciones: list[OperacionSistema] = []
        for indice, operacion in enumerate(self._historial_operaciones):
            if indice >= limite:
                break
            operaciones.append(operacion)
        return operaciones

    def obtener_configuracion_ramillete(self, nombre_ramillete: str) -> dict[str, object]:
        nombre_normalizado = normalizar_texto(nombre_ramillete)
        configuracion = self._catalogo_por_nombre.get(nombre_normalizado)
        if configuracion is None:
            raise ErrorPedido("Error: El ramillete solicitado no existe en el catalogo.")
        return configuracion

    def construir_receta(self, configuracion: dict[str, object]) -> list[FlorPersonalizada]:
        return [
            FlorPersonalizada(
                nombre=flor["nombre"],
                color=flor["color"],
                cantidad_tallos_por_ramillete=flor["cantidad"],
            )
            for flor in configuracion["receta"]
        ]

    def crear_detalle_desde_catalogo(
        self,
        nombre_ramillete: str,
        cantidad_ramilletes: int,
        flores_personalizadas: list[FlorPersonalizada] | None = None,
        notas: str = "",
    ) -> DetalleRamillete:
        configuracion = self.obtener_configuracion_ramillete(nombre_ramillete)
        return DetalleRamillete(
            nombre_ramillete=configuracion["nombre"],
            tamano=configuracion["tamano"],
            cantidad_ramilletes=validar_cantidad_positiva("cantidad de ramilletes", cantidad_ramilletes),
            flores_base=configuracion["flores_base"],
            precio_unitario=configuracion["precio"],
            receta_base=self.construir_receta(configuracion),
            flores_personalizadas=list(flores_personalizadas or []),
            notas=notas.strip(),
        )

    def buscar_pedido_por_id(self, identificador: str) -> Pedido:
        pedido = self._indice_pedidos.get(identificador.strip().upper())
        if pedido is None:
            raise ErrorPedido("Error: No existe un pedido con el identificador indicado.")
        return pedido

    def crear_pedido(
        self,
        cliente: Cliente,
        detalles: list[DetalleRamillete],
        direccion_envio: str,
        fecha_entrega_deseada: date,
        prioridad: int = 2,
        notas: str = "",
    ) -> Pedido:
        self._validar_cliente(cliente)
        self._validar_detalles(detalles)
        direccion_limpia = validar_texto_obligatorio("direccion de envio", direccion_envio)
        fecha_limpia = validar_fecha_futura("fecha de entrega deseada", fecha_entrega_deseada)
        prioridad_limpia = validar_prioridad(prioridad)

        identificador = self._generador_identificadores.siguiente_pedido()
        requerimientos = self._calcular_requerimientos(detalles)
        self._inventario.reservar_requerimientos(requerimientos, f"Reserva para pedido {identificador}")

        pedido = Pedido(
            identificador=identificador,
            cliente=cliente,
            detalles=detalles,
            direccion_envio=direccion_limpia,
            fecha_registro=datetime.now(),
            fecha_entrega_deseada=fecha_limpia,
            prioridad=prioridad_limpia,
            notas=notas.strip(),
        )

        try:
            self._pedidos.agregar_al_final(pedido)
            self._indice_pedidos[pedido.identificador] = pedido
        except Exception as error:
            self._inventario.liberar_requerimientos(
                requerimientos,
                f"Rollback por error al registrar pedido {identificador}",
            )
            raise ErrorPedido("Error: No fue posible registrar el pedido en la lista enlazada.") from error

        self._registrar_operacion(
            accion="Crear pedido",
            descripcion=f"Se creo el pedido {pedido.identificador} para {pedido.cliente.nombre}.",
        )
        return pedido

    def modificar_pedido(
        self,
        identificador: str,
        cliente: Cliente | None = None,
        detalles: list[DetalleRamillete] | None = None,
        direccion_envio: str | None = None,
        fecha_entrega_deseada: date | None = None,
        prioridad: int | None = None,
        notas: str | None = None,
    ) -> Pedido:
        pedido = self.buscar_pedido_por_id(identificador)
        if pedido.estado not in {"pendiente", "en_preparacion"}:
            raise ErrorPedido("Error: Solo se pueden modificar pedidos aun no despachados.")

        respaldo = deepcopy(pedido)
        cliente_nuevo = cliente if cliente is not None else pedido.cliente
        detalles_nuevos = detalles if detalles is not None else pedido.detalles
        direccion_nueva = direccion_envio if direccion_envio is not None else pedido.direccion_envio
        fecha_nueva = fecha_entrega_deseada if fecha_entrega_deseada is not None else pedido.fecha_entrega_deseada
        prioridad_nueva = prioridad if prioridad is not None else pedido.prioridad
        notas_nuevas = notas if notas is not None else pedido.notas

        self._validar_cliente(cliente_nuevo)
        self._validar_detalles(detalles_nuevos)
        direccion_nueva = validar_texto_obligatorio("direccion de envio", direccion_nueva)
        fecha_nueva = validar_fecha_futura("fecha de entrega deseada", fecha_nueva)
        prioridad_nueva = validar_prioridad(prioridad_nueva)

        reservas, liberaciones = self._calcular_diferencias_requerimientos(
            actuales=self._calcular_requerimientos(pedido.detalles),
            nuevos=self._calcular_requerimientos(detalles_nuevos),
        )
        hubo_liberaciones = False
        hubo_reservas = False

        try:
            # Primero se liberan diferencias sobrantes y despues se reservan los nuevos faltantes.
            if liberaciones:
                self._inventario.liberar_requerimientos(
                    liberaciones,
                    f"Liberacion por modificacion de pedido {pedido.identificador}",
                )
                hubo_liberaciones = True
            if reservas:
                self._inventario.reservar_requerimientos(
                    reservas,
                    f"Ajuste por modificacion de pedido {pedido.identificador}",
                )
                hubo_reservas = True

            pedido.cliente = cliente_nuevo
            pedido.detalles = detalles_nuevos
            pedido.direccion_envio = direccion_nueva
            pedido.fecha_entrega_deseada = fecha_nueva
            pedido.prioridad = prioridad_nueva
            pedido.notas = notas_nuevas.strip()
        except Exception as error:
            if hubo_reservas:
                self._inventario.liberar_requerimientos(
                    reservas,
                    f"Rollback de reserva para pedido {pedido.identificador}",
                )
            if hubo_liberaciones:
                self._inventario.reservar_requerimientos(
                    liberaciones,
                    f"Rollback de liberacion para pedido {pedido.identificador}",
                )
            self._restaurar_pedido(pedido, respaldo)
            raise ErrorPedido("Error: No fue posible modificar el pedido solicitado.") from error

        self._registrar_operacion(
            accion="Modificar pedido",
            descripcion=f"Se modifico el pedido {pedido.identificador}.",
        )
        return pedido

    def eliminar_pedido(self, identificador: str) -> Pedido:
        pedido = self.buscar_pedido_por_id(identificador)
        if pedido.estado != "pendiente":
            raise ErrorPedido(
                "Error: Solo se pueden eliminar pedidos pendientes que aun no entraron en preparacion o envio."
            )

        requerimientos = self._calcular_requerimientos(pedido.detalles)
        self._inventario.liberar_requerimientos(
            requerimientos,
            f"Cancelacion del pedido {pedido.identificador}",
        )
        eliminado = self._pedidos.eliminar_primero(lambda actual: actual.identificador == pedido.identificador)
        if eliminado is None:
            raise ErrorPedido("Error: El pedido no pudo eliminarse de la lista enlazada.")
        self._indice_pedidos.pop(pedido.identificador, None)

        self._registrar_operacion(
            accion="Eliminar pedido",
            descripcion=f"Se elimino el pedido {pedido.identificador} del sistema.",
        )
        return eliminado

    def actualizar_estado(
        self,
        identificador: str,
        nuevo_estado: str,
        descripcion: str = "",
        validar_transicion: bool = True,
    ) -> Pedido:
        pedido = self.buscar_pedido_por_id(identificador)
        estado_limpio = validar_estado_pedido(nuevo_estado)
        if pedido.estado == estado_limpio:
            return pedido
        if validar_transicion and not self._transicion_valida(pedido.estado, estado_limpio):
            raise ErrorPedido(
                f"Error: No se permite pasar del estado '{pedido.estado}' a '{estado_limpio}'."
            )
        pedido.estado = estado_limpio
        detalle_historial = descripcion or f"El pedido {pedido.identificador} paso a estado {estado_limpio}."
        self._registrar_operacion(accion="Cambio de estado", descripcion=detalle_historial)
        return pedido

    def _validar_cliente(self, cliente: Cliente) -> None:
        cliente.nombre = validar_texto_obligatorio("nombre del cliente", cliente.nombre)
        cliente.correo = validar_correo(cliente.correo)
        cliente.telefono = validar_telefono(cliente.telefono)
        cliente.pais_destino = validar_texto_obligatorio("pais de destino", cliente.pais_destino)

    def _validar_detalles(self, detalles: list[DetalleRamillete]) -> None:
        if not detalles:
            raise ErrorValidacion("Error: Debe agregar al menos un ramillete al pedido.")
        for detalle in detalles:
            validar_texto_obligatorio("nombre de ramillete", detalle.nombre_ramillete)
            validar_cantidad_positiva("cantidad de ramilletes", detalle.cantidad_ramilletes)
            flores_aplicadas = detalle.obtener_flores_aplicadas()
            if not flores_aplicadas:
                raise ErrorValidacion(
                    "Error: Cada ramillete debe tener una receta base o una personalizacion valida."
                )
            for flor in flores_aplicadas:
                validar_texto_obligatorio("nombre de flor", flor.nombre)
                validar_texto_obligatorio("color de flor", flor.color)
                validar_cantidad_positiva(
                    "cantidad de tallos por ramillete",
                    flor.cantidad_tallos_por_ramillete,
                )

    def _calcular_requerimientos(self, detalles: list[DetalleRamillete]) -> list[tuple[str, str, int]]:
        acumulado: dict[tuple[str, str], int] = {}
        for detalle in detalles:
            for flor in detalle.obtener_flores_aplicadas():
                clave = (flor.nombre, flor.color)
                cantidad_total = flor.cantidad_tallos_por_ramillete * detalle.cantidad_ramilletes
                acumulado[clave] = acumulado.get(clave, 0) + cantidad_total
        return [(nombre, color, cantidad) for (nombre, color), cantidad in acumulado.items()]

    def _calcular_diferencias_requerimientos(
        self,
        actuales: list[tuple[str, str, int]],
        nuevos: list[tuple[str, str, int]],
    ) -> tuple[list[tuple[str, str, int]], list[tuple[str, str, int]]]:
        mapa_actual = {(nombre, color): cantidad for nombre, color, cantidad in actuales}
        mapa_nuevo = {(nombre, color): cantidad for nombre, color, cantidad in nuevos}
        claves = set(mapa_actual) | set(mapa_nuevo)
        reservas: list[tuple[str, str, int]] = []
        liberaciones: list[tuple[str, str, int]] = []

        for nombre, color in claves:
            delta = mapa_nuevo.get((nombre, color), 0) - mapa_actual.get((nombre, color), 0)
            if delta > 0:
                reservas.append((nombre, color, delta))
            elif delta < 0:
                liberaciones.append((nombre, color, abs(delta)))
        return reservas, liberaciones

    def _restaurar_pedido(self, pedido_destino: Pedido, pedido_respaldo: Pedido) -> None:
        pedido_destino.cliente = pedido_respaldo.cliente
        pedido_destino.detalles = pedido_respaldo.detalles
        pedido_destino.direccion_envio = pedido_respaldo.direccion_envio
        pedido_destino.fecha_registro = pedido_respaldo.fecha_registro
        pedido_destino.fecha_entrega_deseada = pedido_respaldo.fecha_entrega_deseada
        pedido_destino.estado = pedido_respaldo.estado
        pedido_destino.prioridad = pedido_respaldo.prioridad
        pedido_destino.notas = pedido_respaldo.notas
        pedido_destino.numero_seguimiento = pedido_respaldo.numero_seguimiento
        pedido_destino.transportista = pedido_respaldo.transportista
        pedido_destino.fecha_estimada_entrega = pedido_respaldo.fecha_estimada_entrega

    def _transicion_valida(self, estado_actual: str, nuevo_estado: str) -> bool:
        transiciones = {
            "pendiente": {"en_preparacion", "cancelado"},
            "en_preparacion": {"pendiente", "enviado", "cancelado"},
            "enviado": {"entregado"},
            "entregado": set(),
            "cancelado": set(),
        }
        return nuevo_estado in transiciones.get(estado_actual, set())

    def _registrar_operacion(self, accion: str, descripcion: str) -> None:
        self._historial_operaciones.apilar(
            OperacionSistema(modulo="Gestion de Pedidos", accion=accion, descripcion=descripcion)
        )
