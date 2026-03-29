from __future__ import annotations

from .datos_iniciales import CATALOGO_RAMILLETES, TRANSPORTISTAS, construir_flores_iniciales, construir_pedidos_semilla
from .modelos import Cliente, DetalleRamillete, FlorPersonalizada
from .servicios.servicio_inventario import ServicioInventario
from .servicios.servicio_logistica import ServicioLogistica
from .servicios.servicio_pedidos import ServicioPedidos
from .utilidades import GeneradorIdentificadores


def construir_servicios() -> tuple[ServicioInventario, ServicioPedidos, ServicioLogistica]:
    generador = GeneradorIdentificadores()
    inventario = ServicioInventario(construir_flores_iniciales())
    pedidos = ServicioPedidos(inventario, generador, CATALOGO_RAMILLETES)
    logistica = ServicioLogistica(pedidos, generador, TRANSPORTISTAS)
    pedidos_creados = _cargar_pedidos_semilla(pedidos)
    _cargar_envios_semilla(logistica, pedidos_creados)
    return inventario, pedidos, logistica


def construir_aplicacion():
    from .interfaz.consola import AplicacionConsola

    inventario, pedidos, logistica = construir_servicios()
    return AplicacionConsola(pedidos=pedidos, inventario=inventario, logistica=logistica)


def _cargar_pedidos_semilla(servicio_pedidos: ServicioPedidos):
    pedidos_creados = []
    for especificacion in construir_pedidos_semilla():
        cliente = Cliente(**especificacion["cliente"])
        detalles = []
        for detalle in especificacion["detalles"]:
            configuracion = servicio_pedidos.obtener_configuracion_ramillete(detalle["ramillete"])
            receta_base = servicio_pedidos.construir_receta(configuracion)
            flores_personalizadas = [
                FlorPersonalizada(
                    nombre=flor["nombre"],
                    color=flor["color"],
                    cantidad_tallos_por_ramillete=flor["cantidad"],
                )
                for flor in detalle["personalizadas"]
            ]
            detalles.append(
                DetalleRamillete(
                    nombre_ramillete=configuracion["nombre"],
                    tamano=configuracion["tamano"],
                    cantidad_ramilletes=detalle["cantidad"],
                    flores_base=configuracion["flores_base"],
                    precio_unitario=configuracion["precio"],
                    receta_base=receta_base,
                    flores_personalizadas=flores_personalizadas,
                )
            )
        pedidos_creados.append(
            servicio_pedidos.crear_pedido(
                cliente=cliente,
                detalles=detalles,
                direccion_envio=especificacion["direccion_envio"],
                fecha_entrega_deseada=especificacion["fecha_entrega"],
                prioridad=especificacion["prioridad"],
                notas=especificacion["notas"],
            )
        )
    return pedidos_creados


def _cargar_envios_semilla(servicio_logistica: ServicioLogistica, pedidos_creados):
    if not pedidos_creados:
        return

    primer_pedido = pedidos_creados[0]
    envio_uno = servicio_logistica.preparar_envio(primer_pedido.identificador, "DHL Express")
    servicio_logistica.registrar_despacho(primer_pedido.identificador)
    servicio_logistica.actualizar_estado_envio(
        envio_uno.numero_seguimiento,
        "en_transito",
        "Paquete en centro de distribucion de Madrid.",
    )

    if len(pedidos_creados) > 1:
        segundo_pedido = pedidos_creados[1]
        servicio_logistica.preparar_envio(segundo_pedido.identificador, "FedEx International")
