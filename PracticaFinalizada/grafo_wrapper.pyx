# distutils: language = c++
# cython: language_level=3

from libcpp.vector cimport vector
from libcpp.string cimport string
from grafo_wrapper cimport GrafoDisperso as CGrafoDisperso

cdef class PyGrafoDisperso:
    cdef CGrafoDisperso* c_grafo

    def __cinit__(self):
        self.c_grafo = new CGrafoDisperso()

    def __dealloc__(self):
        if self.c_grafo != NULL:
            del self.c_grafo

    def cargar_datos(self, str archivo):
        """Carga un archivo de dataset en formato edge list"""
        cdef string c_archivo = archivo.encode('utf-8')
        self.c_grafo.cargarDatos(c_archivo)

    def bfs(self, int nodo_inicio, int profundidad_max):
        """Ejecuta BFS desde un nodo con profundidad máxima"""
        print(f"[Cython] Solicitud recibida: BFS desde Nodo {nodo_inicio}, Profundidad {profundidad_max}.")
        cdef vector[int] resultado = self.c_grafo.BFS(nodo_inicio, profundidad_max)
        print(f"[Cython] Retornando lista de adyacencia local a Python.")
        return list(resultado)

    def obtener_grado(self, int nodo):
        """Obtiene el grado (número de conexiones) de un nodo"""
        return self.c_grafo.obtenerGrado(nodo)

    def get_vecinos(self, int nodo):
        """Obtiene la lista de vecinos de un nodo"""
        cdef vector[int] vecinos = self.c_grafo.getVecinos(nodo)
        return list(vecinos)

    def get_num_nodos(self):
        """Retorna el número total de nodos"""
        return self.c_grafo.getNumNodos()

    def get_num_aristas(self):
        """Retorna el número total de aristas"""
        return self.c_grafo.getNumAristas()

    def get_memoria_usada(self):
        """Retorna la memoria usada en MB"""
        return self.c_grafo.getMemoriaUsada()

    def get_nodo_max_grado(self):
        """Encuentra el nodo con mayor número de conexiones"""
        return self.c_grafo.getNodoMaxGrado()