from __future__ import annotations

from datetime import datetime

from ..excepciones import ErrorSistemaPedidos
from ..modelos import Cliente, FlorPersonalizada
from ..utilidades import formatear_fecha, formatear_fecha_hora, formatear_moneda


class AplicacionConsola:
    def __init__(self, pedidos, inventario, logistica) -> None:
        self.pedidos = pedidos
        self.inventario = inventario
        self.logistica = logistica

    def ejecutar(self) -> None:
        while True:
            self._mostrar_menu_principal()
            opcion = self._leer_opcion("Seleccione una opcion: ", {"1", "2", "3", "4"})
            try:
                if opcion == "1":
                    self._menu_pedidos()
                elif opcion == "2":
                    self._menu_inventario()
                elif opcion == "3":
                    self._menu_logistica()
                else:
                    print("\nSistema finalizado correctamente.")
                    return
            except ErrorSistemaPedidos as error:
                print(f"\n{error}")
                self._pausar()

    def _mostrar_menu_principal(self) -> None:
        print("\n===== SISTEMA DE GESTION DE PEDIDOS FLORAEXPORT =====")
        print(f"Fecha: {formatear_fecha_hora(datetime.now())}")
        print("\nSeleccione un modulo:")
        print("1. Modulo de Gestion de Pedidos")
        print("2. Modulo de Inventario de Flores")
        print("3. Modulo de Logistica y Envios")
        print("4. Salir")

    def _menu_pedidos(self) -> None:
        while True:
            print("\n===== MODULO DE GESTION DE PEDIDOS =====")
            print("1. Crear nuevo pedido")
            print("2. Modificar pedido existente")
            print("3. Eliminar pedido")
            print("4. Buscar pedido por ID")
            print("5. Listar pedidos por estado")
            print("6. Ver historial de cambios")
            print("7. Volver al menu principal")
            opcion = self._leer_opcion("Seleccione una opcion: ", {"1", "2", "3", "4", "5", "6", "7"})
            try:
                if opcion == "1":
                    self._crear_pedido()
                elif opcion == "2":
                    self._modificar_pedido()
                elif opcion == "3":
                    self._eliminar_pedido()
                elif opcion == "4":
                    self._buscar_pedido()
                elif opcion == "5":
                    self._listar_pedidos_por_estado()
                elif opcion == "6":
                    self._ver_historial_pedidos()
                else:
                    return
            except ErrorSistemaPedidos as error:
                print(f"\n{error}")
            self._pausar()

    def _menu_inventario(self) -> None:
        while True:
            print("\n===== MODULO DE INVENTARIO DE FLORES =====")
            print("1. Ver inventario completo")
            print("2. Buscar flor por nombre/color")
            print("3. Registrar nuevo lote de flores")
            print("4. Actualizar stock manualmente")
            print("5. Ver alertas de stock")
            print("6. Ver movimientos recientes")
            print("7. Volver al menu principal")
            opcion = self._leer_opcion("Seleccione una opcion: ", {"1", "2", "3", "4", "5", "6", "7"})
            try:
                if opcion == "1":
                    self._ver_inventario_completo()
                elif opcion == "2":
                    self._buscar_flor_inventario()
                elif opcion == "3":
                    self._registrar_lote_inventario()
                elif opcion == "4":
                    self._actualizar_stock_manual()
                elif opcion == "5":
                    self._ver_alertas_stock()
                elif opcion == "6":
                    self._ver_movimientos_inventario()
                else:
                    return
            except ErrorSistemaPedidos as error:
                print(f"\n{error}")
            self._pausar()

    def _menu_logistica(self) -> None:
        while True:
            print("\n===== MODULO DE LOGISTICA Y ENVIOS =====")
            print("1. Ver cola de envios")
            print("2. Preparar pedido para envio")
            print("3. Registrar despacho de envio")
            print("4. Actualizar estado de envio")
            print("5. Rastrear envio")
            print("6. Generar informe de logistica")
            print("7. Volver al menu principal")
            opcion = self._leer_opcion("Seleccione una opcion: ", {"1", "2", "3", "4", "5", "6", "7"})
            try:
                if opcion == "1":
                    self._ver_cola_envios()
                elif opcion == "2":
                    self._preparar_pedido_para_envio()
                elif opcion == "3":
                    self._registrar_despacho_envio()
                elif opcion == "4":
                    self._actualizar_estado_envio()
                elif opcion == "5":
                    self._rastrear_envio()
                elif opcion == "6":
                    self._generar_informe_logistica()
                else:
                    return
            except ErrorSistemaPedidos as error:
                print(f"\n{error}")
            self._pausar()

    def _crear_pedido(self) -> None:
        print("\n----- CREAR NUEVO PEDIDO -----")
        cliente = Cliente(
            nombre=self._leer_texto("Nombre: "),
            correo=self._leer_texto("Email: "),
            telefono=self._leer_texto("Telefono: "),
            pais_destino=self._leer_texto("Pais de destino: "),
        )
        detalles = self._capturar_detalles_pedido()
        direccion = self._leer_texto("Direccion de envio: ")
        fecha_entrega = self._leer_fecha("Fecha de entrega deseada (DD/MM/AAAA): ")
        notas = self._leer_texto("Notas adicionales (opcional): ", obligatorio=False)
        prioridad = 1 if self._leer_confirmacion("Es un pedido urgente? (s/n): ") else 2

        self._mostrar_resumen_preliminar(cliente, detalles, direccion, fecha_entrega, prioridad, notas)
        if not self._leer_confirmacion("Confirmar pedido? (s/n): "):
            print("Pedido cancelado por el usuario antes de registrarse.")
            return

        pedido = self.pedidos.crear_pedido(
            cliente=cliente,
            detalles=detalles,
            direccion_envio=direccion,
            fecha_entrega_deseada=fecha_entrega,
            prioridad=prioridad,
            notas=notas,
        )
        print("\nPedido creado exitosamente.")
        self._mostrar_detalle_pedido(pedido)

    def _modificar_pedido(self) -> None:
        print("\n----- MODIFICAR PEDIDO -----")
        identificador = self._leer_texto("Ingrese el ID del pedido: ").upper()
        pedido = self.pedidos.buscar_pedido_por_id(identificador)
        self._mostrar_detalle_pedido(pedido)
        print("\nDeje vacio cualquier campo que no desee cambiar.")

        nombre = self._leer_texto(f"Nombre [{pedido.cliente.nombre}]: ", obligatorio=False) or pedido.cliente.nombre
        correo = self._leer_texto(f"Email [{pedido.cliente.correo}]: ", obligatorio=False) or pedido.cliente.correo
        telefono = self._leer_texto(f"Telefono [{pedido.cliente.telefono}]: ", obligatorio=False) or pedido.cliente.telefono
        pais = self._leer_texto(
            f"Pais de destino [{pedido.cliente.pais_destino}]: ", obligatorio=False
        ) or pedido.cliente.pais_destino
        direccion = self._leer_texto(
            f"Direccion de envio [{pedido.direccion_envio}]: ", obligatorio=False
        ) or pedido.direccion_envio
        fecha_texto = self._leer_texto(
            f"Fecha de entrega [{formatear_fecha(pedido.fecha_entrega_deseada)}] (DD/MM/AAAA): ",
            obligatorio=False,
        )
        fecha_nueva = (
            datetime.strptime(fecha_texto, "%d/%m/%Y").date() if fecha_texto else pedido.fecha_entrega_deseada
        )
        prioridad_texto = self._leer_texto(
            f"Prioridad actual {pedido.prioridad_legible} (1 urgente / 2 regular): ",
            obligatorio=False,
        )
        prioridad_nueva = int(prioridad_texto) if prioridad_texto else pedido.prioridad
        notas = self._leer_texto(f"Notas [{pedido.notas or 'Sin notas'}]: ", obligatorio=False)
        notas_nuevas = notas if notas else pedido.notas
        detalles_nuevos = None
        if self._leer_confirmacion("Desea reemplazar la composicion del pedido? (s/n): "):
            detalles_nuevos = self._capturar_detalles_pedido()

        cliente_nuevo = Cliente(nombre=nombre, correo=correo, telefono=telefono, pais_destino=pais)
        pedido_actualizado = self.pedidos.modificar_pedido(
            identificador=identificador,
            cliente=cliente_nuevo,
            detalles=detalles_nuevos,
            direccion_envio=direccion,
            fecha_entrega_deseada=fecha_nueva,
            prioridad=prioridad_nueva,
            notas=notas_nuevas,
        )
        print("\nPedido actualizado correctamente.")
        self._mostrar_detalle_pedido(pedido_actualizado)

    def _eliminar_pedido(self) -> None:
        print("\n----- ELIMINAR PEDIDO -----")
        identificador = self._leer_texto("Ingrese el ID del pedido: ").upper()
        pedido = self.pedidos.buscar_pedido_por_id(identificador)
        self._mostrar_detalle_pedido(pedido)
        if not self._leer_confirmacion("Confirma la eliminacion de este pedido? (s/n): "):
            print("El pedido no fue eliminado.")
            return
        self.pedidos.eliminar_pedido(identificador)
        print(f"Pedido {identificador} eliminado correctamente.")

    def _buscar_pedido(self) -> None:
        print("\n----- BUSCAR PEDIDO -----")
        identificador = self._leer_texto("Ingrese el ID del pedido: ").upper()
        pedido = self.pedidos.buscar_pedido_por_id(identificador)
        self._mostrar_detalle_pedido(pedido)

    def _listar_pedidos_por_estado(self) -> None:
        print("\n----- LISTAR PEDIDOS POR ESTADO -----")
        print("1. Pendiente")
        print("2. En preparacion")
        print("3. Enviado")
        print("4. Entregado")
        opciones_estado = {"1": "pendiente", "2": "en_preparacion", "3": "enviado", "4": "entregado"}
        opcion = self._leer_opcion("Seleccione estado: ", set(opciones_estado))
        pedidos = self.pedidos.listar_pedidos_por_estado(opciones_estado[opcion])
        if not pedidos:
            print("No existen pedidos en el estado solicitado.")
            return
        print()
        for pedido in pedidos:
            print(
                f"- {pedido.identificador} | {pedido.cliente.nombre} | {pedido.estado_legible} | "
                f"{pedido.prioridad_legible} | {formatear_fecha(pedido.fecha_entrega_deseada)} | "
                f"{formatear_moneda(pedido.total)}"
            )

    def _ver_historial_pedidos(self) -> None:
        print("\n----- HISTORIAL DE PEDIDOS -----")
        historial = self.pedidos.obtener_historial_operaciones()
        if not historial:
            print("No hay operaciones registradas.")
            return
        for operacion in historial:
            print(
                f"- {formatear_fecha_hora(operacion.fecha_hora)} | {operacion.accion} | {operacion.descripcion}"
            )

    def _ver_inventario_completo(self) -> None:
        print("\n----- INVENTARIO COMPLETO DE FLORES -----")
        flores = self.inventario.listar_inventario()
        print("Estructura actual: Lista enlazada de inventario\n")
        print("ID    | Nombre    | Color     | Stock | Precio")
        print("------|-----------|-----------|-------|-------")
        for flor in flores:
            etiqueta = " [STOCK BAJO]" if flor.stock <= flor.stock_minimo else ""
            print(
                f"{flor.codigo:<5} | {flor.nombre:<9} | {flor.color:<9} | {flor.stock:<5} | "
                f"{formatear_moneda(flor.precio_unitario)}{etiqueta}"
            )
        print(f"\nTotal de flores en inventario: {self.inventario.total_stock()}")
        print(f"Flores con stock bajo: {len(self.inventario.obtener_alertas_stock_bajo())}")

    def _buscar_flor_inventario(self) -> None:
        print("\n----- BUSCAR FLOR EN INVENTARIO -----")
        nombre = self._leer_texto("Nombre de flor (opcional): ", obligatorio=False)
        color = self._leer_texto("Color (opcional): ", obligatorio=False)
        resultados = self.inventario.buscar_flores(nombre=nombre, color=color)
        if not resultados:
            print("No se encontraron flores con esos criterios.")
            return
        for flor in resultados:
            print(
                f"- {flor.codigo} | {flor.nombre} {flor.color} | Stock: {flor.stock} | "
                f"Precio: {formatear_moneda(flor.precio_unitario)}"
            )

    def _registrar_lote_inventario(self) -> None:
        print("\n----- REGISTRAR NUEVO LOTE DE FLORES -----")
        existentes = sorted({flor.nombre for flor in self.inventario.listar_inventario()})
        print("Flores existentes:")
        for indice, nombre in enumerate(existentes, start=1):
            print(f"{indice}. {nombre}")
        nombre = self._leer_texto("Nombre de flor: ")
        color = self._leer_texto("Color: ")
        cantidad = self._leer_entero("Cantidad de flores en el lote: ", minimo=1)
        precio = self._leer_texto(
            "Precio por unidad (deje vacio para mantener el actual si ya existe): ",
            obligatorio=False,
        )
        flor, movimiento = self.inventario.registrar_lote(
            nombre=nombre,
            color=color,
            cantidad=cantidad,
            precio_unitario=precio or None,
        )
        print("\nActualizacion de inventario:")
        print(f"{flor.nombre} ({flor.color}) ahora tiene stock {flor.stock}.")
        print(
            f"Movimiento: {movimiento.tipo} | Cantidad: {movimiento.cantidad:+d} | "
            f"Hora: {formatear_fecha_hora(movimiento.fecha_hora)}"
        )

    def _actualizar_stock_manual(self) -> None:
        print("\n----- ACTUALIZAR STOCK MANUALMENTE -----")
        referencia = self._leer_texto("Codigo o nombre de la flor: ")
        color = self._leer_texto("Color (si ingreso nombre): ", obligatorio=False)
        ajuste = self._leer_entero("Ajuste de stock (use negativo para descuentos): ", permitir_negativos=True)
        motivo = self._leer_texto("Motivo del ajuste: ")
        flor, movimiento = self.inventario.actualizar_stock_manual(referencia, color, ajuste, motivo)
        print(
            f"Stock actualizado para {flor.nombre} {flor.color}: {movimiento.stock_anterior} -> {movimiento.stock_nuevo}"
        )

    def _ver_alertas_stock(self) -> None:
        print("\n----- ALERTAS DE STOCK BAJO -----")
        alertas = self.inventario.obtener_alertas_stock_bajo()
        if not alertas:
            print("No hay alertas de stock bajo en este momento.")
            return
        for flor in alertas:
            print(
                f"- {flor.codigo} | {flor.nombre} {flor.color} | Stock actual: {flor.stock} | "
                f"Minimo: {flor.stock_minimo}"
            )

    def _ver_movimientos_inventario(self) -> None:
        print("\n----- MOVIMIENTOS RECIENTES DE INVENTARIO -----")
        movimientos = self.inventario.obtener_historial_movimientos()
        if not movimientos:
            print("No hay movimientos registrados.")
            return
        for movimiento in movimientos:
            print(
                f"- {formatear_fecha_hora(movimiento.fecha_hora)} | {movimiento.tipo} | "
                f"{movimiento.nombre_flor} {movimiento.color} | {movimiento.cantidad:+d} | "
                f"{movimiento.stock_anterior} -> {movimiento.stock_nuevo}"
            )

    def _ver_cola_envios(self) -> None:
        print("\n----- COLA DE ENVIOS -----")
        pedidos = self.logistica.listar_cola_envios()
        if not pedidos:
            print("No hay pedidos pendientes de preparacion.")
            return

        urgentes = [pedido for pedido in pedidos if pedido.prioridad == 1]
        regulares = [pedido for pedido in pedidos if pedido.prioridad == 2]
        if urgentes:
            print("Envios prioritarios:")
            for pedido in urgentes:
                print(
                    f"- {pedido.identificador} - {pedido.cliente.nombre} - {pedido.destino} - "
                    f"Fecha entrega: {formatear_fecha(pedido.fecha_entrega_deseada)} [URGENTE]"
                )
        if regulares:
            print("\nEnvios regulares:")
            for pedido in regulares:
                print(
                    f"- {pedido.identificador} - {pedido.cliente.nombre} - {pedido.destino} - "
                    f"Fecha entrega: {formatear_fecha(pedido.fecha_entrega_deseada)}"
                )

    def _preparar_pedido_para_envio(self) -> None:
        print("\n----- PREPARAR PEDIDO PARA ENVIO -----")
        pendientes = self.logistica.listar_cola_envios()
        if not pendientes:
            print("No hay pedidos en cola para preparar.")
            return
        for pedido in pendientes:
            print(
                f"- {pedido.identificador} | {pedido.cliente.nombre} | {pedido.destino} | "
                f"{pedido.resumen_productos()}"
            )
        identificador = self._leer_texto("Seleccione el ID del pedido: ").upper()

        print("\nTransportistas disponibles:")
        transportistas = self.logistica.listar_transportistas()
        for indice, transportista in enumerate(transportistas, start=1):
            print(
                f"{indice}. {transportista['nombre']} ({transportista['dias_min']}-{transportista['dias_max']} dias) - "
                f"{formatear_moneda(transportista['costo'])}"
            )
        seleccion = self._leer_entero("Seleccione transportista: ", minimo=1, maximo=len(transportistas))
        envio = self.logistica.preparar_envio(identificador, transportistas[seleccion - 1]["nombre"])
        print(f"\nNumero de seguimiento generado: {envio.numero_seguimiento}")
        print(f"Transportista: {envio.transportista}")
        print(f"Fecha estimada de entrega: {formatear_fecha(envio.fecha_estimada_entrega)}")

    def _registrar_despacho_envio(self) -> None:
        print("\n----- REGISTRAR DESPACHO DE ENVIO -----")
        pedidos_preparacion = self.logistica.listar_pedidos_en_preparacion()
        if not pedidos_preparacion:
            print("No hay pedidos en preparacion listos para despacho.")
            return
        for pedido in pedidos_preparacion:
            print(f"- {pedido.identificador} | {pedido.cliente.nombre} | Seguimiento: {pedido.numero_seguimiento}")
        identificador = self._leer_texto("Seleccione el ID del pedido a despachar: ").upper()
        envio = self.logistica.registrar_despacho(identificador)
        print(f"Despacho registrado. Estado actual: {envio.estado_actual}")

    def _actualizar_estado_envio(self) -> None:
        print("\n----- ACTUALIZAR ESTADO DE ENVIO -----")
        referencia = self._leer_texto("Ingrese numero de seguimiento o ID del pedido: ").upper()
        print("1. En preparacion")
        print("2. En transito")
        print("3. Entregado")
        print("4. Incidencia")
        mapa = {"1": "en_preparacion", "2": "en_transito", "3": "entregado", "4": "incidencia"}
        opcion = self._leer_opcion("Seleccione nuevo estado: ", set(mapa))
        descripcion = self._leer_texto("Descripcion del evento (opcional): ", obligatorio=False)
        envio = self.logistica.actualizar_estado_envio(referencia, mapa[opcion], descripcion or None)
        print(f"Estado del envio actualizado a: {envio.estado_actual}")

    def _rastrear_envio(self) -> None:
        print("\n----- RASTREAR ENVIO -----")
        referencia = self._leer_texto("Ingrese numero de seguimiento o ID del pedido: ").upper()
        envio = self.logistica.rastrear_envio(referencia)
        print(f"Pedido: {envio.identificador_pedido}")
        print(f"Cliente: {envio.cliente}")
        print(f"Origen: {envio.origen}")
        print(f"Destino: {envio.destino}")
        print(f"Estado actual: {envio.estado_actual}")
        print(f"Transportista: {envio.transportista}")
        print(f"Fecha estimada de entrega: {formatear_fecha(envio.fecha_estimada_entrega)}")
        print("\nHistorial de seguimiento:")
        for evento in envio.historial:
            print(f"- {formatear_fecha_hora(evento.fecha_hora)} - {evento.descripcion}")

    def _generar_informe_logistica(self) -> None:
        print("\n----- INFORME DE LOGISTICA -----")
        informe = self.logistica.generar_informe_logistica()
        print(f"Pedidos pendientes en cola: {informe['pedidos_pendientes']}")
        print(f"Pedidos en preparacion: {informe['pedidos_en_preparacion']}")
        print(f"Pedidos enviados: {informe['pedidos_enviados']}")
        print(f"Pedidos entregados: {informe['pedidos_entregados']}")
        print("\nDistribucion por destino:")
        for destino, cantidad in informe["destinos"].items():
            print(f"- {destino}: {cantidad}")
        print("\nUso de transportistas:")
        if not informe["transportistas"]:
            print("- Aun no se han generado envios.")
        else:
            for transportista, cantidad in informe["transportistas"].items():
                print(f"- {transportista}: {cantidad}")

    def _capturar_detalles_pedido(self):
        detalles = []
        while True:
            print("\nRamilletes disponibles:")
            catalogo = self.pedidos.listar_catalogo_ramilletes()
            for indice, ramillete in enumerate(catalogo, start=1):
                print(
                    f"{indice}. {ramillete['nombre']} ({ramillete['flores_base']} flores) - "
                    f"{formatear_moneda(ramillete['precio'])}"
                )
            seleccion = self._leer_entero(
                f"Seleccione tipo de ramillete (1-{len(catalogo)}): ",
                minimo=1,
                maximo=len(catalogo),
            )
            configuracion = catalogo[seleccion - 1]
            cantidad = self._leer_entero("Cantidad: ", minimo=1)
            flores_personalizadas = []
            notas_detalle = ""
            if self._leer_confirmacion("Desea personalizar los ramilletes? (s/n): "):
                flores_personalizadas = self._capturar_personalizacion()
                notas_detalle = self._leer_texto("Notas del ramillete (opcional): ", obligatorio=False)

            detalle = self.pedidos.crear_detalle_desde_catalogo(
                nombre_ramillete=configuracion["nombre"],
                cantidad_ramilletes=cantidad,
                flores_personalizadas=flores_personalizadas,
                notas=notas_detalle,
            )
            detalles.append(detalle)

            if not self._leer_confirmacion("Desea agregar otro ramillete al pedido? (s/n): "):
                break
        return detalles

    def _capturar_personalizacion(self):
        flores_disponibles = {}
        for flor in self.inventario.listar_inventario():
            flores_disponibles.setdefault(flor.nombre, set()).add(flor.color)

        nombres = sorted(flores_disponibles)
        print("\nSeleccione tipos de flores:")
        for indice, nombre in enumerate(nombres, start=1):
            print(f"{indice}. {nombre}")

        # La personalizacion se recopila como una lista de flores y colores concretos.
        indices = self._leer_indices_multiples(
            "Ingrese numeros separados por coma: ",
            maximo=len(nombres),
        )
        seleccionadas = []
        for indice in indices:
            nombre_flor = nombres[indice - 1]
            colores = sorted(flores_disponibles[nombre_flor])
            print(f"\nColores disponibles para {nombre_flor}:")
            for posicion, color in enumerate(colores, start=1):
                print(f"{posicion}. {color}")
            seleccion_color = self._leer_entero(
                f"Seleccione color para {nombre_flor}: ",
                minimo=1,
                maximo=len(colores),
            )
            tallos = self._leer_entero(
                f"Cantidad de tallos por ramillete para {nombre_flor}: ",
                minimo=1,
            )
            seleccionadas.append(
                FlorPersonalizada(
                    nombre=nombre_flor,
                    color=colores[seleccion_color - 1],
                    cantidad_tallos_por_ramillete=tallos,
                )
            )
        return seleccionadas

    def _mostrar_resumen_preliminar(self, cliente, detalles, direccion, fecha_entrega, prioridad, notas) -> None:
        total = sum(detalle.total for detalle in detalles)
        print("\nResumen preliminar del pedido:")
        print(f"Cliente: {cliente.nombre}")
        print(f"Destino: {cliente.pais_destino}")
        print(f"Productos: {', '.join(detalle.descripcion_corta() for detalle in detalles)}")
        print(f"Flores: {' | '.join(self._resumen_flores_detalle(detalle) for detalle in detalles)}")
        print(f"Direccion: {direccion}")
        print(f"Fecha de entrega: {formatear_fecha(fecha_entrega)}")
        print(f"Prioridad: {'URGENTE' if prioridad == 1 else 'REGULAR'}")
        print(f"Notas: {notas or 'Sin notas'}")
        print(f"Total estimado: {formatear_moneda(total)}")

    def _mostrar_detalle_pedido(self, pedido) -> None:
        print(f"\nID asignado: {pedido.identificador}")
        print(f"Cliente: {pedido.cliente.nombre}")
        print(f"Correo: {pedido.cliente.correo}")
        print(f"Telefono: {pedido.cliente.telefono}")
        print(f"Destino: {pedido.destino}")
        print(f"Direccion: {pedido.direccion_envio}")
        print(f"Productos: {pedido.resumen_productos()}")
        print(f"Flores: {pedido.resumen_flores()}")
        print(f"Fecha de entrega: {formatear_fecha(pedido.fecha_entrega_deseada)}")
        print(f"Estado: {pedido.estado_legible}")
        print(f"Prioridad: {pedido.prioridad_legible}")
        print(f"Notas: {pedido.notas or 'Sin notas'}")
        if pedido.numero_seguimiento:
            print(f"Seguimiento: {pedido.numero_seguimiento}")
        if pedido.transportista:
            print(f"Transportista: {pedido.transportista}")
        if pedido.fecha_estimada_entrega:
            print(f"Entrega estimada: {formatear_fecha(pedido.fecha_estimada_entrega)}")
        print(f"Total: {formatear_moneda(pedido.total)}")

    def _resumen_flores_detalle(self, detalle) -> str:
        return f"{detalle.nombre_ramillete}: " + ", ".join(
            f"{flor.nombre} ({flor.color})" for flor in detalle.obtener_flores_aplicadas()
        )

    def _leer_texto(self, mensaje: str, obligatorio: bool = True) -> str:
        while True:
            valor = input(mensaje).strip()
            if valor or not obligatorio:
                return valor
            print("Error: Debe ingresar un valor.")

    def _leer_entero(
        self,
        mensaje: str,
        minimo: int | None = None,
        maximo: int | None = None,
        permitir_negativos: bool = False,
    ) -> int:
        while True:
            valor = input(mensaje).strip()
            try:
                numero = int(valor)
            except ValueError:
                print("Error: Debe ingresar un numero entero valido.")
                continue
            if not permitir_negativos and numero < 0:
                print("Error: El valor no puede ser negativo.")
                continue
            if minimo is not None and numero < minimo:
                print(f"Error: El valor minimo permitido es {minimo}.")
                continue
            if maximo is not None and numero > maximo:
                print(f"Error: El valor maximo permitido es {maximo}.")
                continue
            return numero

    def _leer_fecha(self, mensaje: str):
        while True:
            texto = input(mensaje).strip()
            try:
                return datetime.strptime(texto, "%d/%m/%Y").date()
            except ValueError:
                print("Error: La fecha debe tener el formato DD/MM/AAAA.")

    def _leer_confirmacion(self, mensaje: str) -> bool:
        while True:
            respuesta = input(mensaje).strip().lower()
            if respuesta in {"s", "si"}:
                return True
            if respuesta in {"n", "no"}:
                return False
            print("Error: Responda con 's' o 'n'.")

    def _leer_opcion(self, mensaje: str, opciones_validas: set[str]) -> str:
        while True:
            opcion = input(mensaje).strip()
            if opcion in opciones_validas:
                return opcion
            print("Error: Seleccione una opcion valida.")

    def _leer_indices_multiples(self, mensaje: str, maximo: int) -> list[int]:
        while True:
            texto = input(mensaje).strip()
            try:
                indices = [int(valor.strip()) for valor in texto.split(",") if valor.strip()]
            except ValueError:
                print("Error: Debe ingresar numeros separados por comas.")
                continue
            if not indices:
                print("Error: Debe seleccionar al menos una flor para continuar con el pedido.")
                continue
            if any(indice < 1 or indice > maximo for indice in indices):
                print("Error: Uno o mas indices estan fuera del rango permitido.")
                continue
            return list(dict.fromkeys(indices))

    @staticmethod
    def _pausar() -> None:
        input("\nPresione Enter para continuar...")
