import matplotlib.pyplot as plt
import numpy as np
from icecream import ic

# Configuración de las intersecciones
intersection_positions = [100, 300, 500]  # Distancia en metros entre las intersecciones
velocity = 20 # km/h
programs = {
    1: {
        "inbound": {"green": 50, "left": 0, "amber": 3, "red": 37},
        "outbound": {"green": 50, "left": 0, "amber": 3, "red": 37},
        },
    2: {
        "inbound": {"green": 50, "left": 0, "amber": 3, "red": 37},
        "outbound": {"green": 50, "left": 0, "amber": 3, "red": 37},
        },
    3: {
        "inbound": {"green": 50, "left": 0, "amber": 3, "red": 37},
        "outbound": {"green": 50, "left": 0, "amber": 3, "red": 37},
        },
}

light_cycles = {number: sum(dict_bounds["inbound"].values()) for number, dict_bounds in programs.items()}

time_max = max(light_cycles.values())*5  # Duración máxima del gráfico (en segundos)

def _draw_segments(ax, position_range, t_start, phases, colors):
    t = t_start
    for phase, duration in phases.items():
        ax.fill_betweenx(
            position_range,
            t,
            t + duration,
            color=colors[phase],
            alpha=1,
        )
        t += duration

# Función principal para dibujar el estado del semáforo
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

def draw_band(ax, intersection_positions, programs, velocity, time_max, direction="inbound", color="green"):
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

# Configuración del gráfico
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, time_max)
ax.set_ylim(0, 600)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Distance (m)")
ax.set_title("Time-Space Diagram for Two Intersections")

# Dibujar semáforos
for (i, position), program, cycle in zip(enumerate(intersection_positions), programs.values(), light_cycles.values()):
    draw_light(ax, position, cycle, time_max, program)

draw_band(ax, intersection_positions, programs, 5.56, time_max, direction="inbound", color="green")

# Ajustes finales
ax.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()