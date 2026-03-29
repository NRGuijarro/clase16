class ErrorSistemaPedidos(Exception):
    """Excepcion base del sistema."""


class ErrorValidacion(ErrorSistemaPedidos):
    """Error de validacion de datos de entrada."""


class ErrorInventario(ErrorSistemaPedidos):
    """Error relacionado con el control de inventario."""


class ErrorPedido(ErrorSistemaPedidos):
    """Error relacionado con el modulo de pedidos."""


class ErrorLogistica(ErrorSistemaPedidos):
    """Error relacionado con el modulo logistico."""
