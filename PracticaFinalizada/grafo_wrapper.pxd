# distutils: language = c++

from libcpp.vector cimport vector
from libcpp.string cimport string

cdef extern from "cpp/GrafoDisperso.h":
    cdef cppclass GrafoDisperso:
        GrafoDisperso() except +
        void cargarDatos(const string& archivo)
        vector[int] BFS(int nodo_inicio, int profundidad_max)
        int obtenerGrado(int nodo)
        vector[int] getVecinos(int nodo)
        int getNumNodos()
        int getNumAristas()
        double getMemoriaUsada()
        int getNodoMaxGrado()