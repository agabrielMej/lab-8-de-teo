# Laboratorio 8 de Teoría de la Computación

Implementación en Python de las partes programables 1b, 2b y 3b. El programa mide el tiempo de ejecución con `perf_counter`, registra el profiling con `cProfile` y genera una tabla CSV y una gráfica PNG por problema.

## Archivos del proyecto

| Archivo o carpeta | Contenido |
| --- | --- |
| `main.py` | Los tres programas, medición, profiling y generación de resultados. |
| `requirements.txt` | Dependencia necesaria para crear las gráficas. |
| `respuestas_manuales/` | Destino del PDF con los ejercicios resueltos a mano. |
| `resultados/` | Se crea al ejecutar el programa. |

## Requisitos

- Python 3.10 o superior.
- Matplotlib 3.10.8, instalado con el comando indicado abajo.

No es necesario instalar `cProfile`, `csv`, `multiprocessing` ni `pstats`: forman parte de Python. Tampoco se requiere Graphviz.

## Instalación

Descomprime el ZIP y abre una terminal dentro de la carpeta `Laboratorio_8_TC`, donde se encuentran `main.py` y `requirements.txt`.

```bash
python -m pip install -r requirements.txt
```

Si Windows reconoce `py` en lugar de `python`, sustituye `python` por `py` en los comandos. En Linux o WSL puedes usar `python3`.

## Prueba de funcionamiento

```bash
python main.py --rapido --salida resultados_prueba
```

Ejecuta los tres problemas con `n = 1, 10, 100, 1000`. Sirve para comprobar la instalación y mostrar el programa; no sustituye las mediciones de los siete tamaños solicitados en el laboratorio.

## Ejecución de todos los casos

```bash
python main.py
```

Se ejecutan los problemas 1, 2 y 3 para `n = 1, 10, 100, 1000, 10000, 100000, 1000000`, sin límite de tiempo y en orden.

Los tamaños grandes de los problemas 1 y 3 son costosos. Para `n = 1000000`, el problema 1 ejecuta `counter += 1` exactamente 5,000,010,000,000 veces y el problema 3 realiza 83,333,250,000 llamadas a `print`. No se reemplazan los ciclos por fórmulas para medirlos. Por ello, la ejecución completa puede tardar mucho más que una demostración en video.

## Ejecución con un límite opcional

```bash
python main.py --limite 10 --salida resultados_limitados
```

Intenta cada uno de los siete tamaños de los tres problemas. Si un caso no termina dentro del límite, se detiene ese proceso y se continúa con el siguiente caso. El límite abarca la ejecución y la escritura de su perfil después del aviso de inicio; el tiempo de la tabla mide únicamente la llamada al algoritmo con el profiler activo.

El estado será `Límite de tiempo alcanzado` y el tiempo quedará vacío. No se inventan ni se extrapolan tiempos, y no se dibuja un punto para esa ejecución. Un caso limitado no equivale a una medición completa requerida por el enunciado.

## Ejecutar un problema o tamaños específicos

Solo el problema 2 con los siete tamaños:

```bash
python main.py --problemas 2 --salida resultados_problema_2
```

Problemas 1 y 3 con tamaños específicos:

```bash
python main.py --problemas 1 3 --n 1 10 100 1000 --salida resultados_parciales
```

Consultar todas las opciones:

```bash
python main.py --help
```

Las tablas y gráficas se actualizan después de cada caso. `Ctrl+C` durante una medición detiene el trabajo y conserva los resultados ya guardados, con el caso actual marcado como interrumpido. Una nueva ejecución en la misma carpeta reemplaza las tablas de los problemas seleccionados; utiliza `--salida` para conservar ejecuciones anteriores.

## Archivos generados

Por cada problema ejecutado se generan:

- `problema_1.csv`, `problema_2.csv` o `problema_3.csv`: tamaño de entrada, tiempo en segundos y estado. Se pueden abrir con Excel o un editor de texto.
- `problema_1.png`, `problema_2.png` o `problema_3.png`: gráfica de tamaño de entrada contra tiempo. Los ejes usan escala logarítmica cuando hay tiempos disponibles.
- `perfiles/problema_P_n_N.prof`: datos de `cProfile` para cada caso completado.
- `perfiles/problema_P_n_N.txt`: reporte legible del mismo perfil, ordenado por tiempo acumulado.
- `ejecucion.json`: parámetros de la ejecución, fecha UTC y versiones del entorno.

## Condiciones de medición

La división entera de C se conserva mediante `//`. En el problema 2 se conserva el `break`, y en el problema 3 se conserva el incremento de cuatro en cuatro.

Las llamadas a `print("Sequence")` se ejecutan realmente, pero su salida se redirige al dispositivo nulo del sistema. Así se evita llenar la terminal y crear archivos de texto enormes. Estos tiempos corresponden a esa condición de salida y no al renderizado de millones de líneas en una terminal.

Se realiza una medición por caso, con `cProfile` activo. El tiempo incluye el costo del profiler durante el algoritmo y excluye el arranque del proceso, la generación de gráficas y la escritura de los reportes. Las mediciones pequeñas pueden fluctuar; los tiempos dependen del equipo y de su carga.

## Respuestas escritas

Coloca tu PDF con los problemas 1a, 2a, 3a, 4 y 5 dentro de `respuestas_manuales/`. Las respuestas escritas del estudiante no están incluidas en este paquete de código.

## Video

Pendiente: agregar aquí el enlace real al video de YouTube configurado como no listado, con duración máxima de 10 minutos, mostrando la ejecución de los programas.

## Entrega

Sube el proyecto a tu repositorio de GitHub, junto con los resultados que obtengas, el PDF de respuestas y este README actualizado con el enlace real del video. Revisa los estados de los CSV antes de presentar una tabla como completa.
