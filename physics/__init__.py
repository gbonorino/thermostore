# physics/__init__.py
from .heat_equations import compute_alpha_from_material, build_grid_properties
from .solver import HeatSolver
from .visualization import plot_temperature_profile, plot_time_evolution

__all__ = [
    "compute_alpha_from_material",
    "build_grid_properties",
    "HeatSolver",
    "plot_temperature_profile",
    "plot_time_evolution",
]