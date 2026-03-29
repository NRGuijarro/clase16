import unittest

from florexport.estructuras import ColaPrioridadDinamica, ListaEnlazada, Pila


class PruebasListaEnlazada(unittest.TestCase):
    def test_agregar_buscar_y_eliminar(self):
        lista = ListaEnlazada(["pedido-1", "pedido-2", "pedido-3"])

        encontrado = lista.buscar(lambda valor: valor == "pedido-2")
        eliminado = lista.eliminar_primero(lambda valor: valor == "pedido-2")

        self.assertEqual(encontrado, "pedido-2")
        self.assertEqual(eliminado, "pedido-2")
        self.assertEqual(list(lista), ["pedido-1", "pedido-3"])


class PruebasPila(unittest.TestCase):
    def test_apilar_y_desapilar_respeta_lifo(self):
        pila = Pila()
        pila.apilar("creacion")
        pila.apilar("modificacion")
        pila.apilar("eliminacion")

        self.assertEqual(pila.ver_tope(), "eliminacion")
        self.assertEqual(pila.desapilar(), "eliminacion")
        self.assertEqual(pila.desapilar(), "modificacion")
        self.assertEqual(pila.desapilar(), "creacion")
        self.assertTrue(pila.esta_vacia())


class PruebasColaPrioridad(unittest.TestCase):
    def test_encolar_respeta_prioridad_y_fifo(self):
        cola = ColaPrioridadDinamica()
        cola.encolar("regular-1", prioridad=2)
        cola.encolar("urgente-1", prioridad=1)
        cola.encolar("urgente-2", prioridad=1)
        cola.encolar("regular-2", prioridad=2)

        self.assertEqual(cola.listar(), ["urgente-1", "urgente-2", "regular-1", "regular-2"])


if __name__ == "__main__":
    unittest.main()
