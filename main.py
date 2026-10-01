import argparse
import cProfile
import csv
import json
import math
import multiprocessing as mp
import os
import platform
import pstats
import signal
import sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


VALORES_N = [1, 10, 100, 1000, 10000, 100000, 1000000]


def problema_1(n):
    counter = 0
    for i in range(n // 2, n + 1):
        for j in range(1, n - n // 2 + 1):
            k = 1
            while k <= n:
                counter += 1
                k *= 2
    return counter


def problema_2(n):
    if n <= 1:
        return
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            print("Sequence")
            break


def problema_3(n):
    for i in range(1, n // 3 + 1):
        for j in range(1, n + 1, 4):
            print("Sequence")


PROGRAMAS = {1: problema_1, 2: problema_2, 3: problema_3}


def ejecutar_profiling(problema, n, carpeta, conexion):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    perfil = cProfile.Profile()
    try:
        with open(os.devnull, "w", encoding="utf-8") as salida:
            with redirect_stdout(salida):
                conexion.send(("preparado", None))
                conexion.recv()
                perfil.enable()
                inicio = perf_counter()
                PROGRAMAS[problema](n)
                tiempo = perf_counter() - inicio
                perfil.disable()
                salida.flush()

        base = Path(carpeta) / f"problema_{problema}_n_{n}"
        perfil.dump_stats(str(base.with_suffix(".prof")))
        with base.with_suffix(".txt").open("w", encoding="utf-8") as archivo:
            pstats.Stats(perfil, stream=archivo).strip_dirs().sort_stats(
                "cumulative"
            ).print_stats()
        conexion.send(("completado", tiempo))
    except Exception as error:
        perfil.disable()
        conexion.send(("error", f"{type(error).__name__}: {error}"))
    finally:
        conexion.close()


def medir_tiempo(problema, n, limite, carpeta):
    contexto = mp.get_context("spawn")
    principal, secundaria = contexto.Pipe()
    proceso = contexto.Process(
        target=ejecutar_profiling,
        args=(problema, n, str(carpeta), secundaria),
    )
    proceso.start()
    secundaria.close()
    try:
        if not principal.poll(60):
            return None, "Error al iniciar el proceso"
        estado, dato = principal.recv()
        if estado != "preparado":
            return None, f"Error: {dato}"

        principal.send("iniciar")
        if not principal.poll(limite if limite > 0 else None):
            return None, "Límite de tiempo alcanzado"

        estado, dato = principal.recv()
        if estado == "completado":
            proceso.join(1)
            return dato, "Completado"
        return None, f"Error: {dato}"
    except EOFError:
        return None, "El proceso terminó sin resultado"
    finally:
        if proceso.is_alive():
            proceso.terminate()
        proceso.join()
        principal.close()


def guardar_resultados(plt, problema, filas, carpeta):
    ruta = carpeta / f"problema_{problema}.csv"
    with ruta.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["n", "tiempo_segundos", "estado"])
        for fila in filas:
            escritor.writerow([
                fila["n"],
                "" if fila["tiempo"] is None else f'{fila["tiempo"]:.12f}',
                fila["estado"],
            ])

    completos = [fila for fila in filas if fila["tiempo"] is not None]
    sin_medicion = [str(fila["n"]) for fila in filas if fila["tiempo"] is None]
    figura, eje = plt.subplots(figsize=(10, 6))

    if completos:
        eje.plot(
            [fila["n"] for fila in completos],
            [fila["tiempo"] for fila in completos],
            marker="o", color="royalblue", linewidth=2,
        )
        eje.set_yscale("log")
    else:
        eje.text(
            0.5, 0.5, "No hay mediciones completas",
            transform=eje.transAxes, ha="center", va="center",
        )

    eje.set_xscale("log")
    eje.set_xticks([fila["n"] for fila in filas])
    eje.set_xticklabels([str(fila["n"]) for fila in filas], rotation=30)
    eje.set_xlabel("Tamaño de entrada (n), escala logarítmica")
    eje.set_ylabel("Tiempo con cProfile (segundos)")
    eje.set_title(f"Problema {problema}: tamaño de entrada vs. tiempo")
    eje.grid(True, which="both", alpha=0.3)

    nota = "Los puntos representan únicamente ejecuciones completas."
    if problema in (2, 3):
        nota += "\nLas llamadas a print se ejecutan hacia el dispositivo nulo."
    if sin_medicion:
        nota += "\nSin medición completa: n = " + ", ".join(sin_medicion)
    figura.text(0.5, 0.02, nota, ha="center", fontsize=9)
    figura.tight_layout(rect=(0, 0.13, 1, 1))
    figura.savefig(carpeta / f"problema_{problema}.png", dpi=180)
    plt.close(figura)


def procesar_problema(plt, problema, valores, limite, carpeta):
    perfiles = carpeta / "perfiles"
    perfiles.mkdir(parents=True, exist_ok=True)
    filas = [
        {"n": n, "tiempo": None, "estado": "Pendiente"}
        for n in valores
    ]
    guardar_resultados(plt, problema, filas, carpeta)
    print(f"\nProblema {problema}")
    print(f"{'n':>12} | {'Tiempo (s)':>18} | Estado")
    print("-" * 75)

    for fila in filas:
        n = fila["n"]
        interrumpido = False
        for extension in (".prof", ".txt"):
            (perfiles / f"problema_{problema}_n_{n}{extension}").unlink(
                missing_ok=True
            )
        print(f"{n:>12} | ", end="", flush=True)
        try:
            tiempo, estado = medir_tiempo(problema, n, limite, perfiles)
        except KeyboardInterrupt:
            tiempo, estado = None, "Interrumpido por el usuario"
            interrumpido = True
        fila.update(tiempo=tiempo, estado=estado)
        mostrado = "-" if tiempo is None else f"{tiempo:.9f}"
        print(f"{mostrado:>18} | {estado}", flush=True)
        guardar_resultados(plt, problema, filas, carpeta)
        if interrumpido:
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Laboratorio 8: profiling de los problemas 1b, 2b y 3b."
    )
    parser.add_argument(
        "--problemas", nargs="+", type=int, choices=[1, 2, 3],
        default=[1, 2, 3], help="Problemas que se ejecutarán.",
    )
    seleccion = parser.add_mutually_exclusive_group()
    seleccion.add_argument("--n", nargs="+", type=int, help="Tamaños de entrada.")
    seleccion.add_argument(
        "--rapido", action="store_true",
        help="Verifica los tres programas con n = 1, 10, 100 y 1000.",
    )
    parser.add_argument(
        "--limite", type=float, default=0,
        help="Segundos máximos por caso; 0 significa sin límite.",
    )
    parser.add_argument(
        "--salida", type=Path, default=Path("resultados"),
        help="Carpeta para guardar tablas, gráficas y perfiles.",
    )
    args = parser.parse_args()
    valores = [1, 10, 100, 1000] if args.rapido else (args.n or VALORES_N)
    valores = sorted(set(valores))
    if any(n < 1 for n in valores):
        parser.error("Los tamaños de entrada deben ser enteros positivos.")
    if not math.isfinite(args.limite) or args.limite < 0:
        parser.error("El límite debe ser finito y mayor o igual a 0.")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        parser.exit(1, "Instala las dependencias: python -m pip install -r requirements.txt\n")

    args.salida.mkdir(parents=True, exist_ok=True)
    metadata = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "sistema": platform.platform(),
        "matplotlib": matplotlib.__version__,
        "problemas": sorted(set(args.problemas)),
        "valores_n": valores,
        "limite_segundos": args.limite,
        "profiling": "cProfile",
        "reloj": "time.perf_counter",
        "salida_programas": "dispositivo nulo",
    }
    (args.salida / "ejecucion.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("Laboratorio 8 | Problemas 1b, 2b y 3b")
    print("Profiling: cProfile. Reloj: perf_counter.")
    print("Las llamadas a print se ejecutan hacia el dispositivo nulo.")
    if args.limite == 0:
        print("Sin límite de tiempo. Los casos grandes de 1 y 3 pueden tardar mucho.")
        print("Usa --rapido para una prueba o --limite SEGUNDOS para limitar cada caso.")
    else:
        print(f"Límite por caso: {args.limite:g} segundos.")
        print("Un caso que exceda el límite se registra sin tiempo medido.")

    for problema in sorted(set(args.problemas)):
        if procesar_problema(plt, problema, valores, args.limite, args.salida):
            break
    print(f"\nResultados guardados en: {args.salida.resolve()}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
