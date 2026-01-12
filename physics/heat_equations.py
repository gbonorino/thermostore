# physics/heat_equations.py
from typing import List, Tuple
import numpy as np
from materials.layer import Layer
from materials.material import Material

def compute_alpha_from_material(mat: Material) -> float:
    """
    Compute thermal diffusivity alpha = k / (rho * cp) [m^2/s].
    Raises ValueError if required properties are missing.
    """
    k = mat.thermal_conductivity()
    rho = mat.density()
    cp = mat.specific_heat()
    if k is None or rho is None or cp is None:
        raise ValueError(f"Material '{mat.name}' missing one of k/rho/cp in props.")
    if rho <= 0 or cp <= 0:
        raise ValueError("rho and cp must be positive.")
    return float(k) / (float(rho) * float(cp))

def build_grid_properties(layers: List[Layer], dx_target: float = 0.005
                         ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build a 1D spatial grid for the list of layers.
    - dx_target: approximate desired cell width (m). Each layer is subdivided into n cells.
    Returns (x, k_cell, rho_cp_cell) arrays:
    - x: cell center positions (m)
    - k_cell: thermal conductivity per cell (W/(m*K))
    - rho_cp_cell: product rho*cp per cell (J/(m^3*K))
    """
    xs = []
    ks = []
    rho_cps = []

    current_x = 0.0
    for layer in layers:
        L = float(layer.thickness)
        if L <= 0:
            raise ValueError("Layer thickness must be positive.")
        # number of cells in this layer (at least 1)
        n = max(1, int(max(1, round(L / dx_target))))
        dx = L / n
        k = layer.get_conductivity()
        rho = layer.material.density()
        cp = layer.material.specific_heat()
        if k is None or rho is None or cp is None:
            raise ValueError(f"Layer's material '{layer.material.name}' missing k, rho, or cp.")
        for i in range(n):
            center = current_x + (i + 0.5) * dx
            xs.append(center)
            ks.append(float(k))
            rho_cps.append(float(rho) * float(cp))
        current_x += L

    import numpy as np
    return np.array(xs), np.array(ks), np.array(rho_cps)
