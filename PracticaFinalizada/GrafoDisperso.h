#ifndef GRAFO_DISPERSO_H
#define GRAFO_DISPERSO_H

#include "GrafoBase.h"
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <queue>
#include <unordered_set>
#include <algorithm>
#include <stdexcept>

class GrafoDisperso : public GrafoBase {
private:
    // Formato CSR (Compressed Sparse Row)
    std::vector<int> valores;          // Nodos destino
    std::vector<int> column_indices;   // Índices de columna
    std::vector<int> row_ptr;          // Punteros de inicio de fila

    int num_nodos;
    int num_aristas;

public:
    GrafoDisperso() : num_nodos(0), num_aristas(0) {}

    ~GrafoDisperso() {}

    void cargarDatos(const std::string& archivo) override;
    std::vector<int> BFS(int nodo_inicio, int profundidad_max) override;
    int obtenerGrado(int nodo) override;
    std::vector<int> getVecinos(int nodo) override;

    int getNumNodos() const override { return num_nodos; }
    int getNumAristas() const override { return num_aristas; }
    double getMemoriaUsada() const override;

    int getNodoMaxGrado();
};

#endif // GRAFO_DISPERSO_H