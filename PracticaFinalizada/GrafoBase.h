#ifndef GRAFO_BASE_H
#define GRAFO_BASE_H

#include <vector>
#include <string>

class GrafoBase {
public:
    virtual ~GrafoBase() {}

    // Métodos virtuales puros que deben implementarse
    virtual void cargarDatos(const std::string& archivo) = 0;
    virtual std::vector<int> BFS(int nodo_inicio, int profundidad_max) = 0;
    virtual int obtenerGrado(int nodo) = 0;
    virtual std::vector<int> getVecinos(int nodo) = 0;
    virtual int getNumNodos() const = 0;
    virtual int getNumAristas() const = 0;
    virtual double getMemoriaUsada() const = 0;
};

#endif // GRAFO_BASE_H