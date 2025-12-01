import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os

# Verificar importación de módulo compilado
try:
    from grafo_wrapper import PyGrafoDisperso
except ImportError as e:
    print("=" * 70)
    print("ERROR CRÍTICO: No se pudo importar grafo_wrapper")
    print("=" * 70)
    print("\nAsegúrate de compilar el módulo primero:")
    print("  python setup.py build_ext --inplace")
    print("\nDetalles del error:", str(e))
    print("=" * 70)
    sys.exit(1)

# Importaciones opcionales con manejo de errores
try:
    import networkx as nx
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    VISUALIZACION_DISPONIBLE = True
except ImportError as e:
    print("ADVERTENCIA: NetworkX o Matplotlib no disponible")
    print("Instala con: pip install networkx matplotlib")
    print("La visualización estará deshabilitada")
    VISUALIZACION_DISPONIBLE = False

import time


class NeuroNetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroNet - Análisis de Redes Masivas")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")

        self.grafo = None
        self.archivo_cargado = None
        self.ultimo_bfs_resultado = None

        self.crear_interfaz()

    def crear_interfaz(self):
        # Frame superior - Controles
        frame_controles = tk.Frame(self.root, bg="#2d2d2d", pady=10)
        frame_controles.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Botón cargar archivo
        btn_cargar = tk.Button(
            frame_controles,
            text="📂 Cargar Dataset",
            command=self.cargar_archivo,
            bg="#0d7377",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_cargar.pack(side=tk.LEFT, padx=5)

        # Label archivo cargado
        self.lbl_archivo = tk.Label(
            frame_controles,
            text="Sin archivo cargado",
            bg="#2d2d2d",
            fg="#aaaaaa",
            font=("Arial", 10)
        )
        self.lbl_archivo.pack(side=tk.LEFT, padx=10)

        # Frame métricas
        frame_metricas = tk.Frame(self.root, bg="#2d2d2d")
        frame_metricas.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.lbl_metricas = tk.Label(
            frame_metricas,
            text="Métricas: -",
            bg="#2d2d2d",
            fg="#00d9ff",
            font=("Arial", 11),
            anchor="w"
        )
        self.lbl_metricas.pack(fill=tk.X, padx=10)

        # Frame análisis
        frame_analisis = tk.LabelFrame(
            self.root,
            text="Análisis Topológico",
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10
        )
        frame_analisis.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Botón nodo crítico
        btn_critico = tk.Button(
            frame_analisis,
            text="🎯 Identificar Nodo Crítico (Mayor Grado)",
            command=self.identificar_nodo_critico,
            bg="#323edd",
            fg="white",
            font=("Arial", 11),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_critico.pack(side=tk.LEFT, padx=10)

        self.lbl_critico = tk.Label(
            frame_analisis,
            text="",
            bg="#2d2d2d",
            fg="#ffcc00",
            font=("Arial", 10, "bold")
        )
        self.lbl_critico.pack(side=tk.LEFT, padx=10)

        # Frame simulación BFS
        frame_bfs = tk.LabelFrame(
            self.root,
            text="Simulación de Recorrido (BFS)",
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10
        )
        frame_bfs.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(
            frame_bfs,
            text="Nodo Inicio:",
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.entry_nodo = tk.Entry(frame_bfs, width=10, font=("Arial", 10))
        self.entry_nodo.insert(0, "0")
        self.entry_nodo.pack(side=tk.LEFT, padx=5)

        tk.Label(
            frame_bfs,
            text="Profundidad Máxima:",
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.entry_profundidad = tk.Entry(frame_bfs, width=10, font=("Arial", 10))
        self.entry_profundidad.insert(0, "2")
        self.entry_profundidad.pack(side=tk.LEFT, padx=5)

        btn_bfs = tk.Button(
            frame_bfs,
            text="▶️ Ejecutar BFS",
            command=self.ejecutar_bfs,
            bg="#14a085",
            fg="white",
            font=("Arial", 11),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        btn_bfs.pack(side=tk.LEFT, padx=10)

        # Frame visualización (solo si está disponible)
        if VISUALIZACION_DISPONIBLE:
            frame_viz = tk.Frame(self.root, bg="#1e1e1e")
            frame_viz.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

            self.figura = plt.Figure(figsize=(10, 6), facecolor="#1e1e1e")
            self.ax = self.figura.add_subplot(111)
            self.ax.set_facecolor("#2d2d2d")

            self.canvas = FigureCanvasTkAgg(self.figura, frame_viz)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Mensaje inicial
            self.ax.text(
                0.5, 0.5,
                "Carga un dataset para comenzar",
                ha='center',
                va='center',
                color='white',
                fontsize=16,
                transform=self.ax.transAxes
            )
            self.canvas.draw()
        else:
            # Frame alternativo si no hay visualización
            frame_info = tk.Frame(self.root, bg="#2d2d2d")
            frame_info.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

            tk.Label(
                frame_info,
                text="Visualización no disponible\n\nInstala: pip install networkx matplotlib",
                bg="#2d2d2d",
                fg="#888888",
                font=("Arial", 14),
                justify=tk.CENTER
            ).pack(expand=True)

    def cargar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de dataset",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=os.path.join(os.getcwd(), "datasets") if os.path.exists("datasets") else os.getcwd()
        )

        if not archivo:
            return

        try:
            # Verificar que el archivo existe
            if not os.path.exists(archivo):
                raise FileNotFoundError(f"El archivo no existe: {archivo}")

            # Verificar que el archivo no está vacío
            if os.path.getsize(archivo) == 0:
                raise ValueError("El archivo está vacío")

            self.grafo = PyGrafoDisperso()
            tiempo_inicio = time.time()

            # Cargar con manejo de errores
            try:
                self.grafo.cargar_datos(archivo)
            except Exception as e:
                raise RuntimeError(f"Error al cargar datos: {str(e)}")

            tiempo_carga = time.time() - tiempo_inicio

            # Obtener métricas con validación
            try:
                num_nodos = self.grafo.get_num_nodos()
                num_aristas = self.grafo.get_num_aristas()
                memoria = self.grafo.get_memoria_usada()
            except Exception as e:
                raise RuntimeError(f"Error al obtener métricas: {str(e)}")

            # Validar que se cargó algo
            if num_nodos == 0:
                raise ValueError("El dataset no contiene nodos válidos")

            self.archivo_cargado = os.path.basename(archivo)
            self.lbl_archivo.config(text=f"✅ {self.archivo_cargado}")

            self.lbl_metricas.config(
                text=f"Nodos: {num_nodos:,} | Aristas: {num_aristas:,} | "
                     f"Memoria: {memoria:.2f} MB | Tiempo carga: {tiempo_carga:.2f}s"
            )

            messagebox.showinfo(
                "Éxito",
                f"Dataset cargado correctamente\n\n"
                f"Archivo: {self.archivo_cargado}\n"
                f"Nodos: {num_nodos:,}\n"
                f"Aristas: {num_aristas:,}\n"
                f"Memoria: {memoria:.2f} MB\n"
                f"Tiempo: {tiempo_carga:.2f}s"
            )

        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Archivo no encontrado:\n{str(e)}")
            self.grafo = None
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos:\n{str(e)}")
            self.grafo = None
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
            self.grafo = None
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}\n\nTipo: {type(e).__name__}")
            self.grafo = None

    def identificar_nodo_critico(self):
        if not self.grafo:
            messagebox.showwarning("Advertencia", "Primero debes cargar un dataset")
            return

        try:
            nodo_max = self.grafo.get_nodo_max_grado()

            if nodo_max < 0:
                messagebox.showerror("Error", "No se pudo identificar el nodo crítico")
                return

            grado_max = self.grafo.obtener_grado(nodo_max)

            self.lbl_critico.config(
                text=f"Nodo más crítico: {nodo_max} (Grado: {grado_max})"
            )

            messagebox.showinfo(
                "Nodo Crítico Identificado",
                f"El nodo con mayor grado es:\n\n"
                f"ID: {nodo_max}\n"
                f"Conexiones: {grado_max}\n\n"
                f"Este nodo es el más influyente de la red."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al identificar nodo crítico:\n{str(e)}")

    def ejecutar_bfs(self):
        if not self.grafo:
            messagebox.showwarning("Advertencia", "Primero debes cargar un dataset")
            return

        try:
            # Validar entrada de nodo
            try:
                nodo_inicio = int(self.entry_nodo.get())
            except ValueError:
                messagebox.showerror("Error", "El nodo inicio debe ser un número entero")
                return

            # Validar entrada de profundidad
            try:
                profundidad = int(self.entry_profundidad.get())
            except ValueError:
                messagebox.showerror("Error", "La profundidad debe ser un número entero")
                return

            # Validar rangos
            num_nodos = self.grafo.get_num_nodos()

            if nodo_inicio < 0 or nodo_inicio >= num_nodos:
                messagebox.showerror(
                    "Error",
                    f"Nodo fuera de rango.\n\n"
                    f"Debe estar entre 0 y {num_nodos-1}\n"
                    f"Ingresaste: {nodo_inicio}"
                )
                return

            if profundidad < 0:
                messagebox.showerror("Error", "La profundidad no puede ser negativa")
                return

            if profundidad > 10:
                respuesta = messagebox.askyesno(
                    "Advertencia",
                    f"Profundidad {profundidad} puede ser muy grande.\n\n"
                    f"¿Deseas continuar?"
                )
                if not respuesta:
                    return

            # Ejecutar BFS
            tiempo_inicio = time.time()
            nodos_visitados = self.grafo.bfs(nodo_inicio, profundidad)
            tiempo_ejecucion = time.time() - tiempo_inicio

            # Validar resultado
            if not nodos_visitados:
                messagebox.showwarning(
                    "Advertencia",
                    f"No se encontraron nodos accesibles desde el nodo {nodo_inicio}"
                )
                return

            self.ultimo_bfs_resultado = {
                'nodo_inicio': nodo_inicio,
                'profundidad': profundidad,
                'nodos': nodos_visitados,
                'tiempo': tiempo_ejecucion
            }

            # Visualizar si está disponible
            if VISUALIZACION_DISPONIBLE:
                self.visualizar_subgrafo(nodo_inicio, nodos_visitados, profundidad)

            messagebox.showinfo(
                "BFS Completado",
                f"Recorrido finalizado exitosamente\n\n"
                f"Nodo inicial: {nodo_inicio}\n"
                f"Profundidad: {profundidad}\n"
                f"Nodos visitados: {len(nodos_visitados):,}\n"
                f"Tiempo: {tiempo_ejecucion*1000:.2f}ms"
            )

        except ValueError as e:
            messagebox.showerror("Error", f"Valor inválido:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar BFS:\n{str(e)}\n\nTipo: {type(e).__name__}")

    def visualizar_subgrafo(self, nodo_inicio, nodos_visitados, profundidad):
        if not VISUALIZACION_DISPONIBLE:
            return

        try:
            # Limpiar figura
            self.ax.clear()
            self.ax.set_facecolor("#2d2d2d")

            # Limitar visualización para grafos grandes
            max_nodos_viz = 100
            if len(nodos_visitados) > max_nodos_viz:
                nodos_mostrar = nodos_visitados[:max_nodos_viz]
                titulo = f"BFS desde Nodo {nodo_inicio} (Mostrando {max_nodos_viz}/{len(nodos_visitados)} nodos)"
            else:
                nodos_mostrar = nodos_visitados
                titulo = f"BFS desde Nodo {nodo_inicio} - Profundidad {profundidad}"

            self.ax.set_title(titulo, color='white', fontsize=14, pad=20)

            # Crear subgrafo con NetworkX
            G = nx.DiGraph()

            # Construir aristas del subgrafo con validación
            aristas_agregadas = 0
            for nodo in nodos_mostrar:
                try:
                    vecinos = self.grafo.get_vecinos(nodo)
                    for vecino in vecinos:
                        if vecino in nodos_mostrar:
                            G.add_edge(nodo, vecino)
                            aristas_agregadas += 1
                            if aristas_agregadas > 1000:  # Limitar aristas
                                break
                except:
                    continue

                if aristas_agregadas > 1000:
                    break

            # Si no hay nodos, mostrar mensaje
            if len(G.nodes()) == 0:
                self.ax.text(
                    0.5, 0.5,
                    "No se pudieron visualizar conexiones",
                    ha='center',
                    va='center',
                    color='white',
                    fontsize=14,
                    transform=self.ax.transAxes
                )
                self.canvas.draw()
                return

            # Layout con manejo de errores
            try:
                pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
            except:
                pos = nx.circular_layout(G)

            # Colores
            node_colors = []
            for nodo in G.nodes():
                if nodo == nodo_inicio:
                    node_colors.append('#ff4444')
                else:
                    node_colors.append('#00d9ff')

            # Dibujar nodos
            nx.draw_networkx_nodes(
                G, pos, ax=self.ax,
                node_color=node_colors,
                node_size=300,
                alpha=0.9
            )

            # Dibujar aristas
            nx.draw_networkx_edges(
                G, pos, ax=self.ax,
                edge_color='#666666',
                alpha=0.5,
                arrows=True,
                arrowsize=10,
                width=0.5
            )

            # Etiquetas solo para grafos pequeños
            if len(G.nodes()) < 30:
                nx.draw_networkx_labels(
                    G, pos, ax=self.ax,
                    font_size=8,
                    font_color='white'
                )

            self.ax.axis('off')
            self.figura.tight_layout()
            self.canvas.draw()

        except Exception as e:
            print(f"Error en visualización: {e}")
            self.ax.clear()
            self.ax.set_facecolor("#2d2d2d")
            self.ax.text(
                0.5, 0.5,
                f"Error al visualizar:\n{str(e)}",
                ha='center',
                va='center',
                color='red',
                fontsize=12,
                transform=self.ax.transAxes
            )
            self.canvas.draw()


def main():
    try:
        root = tk.Tk()
        app = NeuroNetGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error fatal: {e}")
        messagebox.showerror("Error Fatal", f"La aplicación no puede iniciar:\n\n{str(e)}")


if __name__ == "__main__":
    main()