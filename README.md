# Sistema de Gestion de Pedidos FloraExport

Aplicacion de consola en Python para gestionar pedidos de ramilletes de flores, inventario y logistica de envios internacionales.

El proyecto implementa los tres modulos solicitados en el plan original:

- Gestion de Pedidos
- Inventario de Flores
- Logistica y Envios

Tambien incorpora validaciones de entrada, manejo de errores, estructuras de datos dinamicas y pruebas automatizadas para verificar el flujo completo del sistema.

## Caracteristicas implementadas

### Modulo de Gestion de Pedidos

- Creacion de pedidos con datos de cliente, direccion, fecha de entrega, prioridad y notas.
- Personalizacion de ramilletes por tipo de flor, color y cantidad de tallos por ramillete.
- Modificacion de pedidos pendientes o en preparacion.
- Eliminacion de pedidos pendientes con reintegro automatico del inventario.
- Busqueda de pedidos por identificador unico.
- Listado de pedidos por estado.
- Historial de operaciones del modulo utilizando una pila.

### Modulo de Inventario de Flores

- Inventario cargado sobre una lista enlazada.
- Consulta completa de stock disponible.
- Busqueda por nombre o color.
- Registro de nuevos lotes o nuevas variedades de flores.
- Ajuste manual de stock con motivo asociado.
- Alertas de stock bajo.
- Historial de movimientos de inventario en estructura de pila.

### Modulo de Logistica y Envios

- Cola dinamica priorizada para pedidos pendientes de preparacion.
- Preparacion de pedidos para envio con asignacion de transportista.
- Registro de despacho.
- Actualizacion de estado de envio.
- Rastreo por ID de pedido o numero de seguimiento.
- Informe general de logistica.

## Estructuras de datos utilizadas

- Lista enlazada: almacenamiento de pedidos e inventario.
- Pila: historial de operaciones y movimientos recientes.
- Cola dinamica con prioridad: organizacion de pedidos pendientes para envio.

## Validaciones y manejo de errores

- Campos obligatorios para cliente y pedido.
- Validacion de correo electronico.
- Validacion de telefono internacional con 10 a 15 digitos.
- Validacion de cantidades positivas.
- Verificacion de stock suficiente antes de registrar o modificar pedidos.
- Rollback del inventario si ocurre un error durante modificaciones importantes.
- Restricciones para impedir eliminar pedidos que ya entraron en flujo logistico.

## Datos de demostracion

Al iniciar la aplicacion se cargan:

- Flores base de inventario.
- Catalogo de ramilletes.
- Pedidos de ejemplo.
- Envios semilla para demostrar rastreo y estados logisticos.

Esto permite probar el sistema desde el primer arranque sin cargar informacion manualmente.

## Estructura del proyecto

```text
clase16/
|-- main.py
|-- README.md
|-- florexport/
|   |-- bootstrap.py
|   |-- datos_iniciales.py
|   |-- excepciones.py
|   |-- modelos.py
|   |-- utilidades.py
|   |-- validaciones.py
|   |-- estructuras/
|   |   |-- lista_enlazada.py
|   |   |-- pila.py
|   |   |-- cola_prioridad.py
|   |-- servicios/
|   |   |-- servicio_pedidos.py
|   |   |-- servicio_inventario.py
|   |   |-- servicio_logistica.py
|   |-- interfaz/
|       |-- consola.py
|-- tests/
|   |-- test_estructuras.py
|   |-- test_flujo_sistema.py
```

## Requisitos tecnicos

- Python 3.14 o superior
- Sin dependencias externas

## Como ejecutar

Desde la carpeta del proyecto:

```bash
python main.py
```

En este entorno la ruta completa del interprete configurado es:

```bash
C:/Users/Nelson/AppData/Local/Programs/Python/Python314/python.exe main.py
```

## Como ejecutar las pruebas

```bash
python -m unittest discover -s tests -v
```

En este entorno:

```bash
C:/Users/Nelson/AppData/Local/Programs/Python/Python314/python.exe -m unittest discover -s tests -v
```

## Cobertura del plan solicitado

### Requisitos funcionales

- Personalizacion de pedidos: cubierta.
- Registro y seguimiento de pedidos: cubierto.
- Actualizacion automatica del inventario: cubierta.
- Organizacion de envios por prioridad: cubierta.
- Cambio de estado del pedido durante el flujo: cubierto.
- Busqueda por identificador unico: cubierta.

### Requisitos de estructuras de datos

- Listas enlazadas para pedidos: implementadas.
- Uso de pila para historial: implementado.
- Cola FIFO priorizada para envios: implementada.
- Indices por clave unica para agilizar busquedas: implementados.

### Requisitos de validacion

- Datos incompletos: cubiertos.
- Correo y telefono invalidos: cubiertos.
- Solicitud superior al inventario: cubierta.
- Manejo de excepciones por modulo: cubierto.

## Pruebas automatizadas incluidas

- Operaciones de lista enlazada.
- Comportamiento LIFO de la pila.
- Prioridad y orden FIFO de la cola.
- Creacion de pedidos y descuento de inventario.
- Personalizacion de ramilletes.
- Bloqueo por stock insuficiente.
- Modificacion de pedidos con recalculo de inventario.
- Eliminacion con reintegro de stock.
- Flujo logistico completo hasta entrega.
- Validaciones de cliente.

## Observaciones finales

- Todo el codigo, nombres de variables y mensajes principales estan en espanol.
- Se agregaron comentarios solo en las secciones donde el flujo interno requiere contexto adicional.
- La solucion esta orientada a demostracion academica, con datos en memoria y menus de consola claros para exposicion o sustentacion.