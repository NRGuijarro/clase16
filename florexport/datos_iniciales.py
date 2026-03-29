from __future__ import annotations

from datetime import date, timedelta

from .modelos import FlorInventario
from .utilidades import a_decimal


CATALOGO_RAMILLETES = [
    {
        "nombre": "Premium",
        "tamano": "Grande",
        "flores_base": 24,
        "precio": a_decimal("99.99"),
        "receta": [
            {"nombre": "Rosa", "color": "Rojo", "cantidad": 10},
            {"nombre": "Rosa", "color": "Blanco", "cantidad": 6},
            {"nombre": "Tulipan", "color": "Amarillo", "cantidad": 4},
            {"nombre": "Orquidea", "color": "Blanco", "cantidad": 4},
        ],
    },
    {
        "nombre": "Clasico",
        "tamano": "Mediano",
        "flores_base": 18,
        "precio": a_decimal("69.99"),
        "receta": [
            {"nombre": "Rosa", "color": "Rosa", "cantidad": 8},
            {"nombre": "Tulipan", "color": "Rojo", "cantidad": 6},
            {"nombre": "Clavel", "color": "Rojo", "cantidad": 4},
        ],
    },
    {
        "nombre": "Pequeno",
        "tamano": "Pequeno",
        "flores_base": 12,
        "precio": a_decimal("49.99"),
        "receta": [
            {"nombre": "Rosa", "color": "Blanco", "cantidad": 6},
            {"nombre": "Girasol", "color": "Amarillo", "cantidad": 4},
            {"nombre": "Lirio", "color": "Blanco", "cantidad": 2},
        ],
    },
    {
        "nombre": "Mini",
        "tamano": "Mini",
        "flores_base": 6,
        "precio": a_decimal("29.99"),
        "receta": [
            {"nombre": "Rosa", "color": "Rojo", "cantidad": 4},
            {"nombre": "Clavel", "color": "Rojo", "cantidad": 2},
        ],
    },
]

TRANSPORTISTAS = [
    {"nombre": "DHL Express", "dias_min": 1, "dias_max": 2, "costo": a_decimal("35.00")},
    {"nombre": "FedEx International", "dias_min": 2, "dias_max": 3, "costo": a_decimal("22.50")},
    {"nombre": "UPS Global", "dias_min": 2, "dias_max": 3, "costo": a_decimal("23.00")},
]


def construir_flores_iniciales() -> list[FlorInventario]:
    return [
        FlorInventario("F001", "Rosa", "Rojo", 182, a_decimal("1.50")),
        FlorInventario("F002", "Rosa", "Blanco", 142, a_decimal("1.50")),
        FlorInventario("F003", "Rosa", "Rosa", 120, a_decimal("1.50")),
        FlorInventario("F004", "Tulipan", "Amarillo", 68, a_decimal("2.00")),
        FlorInventario("F005", "Tulipan", "Rojo", 75, a_decimal("2.00")),
        FlorInventario("F006", "Girasol", "Amarillo", 50, a_decimal("2.50")),
        FlorInventario("F007", "Orquidea", "Blanco", 18, a_decimal("5.00"), stock_minimo=20),
        FlorInventario("F008", "Orquidea", "Morado", 25, a_decimal("5.50"), stock_minimo=20),
        FlorInventario("F009", "Clavel", "Rojo", 100, a_decimal("1.00")),
        FlorInventario("F010", "Lirio", "Blanco", 60, a_decimal("3.00")),
    ]


def construir_pedidos_semilla() -> list[dict[str, object]]:
    hoy = date.today()
    return [
        {
            "cliente": {
                "nombre": "John Smith",
                "correo": "john.smith@example.com",
                "telefono": "+12125551234",
                "pais_destino": "Estados Unidos",
            },
            "direccion_envio": "456 Main St, New York, NY 10001, USA",
            "fecha_entrega": hoy + timedelta(days=3),
            "prioridad": 1,
            "notas": "Cliente VIP con entrega prioritaria.",
            "detalles": [
                {
                    "ramillete": "Clasico",
                    "cantidad": 1,
                    "personalizadas": [
                        {"nombre": "Rosa", "color": "Rojo", "cantidad": 6},
                        {"nombre": "Tulipan", "color": "Amarillo", "cantidad": 6},
                        {"nombre": "Clavel", "color": "Rojo", "cantidad": 6},
                    ],
                },
                {"ramillete": "Mini", "cantidad": 2, "personalizadas": []},
            ],
        },
        {
            "cliente": {
                "nombre": "Maria Gonzalez",
                "correo": "maria@example.com",
                "telefono": "+34612345678",
                "pais_destino": "Espana",
            },
            "direccion_envio": "Calle Principal 123, Madrid, Espana",
            "fecha_entrega": hoy + timedelta(days=5),
            "prioridad": 2,
            "notas": "Incluir tarjeta de felicitacion.",
            "detalles": [
                {
                    "ramillete": "Premium",
                    "cantidad": 2,
                    "personalizadas": [
                        {"nombre": "Rosa", "color": "Rojo", "cantidad": 8},
                        {"nombre": "Rosa", "color": "Blanco", "cantidad": 8},
                        {"nombre": "Tulipan", "color": "Amarillo", "cantidad": 4},
                        {"nombre": "Orquidea", "color": "Blanco", "cantidad": 4},
                    ],
                }
            ],
        },
        {
            "cliente": {
                "nombre": "Ana Lopez",
                "correo": "ana.lopez@example.com",
                "telefono": "+573155555555",
                "pais_destino": "Colombia",
            },
            "direccion_envio": "Cra 10 # 20-30, Bogota, Colombia",
            "fecha_entrega": hoy + timedelta(days=4),
            "prioridad": 2,
            "notas": "Entrega en horario de oficina.",
            "detalles": [{"ramillete": "Pequeno", "cantidad": 1, "personalizadas": []}],
        },
        {
            "cliente": {
                "nombre": "Luis Perez",
                "correo": "luis.perez@example.com",
                "telefono": "+33123456789",
                "pais_destino": "Francia",
            },
            "direccion_envio": "14 Rue de Paris, Lyon, Francia",
            "fecha_entrega": hoy + timedelta(days=6),
            "prioridad": 1,
            "notas": "Requiere embalaje reforzado.",
            "detalles": [{"ramillete": "Mini", "cantidad": 3, "personalizadas": []}],
        },
    ]
