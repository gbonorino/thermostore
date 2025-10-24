# physics/visualization.py
import matplotlib.pyplot as plt
from typing import Tuple
import numpy as np

def plot_temperature_profile(x: np.ndarray, T: np.ndarray, title: str = "Temperature profile"):
    """
    Plot temperature vs position.
    x: positions (m) of cell centers
    T: temperatures (K) for each cell
    """
    plt.figure(figsize=(8, 3.5))
    plt.plot(x, T, marker="o")
    plt.xlabel("x (m)")
    plt.ylabel("Temperature (K)")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_time_evolution(times, x, T_record, indices=None):
    """
    Plot temperature vs time for selected positions (cell indices).
    - indices: list of cell indices to plot. If None plot center and two edges.
    """
    if indices is None:
        n = len(x)
        indices = [0, n // 2, n - 1] if n >= 3 else list(range(n))

    plt.figure(figsize=(8, 4))
    for idx in indices:
        label = f"x={x[idx]:.3f} m (cell {idx})"
        plt.plot(times, T_record[:, idx], label=label)
    plt.xlabel("Time (s)")
    plt.ylabel("Temperature (K)")
    plt.title("Temperature evolution")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()