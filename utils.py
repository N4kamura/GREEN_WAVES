from copy import deepcopy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def apply_offset(program: list[list], offset: float) -> list[list]:
    cycle_time = sum([time_duration for _, time_duration in program])
    new_program = deepcopy(program)
    accum = offset % cycle_time
    for phase, duration in reversed(program):
        if accum >= duration:
            new_program[:0] = [[phase, duration]]
            new_program.pop()
            accum -= duration
            if accum == 0: break
        elif accum < duration: # accum < duration
            new_program[:0] = [[phase, accum]]
            new_program[-1][1] = duration - accum
            accum = 0
            break

    return new_program

def draw_light(ax, position, cycle, time_max, program, color_green="green", color_left="blue", color_amber="yellow", color_red="red"):
    colors = {
        "green": color_green,
        "left": color_left,
        "amber": color_amber,
        "red": color_red,
    }

    for t in np.arange(0, time_max, cycle):
        # Dibujar semáforo inbound
        _draw_segments(
            ax,
            [position, position + 10],
            t,
            program["inbound"],
            colors
        )
        # Dibujar semáforo outbound
        _draw_segments(
            ax,
            [position - 10, position],
            t,
            program["outbound"],
            colors
        )

def _draw_segments(ax, position_range, t_start, phases: list[list], colors) -> None:
    t = t_start
    for colour, duration in phases:
        ax.fill_betweenx(
            position_range,
            t,
            t + duration,
            color=colour,
            alpha=1,
        )
        t += duration

def draw_band(ax, intersection_positions, programs, velocity, time_max, light_cycles, direction="inbound", color="green"):
    """
    Dibuja las bandas de tiempo-espacio para un flujo específico (inbound u outbound).
    
    Args:
        ax: Ejes del gráfico.
        intersection_positions: Lista de posiciones de las intersecciones.
        programs: Diccionario de programas semafóricos.
        velocity: Velocidad en m/s.
        time_max: Duración máxima del gráfico (en segundos).
        direction: Dirección del flujo ('inbound' o 'outbound').
        color: Color de la banda.
    """
    if direction == "inbound":
        # Velocidad en m/s
        slope = -1 / velocity  # Pendiente inversa para el eje tiempo-espacio
        positions = intersection_positions[::-1]
        for i, (start_pos, end_pos) in enumerate(zip(positions[:-1], positions[1:])):
            cycle = light_cycles[i + 1]  # Ciclo total de la intersección
            green_duration = programs[i + 1][direction]["green"]  # Duración del verde
            start_time = 0  # Inicia en t=0

            while start_time < time_max:
                # Coordenadas del inicio y fin de la banda verde
                x1 = start_time
                y1 = start_pos
                x2 = x1 + slope * (end_pos - start_pos)  # Avance en el eje tiempo
                y2 = end_pos

                # Coordenadas del final de la banda verde
                x1_end = x1 + green_duration
                x2_end = x2 + green_duration

                # Dibujar la banda verde
                ax.fill(
                    [x1, x2, x2_end, x1_end],
                    [y1, y2, y2, y1],
                    color=color,
                    alpha=0.5
                )

                # Avanzar al siguiente ciclo
                start_time += cycle

    elif direction == "outbound":
        # Velocidad en m/s
        slope = 1 / velocity  # Pendiente inversa para el eje tiempo-espacio
        positions = intersection_positions
        for i, (start_pos, end_pos) in enumerate(zip(positions[:-1], positions[1:])):
            cycle = light_cycles[i + 1]  # Ciclo total de la intersección
            green_duration = programs[i + 1][direction]["green"]  # Duración del verde
            start_time = 0  # Inicia en t=0

            while start_time < time_max:
                # Coordenadas del inicio y fin de la banda verde
                x1 = start_time
                y1 = start_pos
                x2 = x1 + slope * (end_pos - start_pos)  # Avance en el eje tiempo
                y2 = end_pos

                # Coordenadas del final de la banda verde
                x1_end = x1 + green_duration
                x2_end = x2 + green_duration

                # Dibujar la banda verde
                ax.fill(
                    [x1, x2, x2_end, x1_end],
                    [y1, y2, y2, y1],
                    color=color,
                    alpha=0.5
                )

                # Avanzar al siguiente ciclo
                start_time += cycle

def read_gps_data(file_path: str, inbound: bool, upper_limit: float) -> pd.DataFrame:
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Lista para almacenar los datos procesados
    data = []

    # Identificar la sección de datos (evitar encabezados)
    start_parsing = False

    for line in lines:
        line = line.strip()  # Eliminar espacios en blanco y saltos de línea
        
        # Detectar el inicio de los datos cuando aparece "Trackpoint"
        if line.startswith("Header"):
            start_parsing = True
            continue  # Saltamos la línea de encabezado
        
        if start_parsing and line.startswith("Trackpoint"):
            # Separar por tabulaciones
            values = line.split("\t")
            
            # Manejo de datos vacíos (considerando que Temperature está vacío en algunos casos)
            while len(values) < 10:  # Ajustar longitud de lista si hay columnas vacías
                values.append("")

            # Extraer los valores con la estructura esperada
            # position = values[1]
            time = values[2]
            # altitude = values[3]
            # depth = float(values[4][:-2]) if values[4] else None
            # temperature = values[5] if values[5] else None
            leg_length = float(values[6][:-2]) if values[6] else 0.0
            # leg_time = values[7] if values[7] else None
            leg_speed = float(values[8][:-4]) if values[8] else 0.0
            # leg_course = values[9] if len(values) > 9 else None

            # Agregar a la lista de datos
            data.append([time, leg_length, leg_speed])

    # Crear el DataFrame
    columns = ["Time", "Leg Length", "Leg Speed"]
    df = pd.DataFrame(data, columns=columns)

    # Convertir valores numéricos
    df["Leg Length"] = pd.to_numeric(df["Leg Length"], errors="coerce")
    df["Leg Speed"] = pd.to_numeric(df["Leg Speed"], errors="coerce")

    # Agregar la columna de acumulado de 'Leg Length'
    df["Cumulative Length"] = df["Leg Length"].cumsum()

    # Convertir la columna 'Time' a datetime
    df["Time"] = df["Time"].str.strip()
    df["Time"] = pd.to_datetime(df["Time"], format="%d/%m/%Y %I:%M:%S %p")

    df["Time_Seconds"] = (df["Time"] - df["Time"].iloc[0]).dt.total_seconds()

    # Aplicando demora para afinar los inicios de los tiempos
    df["Time_Seconds"] += 26

    return df

def start_algorithm(df: pd.DataFrame) -> None:
    # Configuración de las intersecciones
    intersection_positions = [0, 134, 251+134, 530+251+134]  # Distancia en metros entre las intersecciones
    velocity = 20 # km/h
    programs = {
        4: {
            "inbound":  [["green", 77], ["blue", 0], ["yellow", 3], ["red", 70]],
            "outbound":  [["green", 77], ["blue", 0], ["yellow", 3], ["red", 70]]
        },
        3: {
            "inbound":  [["green", 42], ["blue", 0], ["yellow", 3], ["red", 45]],
            "outbound": [["green", 42], ["blue", 0], ["yellow", 3], ["red", 45]],
            },
        2: {
            "inbound":  [["green", 50], ["blue", 0], ["yellow", 3], ["red", 37]],
            "outbound": [["green", 50], ["blue", 0], ["yellow", 3], ["red", 37]],
            },
        1: {
            "inbound":  [["green", 57], ["blue", 0], ["yellow", 3], ["red", 30]],
            "outbound": [["green", 57], ["blue", 0], ["yellow", 3], ["red", 30]],
            },
    }

    # offsets = [0, 0, 0 , 0] # Dulanto 28-01-25
    # offsets = [0, 2, 28, 38] # Dulanto 29-01-25

    # Aplicando desfases
    for intersection, bounds in programs.items():
        pass


    light_cycles = {number: sum([value for _, value in dict_bounds["inbound"]]) for number, dict_bounds in programs.items()}

    time_max = max(light_cycles.values())*3  # Duración máxima del gráfico (en segundos)


    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, time_max)
    # ax.set_ylim(0, 1500)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Distance (m)")
    ax.set_title("Time-Space Diagram")

    # draw_band(ax, intersection_positions, programs, 5.56, time_max, light_cycles, direction="inbound", color="green")
    # draw_band(ax, intersection_positions, programs, 5.56, time_max, light_cycles, direction="outbound", color="blue")

    # Graficar datos de GPS
    if "Time_Seconds" in df.columns and "Cumulative Length" in df.columns:
        ax.plot(df["Time_Seconds"], df["Cumulative Length"], marker='o', linestyle='-', color='black', label="Vehicle Tracking")

    # Dibujar semáforos
    for (i, position), program, cycle in zip(enumerate(intersection_positions), programs.values(), light_cycles.values()):
        draw_light(ax, position, cycle, time_max, program)

    # Ajustes finales
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()