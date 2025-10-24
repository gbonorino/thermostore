# materials/layer.py
from dataclasses import dataclass, field
from typing import Optional
from .material import Material
import uuid

@dataclass
class Layer:
    """
    Minimal Layer class that references a Material.
    - id: unique id
    - material: Material instance
    - thickness: thickness in meters (float)
    - note: optional string
    """
    material: Material
    thickness: float
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mass_per_unit_area(self) -> Optional[float]:
        """
        Compute mass per unit area (kg/m^2) = density (kg/m^3) * thickness (m).
        Returns None if material density is missing.
        """
        dens = self.material.density()
        if dens is None:
            return None
        return dens * self.thickness

    def thermal_resistance(self) -> Optional[float]:
        """
        Return thermal resistance R = thickness / k (m^2*K/W) if k present.
        """
        k = self.material.thermal_conductivity()
        if k is None or k == 0:
            return None
        return self.thickness / k

    def to_dict(self):
        return {
            "id": self.id,
            "material_id": self.material.id,
            "material_name": self.material.name,
            "thickness": self.thickness,
            "note": self.note,
        }
