from setuptools import setup, Extension
from Cython.Build import cythonize
import platform

# Configuración específica según el sistema operativo
extra_compile_args = []
extra_link_args = []

if platform.system() == "Windows":
    extra_compile_args = ["/std:c++17", "/O2"]
elif platform.system() in ["Linux", "Darwin"]:
    extra_compile_args = ["-std=c++17", "-O3", "-march=native"]
    extra_link_args = ["-std=c++17"]

extensions = [
    Extension(
        name="grafo_wrapper",
        sources=[
            "cython/grafo_wrapper.pyx",
            "cpp/GrafoDisperso.cpp"
        ],
        include_dirs=["cpp"],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    name="NeuroNet",
    version="1.0",
    description="Sistema híbrido C++/Python para análisis de redes masivas",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'embedsignature': True
        }
    ),
    zip_safe=False,
)