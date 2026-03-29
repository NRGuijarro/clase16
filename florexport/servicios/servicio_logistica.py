from __future__ import annotations

from datetime import date, timedelta

from ..estructuras import ColaPrioridadDinamica, Pila
from ..excepciones import ErrorLogistica
from ..modelos import ESTADOS_ENVIO_VALIDOS, Envio, OperacionSistema
from ..validaciones import validar_texto_obligatorio


class ServicioLogistica:
    def __init__(self, servicio_pedidos, generador_identificadores, transportistas) -> None:
        self._servicio_pedidos = servicio_pedidos
        self._generador_identificadores = generador_identificadores
        self._transportistas = {
            transportista["nombre"]: dict(transportista) for transportista in transportistas
        }
        self._envios_por_pedido: dict[str, Envio] = {}
        self._envios_por_seguimiento: dict[str, Envio] = {}
        self._historial_operaciones: Pila[OperacionSistema] = Pila()

    def listar_transportistas(self) -> list[dict[str, object]]:
        return list(self._transportistas.values())

    def listar_cola_envios(self):
        cola = ColaPrioridadDinamica()
        for pedido in self._servicio_pedidos.listar_pedidos_por_estado("pendiente"):
            cola.encolar(pedido, pedido.prioridad)
        return cola.listar()

    def listar_pedidos_en_preparacion(self):
        return self._servicio_pedidos.listar_pedidos_por_estado("en_preparacion")

    def preparar_envio(self, identificador_pedido: str, nombre_transportista: str) -> Envio:
        pedido = self._servicio_pedidos.buscar_pedido_por_id(identificador_pedido)
        if pedido.estado != "pendiente":
            raise ErrorLogistica("Error: Solo los pedidos pendientes pueden pasar a preparacion de envio.")
        if pedido.identificador in self._envios_por_pedido:
            raise ErrorLogistica("Error: El pedido ya tiene un envio asociado.")

        transportista = self._obtener_transportista(nombre_transportista)
        numero_seguimiento = self._generador_identificadores.siguiente_seguimiento(transportista["nombre"])
        dias_estimados = transportista["dias_min"] if pedido.prioridad == 1 else transportista["dias_max"]
        fecha_estimada = date.today() + timedelta(days=dias_estimados)

        envio = Envio(
            identificador_pedido=pedido.identificador,
            cliente=pedido.cliente.nombre,
            origen="Bogota, Colombia",
            destino=pedido.destino,
            transportista=transportista["nombre"],
            numero_seguimiento=numero_seguimiento,
            estado_actual="En preparacion",
            fecha_estimada_entrega=fecha_estimada,
        )
        envio.registrar_evento("Preparacion iniciada - Pedido procesado.", "En preparacion")
        pedido.numero_seguimiento = numero_seguimiento
        pedido.transportista = transportista["nombre"]
        pedido.fecha_estimada_entrega = fecha_estimada
        self._envios_por_pedido[pedido.identificador] = envio
        self._envios_por_seguimiento[numero_seguimiento] = envio
        self._servicio_pedidos.actualizar_estado(
            pedido.identificador,
            "en_preparacion",
            descripcion=f"Pedido {pedido.identificador} preparado para envio con {transportista['nombre']}.",
        )
        self._registrar_operacion(
            accion="Preparar envio",
            descripcion=f"Se preparo el pedido {pedido.identificador} con seguimiento {numero_seguimiento}.",
        )
        return envio

    def registrar_despacho(self, identificador_pedido: str) -> Envio:
        pedido = self._servicio_pedidos.buscar_pedido_por_id(identificador_pedido)
        if pedido.estado != "en_preparacion":
            raise ErrorLogistica("Error: El pedido debe estar en preparacion antes de despacharse.")

        envio = self._envios_por_pedido.get(pedido.identificador)
        if envio is None:
            raise ErrorLogistica("Error: No existe un envio preparado para el pedido indicado.")

        envio.registrar_evento(
            f"Recogido por {envio.transportista} para despacho internacional.",
            "En transito",
        )
        self._servicio_pedidos.actualizar_estado(
            pedido.identificador,
            "enviado",
            descripcion=f"Pedido {pedido.identificador} entregado al transportista.",
        )
        self._registrar_operacion(
            accion="Registrar despacho",
            descripcion=f"El pedido {pedido.identificador} fue despachado con {envio.transportista}.",
        )
        return envio

    def actualizar_estado_envio(
        self,
        referencia: str,
        nuevo_estado: str,
        descripcion: str | None = None,
    ) -> Envio:
        estado_limpio = validar_texto_obligatorio("estado del envio", nuevo_estado).lower()
        if estado_limpio not in ESTADOS_ENVIO_VALIDOS:
            raise ErrorLogistica("Error: El estado del envio indicado no es valido.")

        envio = self.rastrear_envio(referencia)
        pedido = self._servicio_pedidos.buscar_pedido_por_id(envio.identificador_pedido)
        descripciones_por_defecto = {
            "en_preparacion": "El envio continua en preparacion.",
            "en_transito": "El envio se encuentra en transito.",
            "entregado": "El envio fue entregado al cliente final.",
            "incidencia": "Se registro una incidencia logistica en el envio.",
        }
        estados_mostrados = {
            "en_preparacion": "En preparacion",
            "en_transito": "En transito",
            "entregado": "Entregado",
            "incidencia": "Incidencia",
        }
        envio.registrar_evento(
            descripcion or descripciones_por_defecto[estado_limpio],
            estados_mostrados[estado_limpio],
        )

        if estado_limpio == "en_preparacion":
            self._servicio_pedidos.actualizar_estado(
                pedido.identificador,
                "en_preparacion",
                descripcion=f"Pedido {pedido.identificador} permanece en preparacion.",
                validar_transicion=False,
            )
        elif estado_limpio == "en_transito":
            self._servicio_pedidos.actualizar_estado(
                pedido.identificador,
                "enviado",
                descripcion=f"Pedido {pedido.identificador} en transito internacional.",
                validar_transicion=False,
            )
        elif estado_limpio == "entregado":
            self._servicio_pedidos.actualizar_estado(
                pedido.identificador,
                "entregado",
                descripcion=f"Pedido {pedido.identificador} entregado correctamente.",
            )

        self._registrar_operacion(
            accion="Actualizar envio",
            descripcion=f"El envio {envio.numero_seguimiento} cambio a estado {estado_limpio}.",
        )
        return envio

    def rastrear_envio(self, referencia: str) -> Envio:
        referencia_limpia = validar_texto_obligatorio("referencia de envio", referencia)
        envio = self._envios_por_seguimiento.get(referencia_limpia) or self._envios_por_pedido.get(
            referencia_limpia
        )
        if envio is None:
            raise ErrorLogistica("Error: No existe informacion de seguimiento para la referencia indicada.")
        return envio

    def generar_informe_logistica(self) -> dict[str, object]:
        pedidos = self._servicio_pedidos.listar_pedidos()
        pedidos_pendientes = len(self.listar_cola_envios())
        pedidos_preparacion = len(self.listar_pedidos_en_preparacion())
        pedidos_enviados = len(self._servicio_pedidos.listar_pedidos_por_estado("enviado"))
        pedidos_entregados = len(self._servicio_pedidos.listar_pedidos_por_estado("entregado"))
        destinos: dict[str, int] = {}
        transportistas: dict[str, int] = {}
        for pedido in pedidos:
            destinos[pedido.destino] = destinos.get(pedido.destino, 0) + 1
        for envio in self._envios_por_pedido.values():
            transportistas[envio.transportista] = transportistas.get(envio.transportista, 0) + 1

        return {
            "pedidos_pendientes": pedidos_pendientes,
            "pedidos_en_preparacion": pedidos_preparacion,
            "pedidos_enviados": pedidos_enviados,
            "pedidos_entregados": pedidos_entregados,
            "destinos": destinos,
            "transportistas": transportistas,
        }

    def obtener_historial_operaciones(self, limite: int = 10) -> list[OperacionSistema]:
        operaciones: list[OperacionSistema] = []
        for indice, operacion in enumerate(self._historial_operaciones):
            if indice >= limite:
                break
            operaciones.append(operacion)
        return operaciones

    def _obtener_transportista(self, nombre_transportista: str) -> dict[str, object]:
        nombre_limpio = validar_texto_obligatorio("transportista", nombre_transportista)
        transportista = self._transportistas.get(nombre_limpio)
        if transportista is None:
            raise ErrorLogistica("Error: El transportista seleccionado no existe.")
        return transportista

    def _registrar_operacion(self, accion: str, descripcion: str) -> None:
        self._historial_operaciones.apilar(
            OperacionSistema(modulo="Logistica y Envios", accion=accion, descripcion=descripcion)
        )
