# physics/solver.py
import numpy as np
from typing import Tuple, Optional, List
from .heat_equations import build_grid_properties
from materials.layer import Layer

class HeatSolver:
    """
    Simple explicit 1D heat equation solver.
    Equation: rho*cp * dT/dt = d/dx (k * dT/dx)

    Usage:
      solver = HeatSolver(layers)
      t, Ts = solver.solve(t_final=3600, dt=None, T0=293.15, bc=(300, 293.15))
    """

    def __init__(self, layers: List[Layer], dx_target: float = 0.005):
        self.layers = layers
        # create grid and per-cell properties
        self.x, self.k, self.rho_cp = build_grid_properties(layers, dx_target=dx_target)
        # compute uniform dx array (distance between adjacent cell centers)
        self.dx = np.diff(self.x)
        if len(self.dx) == 0:
            # single cell -> arbitrarily assign dx = layer thickness
            self.dx_uniform = 1.0
        else:
            # assume near-uniform
            self.dx_uniform = float(np.mean(self.dx))

    def _compute_stable_dt(self) -> float:
        """
        For explicit scheme, stability roughly dt <= dx^2 / (2 * alpha_max),
        where alpha = k/(rho*cp).
        We'll compute alpha per cell and use the most restrictive.
        """
        alphas = self.k / self.rho_cp
        alpha_max = float(np.max(alphas))
        dt_stable = (self.dx_uniform ** 2) / (2.0 * alpha_max)
        # safety factor
        return dt_stable * 0.5

    def solve(
        self,
        t_final: float,
        dt: Optional[float] = None,
        T0: float = 293.15,
        bc: Tuple[float, float] = (300.0, 293.15),
        record_every: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve from t=0 to t=t_final (seconds).
        - dt: time step in seconds. If None, chosen by stability rule.
        - T0: initial temperature (K)
        - bc: (T_left, T_right) Dirichlet boundary conditions (K)
        - record_every: store solution every N time steps (for memory control)
        Returns:
          times: array of times
          T_record: array shape (n_records, n_cells)
        """
        n_cells = len(self.x)
        if n_cells == 0:
            raise ValueError("No grid cells created.")

        if dt is None:
            dt = self._compute_stable_dt()

        # initialize temperature array
        T = np.ones(n_cells) * float(T0)

        # precompute conductances between adjacent cell centers:
        # use harmonic mean of k and distance dx between centers
        # conductance per unit area (W/(m*K)) when combined with dx is handled in finite-difference below
        xs = self.x
        ks = self.k
        rho_cp = self.rho_cp
        # prepare arrays for neighbor indices
        nsteps = max(1, int(np.ceil(t_final / dt)))
        n_records = (nsteps // record_every) + 1

        T_record = np.zeros((n_records, n_cells))
        times = np.zeros(n_records)

        rec_idx = 0
        T_record[rec_idx] = T.copy()
        times[rec_idx] = 0.0
        rec_idx += 1

        # Precompute dxs between centers: left/right distances
        # For interior cell i, left interface at (x[i]-x[i-1])/2 etc.
        # We'll implement second-order central difference with cell-centered properties.
        for step in range(1, nsteps + 1):
            T_new = T.copy()
            # apply interior updates
            for i in range(n_cells):
                # left neighbor
                if i == 0:
                    T_left = bc[0]
                    x_left = xs[i] - (xs[i+1] - xs[i]) / 2 if n_cells > 1 else xs[i] - self.dx_uniform/2
                    k_left = ks[i]  # approximate
                    dx_left = xs[i] - (xs[i] - (xs[i+1] - xs[i]) / 2) if n_cells > 1 else self.dx_uniform
                else:
                    T_left = T[i-1]
                    dx_left = xs[i] - xs[i-1]
                    # harmonic average of k between cells
                    k_left = 2.0 * ks[i] * ks[i-1] / (ks[i] + ks[i-1]) if (ks[i] + ks[i-1]) != 0 else 0.0

                # right neighbor
                if i == n_cells - 1:
                    T_right = bc[1]
                    x_right = xs[i] + (xs[i] - xs[i-1]) / 2 if n_cells > 1 else xs[i] + self.dx_uniform/2
                    k_right = ks[i]
                    dx_right = (x_right - xs[i]) if n_cells > 1 else self.dx_uniform
                else:
                    T_right = T[i+1]
                    dx_right = xs[i+1] - xs[i]
                    k_right = 2.0 * ks[i] * ks[i+1] / (ks[i] + ks[i+1]) if (ks[i] + ks[i+1]) != 0 else 0.0

                # discrete fluxes: approximate d/dx (k dT/dx) ~ (k_right*(T_right - T)/dx_right - k_left*(T - T_left)/dx_left) / dx_cell
                dx_cell = 0.5 * (dx_left + dx_right)
                flux_right = k_right * (T_right - T[i]) / dx_right if dx_right != 0 else 0.0
                flux_left = k_left * (T[i] - T_left) / dx_left if dx_left != 0 else 0.0
                dTdt = (flux_right - flux_left) / dx_cell / rho_cp[i]
                T_new[i] = T[i] + dt * dTdt

            T = T_new

            if step % record_every == 0:
                times[rec_idx] = step * dt
                T_record[rec_idx] = T.copy()
                rec_idx += 1

        # trim records if needed
        T_record = T_record[:rec_idx]
        times = times[:rec_idx]
        return times, T_record