import unittest

from florexport.datos_iniciales import CATALOGO_RAMILLETES, TRANSPORTISTAS, construir_flores_iniciales
from florexport.excepciones import ErrorInventario, ErrorValidacion
from florexport.modelos import Cliente, FlorPersonalizada
from florexport.servicios import ServicioInventario, ServicioLogistica, ServicioPedidos
from florexport.utilidades import GeneradorIdentificadores


class PruebasFlujoSistema(unittest.TestCase):
    def setUp(self):
        generador = GeneradorIdentificadores(inicio_pedidos=2000, inicio_envios=99000000)
        self.inventario = ServicioInventario(construir_flores_iniciales())
        self.pedidos = ServicioPedidos(self.inventario, generador, CATALOGO_RAMILLETES)
        self.logistica = ServicioLogistica(self.pedidos, generador, TRANSPORTISTAS)
        self.cliente = Cliente(
            nombre="Cliente Prueba",
            correo="cliente.prueba@example.com",
            telefono="+573155551234",
            pais_destino="Chile",
        )

    def test_crear_pedido_descuenta_inventario_base(self):
        stock_inicial = self.inventario.obtener_flor("Rosa", "Rojo").stock
        detalle = self.pedidos.crear_detalle_desde_catalogo("Mini", 2)

        pedido = self.pedidos.crear_pedido(
            cliente=self.cliente,
            detalles=[detalle],
            direccion_envio="Av. Siempre Viva 123",
            fecha_entrega_deseada=self._fecha_futura(3),
        )

        self.assertEqual(pedido.estado, "pendiente")
        self.assertEqual(self.inventario.obtener_flor("Rosa", "Rojo").stock, stock_inicial - 8)

    def test_crear_pedido_personalizado_descuenta_stock_correcto(self):
        stock_orquidea = self.inventario.obtener_flor("Orquidea", "Blanco").stock
        detalle = self.pedidos.crear_detalle_desde_catalogo(
            "Premium",
            1,
            flores_personalizadas=[
                FlorPersonalizada("Rosa", "Rojo", 6),
                FlorPersonalizada("Tulipan", "Amarillo", 6),
                FlorPersonalizada("Orquidea", "Blanco", 4),
            ],
        )

        self.pedidos.crear_pedido(
            cliente=self.cliente,
            detalles=[detalle],
            direccion_envio="Av. Siempre Viva 123",
            fecha_entrega_deseada=self._fecha_futura(4),
        )

        self.assertEqual(self.inventario.obtener_flor("Orquidea", "Blanco").stock, stock_orquidea - 4)

    def test_no_permite_pedido_sin_stock_suficiente(self):
        detalle = self.pedidos.crear_detalle_desde_catalogo("Premium", 5)

        with self.assertRaises(ErrorInventario):
            self.pedidos.crear_pedido(
                cliente=self.cliente,
                detalles=[detalle],
                direccion_envio="Av. Siempre Viva 123",
                fecha_entrega_deseada=self._fecha_futura(2),
            )

    def test_modificar_pedido_recalcula_inventario(self):
        stock_rojas = self.inventario.obtener_flor("Rosa", "Rojo").stock
        detalle_inicial = self.pedidos.crear_detalle_desde_catalogo("Mini", 1)
        pedido = self.pedidos.crear_pedido(
            cliente=self.cliente,
            detalles=[detalle_inicial],
            direccion_envio="Av. Siempre Viva 123",
            fecha_entrega_deseada=self._fecha_futura(3),
        )

        detalle_nuevo = self.pedidos.crear_detalle_desde_catalogo("Pequeno", 1)
        self.pedidos.modificar_pedido(
            identificador=pedido.identificador,
            detalles=[detalle_nuevo],
            cliente=self.cliente,
        )

        self.assertEqual(self.inventario.obtener_flor("Rosa", "Rojo").stock, stock_rojas)
        self.assertEqual(self.inventario.obtener_flor("Lirio", "Blanco").stock, 58)

    def test_eliminar_pedido_reintegra_stock(self):
        stock_inicial = self.inventario.obtener_flor("Clavel", "Rojo").stock
        detalle = self.pedidos.crear_detalle_desde_catalogo("Mini", 1)
        pedido = self.pedidos.crear_pedido(
            cliente=self.cliente,
            detalles=[detalle],
            direccion_envio="Av. Siempre Viva 123",
            fecha_entrega_deseada=self._fecha_futura(5),
        )

        self.pedidos.eliminar_pedido(pedido.identificador)

        self.assertEqual(self.inventario.obtener_flor("Clavel", "Rojo").stock, stock_inicial)

    def test_logistica_prepara_despacha_y_entrega(self):
        detalle = self.pedidos.crear_detalle_desde_catalogo("Clasico", 1)
        pedido = self.pedidos.crear_pedido(
            cliente=self.cliente,
            detalles=[detalle],
            direccion_envio="Av. Siempre Viva 123",
            fecha_entrega_deseada=self._fecha_futura(3),
            prioridad=1,
        )

        envio = self.logistica.preparar_envio(pedido.identificador, "DHL Express")
        self.assertEqual(self.pedidos.buscar_pedido_por_id(pedido.identificador).estado, "en_preparacion")

        self.logistica.registrar_despacho(pedido.identificador)
        self.logistica.actualizar_estado_envio(envio.numero_seguimiento, "entregado")

        pedido_actualizado = self.pedidos.buscar_pedido_por_id(pedido.identificador)
        self.assertEqual(pedido_actualizado.estado, "entregado")
        self.assertGreaterEqual(len(self.logistica.rastrear_envio(envio.numero_seguimiento).historial), 3)

    def test_valida_correo_y_telefono(self):
        cliente_invalido = Cliente(
            nombre="Cliente Invalido",
            correo="correo-invalido",
            telefono="123",
            pais_destino="Chile",
        )
        detalle = self.pedidos.crear_detalle_desde_catalogo("Mini", 1)

        with self.assertRaises(ErrorValidacion):
            self.pedidos.crear_pedido(
                cliente=cliente_invalido,
                detalles=[detalle],
                direccion_envio="Direccion de prueba",
                fecha_entrega_deseada=self._fecha_futura(3),
            )

    @staticmethod
    def _fecha_futura(dias):
        from datetime import date, timedelta

        return date.today() + timedelta(days=dias)


if __name__ == "__main__":
    unittest.main()
