# example.py
from materials import Material, Layer, Database
from physics.solver import HeatSolver
from physics.visualization import plot_temperature_profile, plot_time_evolution

def main():
    # --- create materials with required properties ---
    # Units: density kg/m^3, specific_heat J/(kg*K), thermal_conductivity W/(m*K)
    concrete = Material(
        "Concrete",
        props={"density": 2400, "specific_heat": 880, "thermal_conductivity": 1.7},
    )
    eps = Material(
        "EPS_Foam",
        props={"density": 30, "specific_heat": 1400, "thermal_conductivity": 0.035},
    )

    # --- create layers ---
    layer_conc = Layer(material=concrete, thickness=0.2, note="floor slab")
    layer_eps = Layer(material=eps, thickness=0.1, note="insulation")

    # Optional: persist to DB (materials.database stores props as JSON)
    db = Database(":memory:")
    db.add_material(concrete)
    db.add_material(eps)

    db.add_layer(layer_conc)
    db.add_layer(layer_eps)

    print("Materials in DB:")
    for m in db.list_materials():
        print(m.to_dict())

    print("\nLayers in DB:")
    for l in db.list_layers():
        print(l.to_dict(), "mass_per_m2=", l.mass_per_unit_area())

    db.close()

    # --- run physics solver ---
    layers = [layer_conc, layer_eps]
    solver = HeatSolver(layers, dx_target=0.01)  # ~1 cm cells
    # simulate 2 hours (7200 s). Let left boundary be 310K (hot side), right boundary 293.15K
    times, T_record = solver.solve(t_final=3600 * 2, dt=None, T0=293.15, bc=(310.0, 293.15), record_every=50)

    # final temperature profile
    x = solver.x
    final_T = T_record[-1]

    print("\nFinal temperatures (K):")
    for xi, Ti in zip(x, final_T):
        print(f"x={xi:.3f} m -> T={Ti:.2f} K")

    # --- visualize ---
    plot_temperature_profile(x, final_T, title="Final temperature profile after 2 hours")
    plot_time_evolution(times, x, T_record)

if __name__ == "__main__":
    main()
