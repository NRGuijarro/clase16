from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal


ESTADOS_PEDIDO_VALIDOS = (
    "pendiente",
    "en_preparacion",
    "enviado",
    "entregado",
    "cancelado",
)

ESTADOS_ENVIO_VALIDOS = (
    "en_preparacion",
    "en_transito",
    "entregado",
    "incidencia",
)


@dataclass(slots=True)
class Cliente:
    nombre: str
    correo: str
    telefono: str
    pais_destino: str


@dataclass(slots=True)
class FlorPersonalizada:
    nombre: str
    color: str
    cantidad_tallos_por_ramillete: int


@dataclass(slots=True)
class DetalleRamillete:
    nombre_ramillete: str
    tamano: str
    cantidad_ramilletes: int
    flores_base: int
    precio_unitario: Decimal
    receta_base: list[FlorPersonalizada] = field(default_factory=list)
    flores_personalizadas: list[FlorPersonalizada] = field(default_factory=list)
    notas: str = ""

    @property
    def total(self) -> Decimal:
        return self.precio_unitario * self.cantidad_ramilletes

    @property
    def personalizado(self) -> bool:
        return bool(self.flores_personalizadas)

    def obtener_flores_aplicadas(self) -> list[FlorPersonalizada]:
        return self.flores_personalizadas or self.receta_base

    def descripcion_corta(self) -> str:
        sufijo = " (Personalizado)" if self.personalizado else ""
        return f"{self.cantidad_ramilletes}x {self.nombre_ramillete}{sufijo}"


@dataclass(slots=True)
class Pedido:
    identificador: str
    cliente: Cliente
    detalles: list[DetalleRamillete]
    direccion_envio: str
    fecha_registro: datetime
    fecha_entrega_deseada: date
    estado: str = "pendiente"
    prioridad: int = 2
    notas: str = ""
    numero_seguimiento: str | None = None
    transportista: str | None = None
    fecha_estimada_entrega: date | None = None

    @property
    def total(self) -> Decimal:
        acumulado = Decimal("0.00")
        for detalle in self.detalles:
            acumulado += detalle.total
        return acumulado

    @property
    def destino(self) -> str:
        return self.cliente.pais_destino

    @property
    def prioridad_legible(self) -> str:
        return "URGENTE" if self.prioridad == 1 else "REGULAR"

    @property
    def estado_legible(self) -> str:
        equivalencias = {
            "pendiente": "Pendiente",
            "en_preparacion": "En preparacion",
            "enviado": "Enviado",
            "entregado": "Entregado",
            "cancelado": "Cancelado",
        }
        return equivalencias.get(self.estado, self.estado)

    def resumen_productos(self) -> str:
        return ", ".join(detalle.descripcion_corta() for detalle in self.detalles)

    def resumen_flores(self) -> str:
        fragmentos: list[str] = []
        for detalle in self.detalles:
            flores = []
            for flor in detalle.obtener_flores_aplicadas():
                flores.append(
                    f"{flor.nombre} ({flor.color}) x{flor.cantidad_tallos_por_ramillete}/ramillete"
                )
            fragmentos.append(f"{detalle.nombre_ramillete}: " + ", ".join(flores))
        return " | ".join(fragmentos)


@dataclass(slots=True)
class FlorInventario:
    codigo: str
    nombre: str
    color: str
    stock: int
    precio_unitario: Decimal
    stock_minimo: int = 20


@dataclass(slots=True)
class MovimientoInventario:
    tipo: str
    nombre_flor: str
    color: str
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    fecha_hora: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class OperacionSistema:
    modulo: str
    accion: str
    descripcion: str
    fecha_hora: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class EventoSeguimiento:
    descripcion: str
    fecha_hora: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class Envio:
    identificador_pedido: str
    cliente: str
    origen: str
    destino: str
    transportista: str
    numero_seguimiento: str
    estado_actual: str
    fecha_estimada_entrega: date
    historial: list[EventoSeguimiento] = field(default_factory=list)

    def registrar_evento(self, descripcion: str, estado_actual: str | None = None) -> None:
        self.historial.append(EventoSeguimiento(descripcion=descripcion))
        if estado_actual is not None:
            self.estado_actual = estado_actual
