# materials/material.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid

@dataclass
class Material:
    """
    Minimal Material class.
    - id: unique identifier (string)
    - name: human-friendly name
    - props: arbitrary properties dictionary (e.g., density, color, thermal_conductivity)
    """
    name: str
    props: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def density(self) -> Optional[float]:
        """Convenience accessor for density (returns None if not set)."""
        d = self.props.get("density")
        try:
            return float(d) if d is not None else None
        except (ValueError, TypeError):
            return None

    def specific_heat(self) -> Optional[float]:
        """Return specific heat capacity in J/(kg·K) if present, else None."""
        c = self.props.get("specific_heat")
        try:
            return float(c) if c is not None else None
        except (ValueError, TypeError):
            return None

    def thermal_conductivity(self) -> Optional[float]:
        """Return thermal conductivity in W/(m·K) if present, else None."""
        k = self.props.get("thermal_conductivity")
        try:
            return float(k) if k is not None else None
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "props": self.props}
