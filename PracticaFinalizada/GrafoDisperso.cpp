#include "GrafoDisperso.h"
#include <chrono>  // CRÍTICO: Faltaba esto
#include <algorithm>
#include <unordered_map>

void GrafoDisperso::cargarDatos(const std::string& archivo) {
    std::cout << "[C++ Core] Inicializando GrafoDisperso..." << std::endl;
    std::cout << "[C++ Core] Cargando dataset '" << archivo << "'..." << std::endl;
    
    std::ifstream file(archivo);
    if (!file.is_open()) {
        std::cerr << "Error: No se pudo abrir el archivo " << archivo << std::endl;
        throw std::runtime_error("No se pudo abrir el archivo");
    }
    
    // Usar map para evitar duplicados y manejar grafos no dirigidos
    std::unordered_map<int, std::unordered_set<int>> adj_map;
    std::string line;
    int max_nodo = -1;
    int count_aristas = 0;
    
    // Leer todas las aristas
    while (std::getline(file, line)) {
        // Ignorar líneas vacías y comentarios
        if (line.empty() || line[0] == '#') continue;
        
        std::istringstream iss(line);
        int origen, destino;
        if (iss >> origen >> destino) {
            // Verificar que los nodos sean válidos
            if (origen < 0 || destino < 0) continue;
            
            max_nodo = std::max(max_nodo, std::max(origen, destino));
            
            // Agregar arista (evitar duplicados con set)
            if (adj_map[origen].insert(destino).second) {
                count_aristas++;
            }
        }
    }
    file.close();
    
    // Verificar que se haya cargado algo
    if (max_nodo < 0) {
        throw std::runtime_error("El archivo no contiene datos válidos");
    }
    
    num_nodos = max_nodo + 1;
    num_aristas = count_aristas;
    
    // Construir estructura CSR
    row_ptr.clear();
    row_ptr.resize(num_nodos + 1, 0);
    valores.clear();
    column_indices.clear();
    
    // Calcular row_ptr
    for (int i = 0; i < num_nodos; i++) {
        row_ptr[i + 1] = row_ptr[i] + adj_map[i].size();
    }
    
    // Reservar espacio exacto
    valores.reserve(num_aristas);
    column_indices.reserve(num_aristas);
    
    // Llenar valores de forma ordenada
    for (int i = 0; i < num_nodos; i++) {
        std::vector<int> vecinos(adj_map[i].begin(), adj_map[i].end());
        std::sort(vecinos.begin(), vecinos.end());
        
        for (int vecino : vecinos) {
            valores.push_back(vecino);
            column_indices.push_back(vecino);
        }
    }
    
    // Liberar memoria del map temporal
    adj_map.clear();
    
    std::cout << "[C++ Core] Carga completa. Nodos: " << num_nodos 
              << " | Aristas: " << num_aristas << std::endl;
    std::cout << "[C++ Core] Estructura CSR construida. Memoria estimada: " 
              << getMemoriaUsada() << " MB." << std::endl;
}

std::vector<int> GrafoDisperso::BFS(int nodo_inicio, int profundidad_max) {
    std::cout << "[C++ Core] Ejecutando BFS nativo..." << std::endl;
    
    // Validaciones críticas
    if (num_nodos == 0) {
        std::cerr << "Error: Grafo no inicializado" << std::endl;
        return std::vector<int>();
    }
    
    if (nodo_inicio < 0 || nodo_inicio >= num_nodos) {
        std::cerr << "Error: Nodo inicio " << nodo_inicio << " fuera de rango [0, " 
                  << num_nodos - 1 << "]" << std::endl;
        return std::vector<int>();
    }
    
    if (profundidad_max < 0) {
        std::cerr << "Error: Profundidad no puede ser negativa" << std::endl;
        return std::vector<int>();
    }
    
    std::vector<int> resultado;
    std::vector<int> distancia(num_nodos, -1);
    std::queue<int> cola;
    
    cola.push(nodo_inicio);
    distancia[nodo_inicio] = 0;
    resultado.push_back(nodo_inicio);
    
    auto inicio = std::chrono::high_resolution_clock::now();
    
    while (!cola.empty()) {
        int actual = cola.front();
        cola.pop();
        
        if (distancia[actual] >= profundidad_max) continue;
        
        // Obtener vecinos con validación
        if (actual < 0 || actual >= num_nodos) continue;
        
        int inicio_vecinos = row_ptr[actual];
        int fin_vecinos = row_ptr[actual + 1];
        
        // Validar índices
        if (inicio_vecinos < 0 || fin_vecinos > static_cast<int>(valores.size())) {
            continue;
        }
        
        for (int i = inicio_vecinos; i < fin_vecinos; i++) {
            int vecino = valores[i];
            
            // Validar vecino
            if (vecino < 0 || vecino >= num_nodos) continue;
            
            if (distancia[vecino] == -1) {
                distancia[vecino] = distancia[actual] + 1;
                cola.push(vecino);
                resultado.push_back(vecino);
            }
        }
    }
    
    auto fin = std::chrono::high_resolution_clock::now();
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);
    
    std::cout << "[C++ Core] Nodos encontrados: " << resultado.size() 
              << ". Tiempo ejecución: " << duracion.count() / 1000.0 << "ms." << std::endl;
    
    return resultado;
}

int GrafoDisperso::obtenerGrado(int nodo) {
    if (nodo < 0 || nodo >= num_nodos) {
        return 0;
    }
    
    // Validar que row_ptr esté correctamente inicializado
    if (row_ptr.size() < static_cast<size_t>(nodo + 2)) {
        return 0;
    }
    
    return row_ptr[nodo + 1] - row_ptr[nodo];
}

std::vector<int> GrafoDisperso::getVecinos(int nodo) {
    if (nodo < 0 || nodo >= num_nodos) {
        return std::vector<int>();
    }
    
    if (row_ptr.size() < static_cast<size_t>(nodo + 2)) {
        return std::vector<int>();
    }
    
    int inicio = row_ptr[nodo];
    int fin = row_ptr[nodo + 1];
    
    // Validar índices
    if (inicio < 0 || fin > static_cast<int>(valores.size()) || inicio > fin) {
        return std::vector<int>();
    }
    
    return std::vector<int>(valores.begin() + inicio, valores.begin() + fin);
}

double GrafoDisperso::getMemoriaUsada() const {
    size_t bytes = 0;
    bytes += valores.capacity() * sizeof(int);
    bytes += column_indices.capacity() * sizeof(int);
    bytes += row_ptr.capacity() * sizeof(int);
    return bytes / (1024.0 * 1024.0);
}

int GrafoDisperso::getNodoMaxGrado() {
    if (num_nodos == 0) {
        std::cerr << "Error: Grafo vacío" << std::endl;
        return -1;
    }
    
    int max_grado = -1;
    int nodo_max = 0;
    
    for (int i = 0; i < num_nodos; i++) {
        int grado = obtenerGrado(i);
        if (grado > max_grado) {
            max_grado = grado;
            nodo_max = i;
        }
    }
    
    return nodo_max;
}