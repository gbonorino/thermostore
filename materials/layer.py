# materials/layer.py
from dataclasses import dataclass, field
from typing import Optional
from .material import Material
import uuid

@dataclass
class Layer:
    """
    Clase que representa una capa térmica en un sistema de transferencia de calor.
    
    Una capa térmica está caracterizada por su material, espesor y conductividad térmica.
    La conductividad puede especificarse directamente o obtenerse del material asociado.
    
    Atributos:
        material (Material): Instancia del material que compone la capa.
        thickness (float): Espesor de la capa en metros (m). Debe ser un valor positivo.
        conductivity (Optional[float]): Conductividad térmica de la capa en W/(m·K).
            Si es None, se obtendrá del material asociado. Si se proporciona, tiene
            prioridad sobre la conductividad del material.
        note (str): Nota opcional o descripción adicional de la capa.
        id (str): Identificador único de la capa (generado automáticamente si no se proporciona).
    
    Ejemplo:
        >>> material = Material("Concreto", props={"thermal_conductivity": 1.7})
        >>> layer = Layer(material=material, thickness=0.2, conductivity=1.7)
        >>> print(layer.thermal_resistance())
        0.11764705882352941
    """
    material: Material
    thickness: float
    conductivity: Optional[float] = None
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
        Calcula la resistencia térmica de la capa.
        
        La resistencia térmica se calcula como R = espesor / conductividad (m²·K/W).
        Utiliza la conductividad de la capa si está disponible, de lo contrario
        obtiene la conductividad del material asociado.
        
        Returns:
            Optional[float]: Resistencia térmica en m²·K/W, o None si la conductividad
                no está disponible o es cero.
        """
        k = self.get_conductivity()
        if k is None or k == 0:
            return None
        return self.thickness / k
    
    def get_conductivity(self) -> Optional[float]:
        """
        Obtiene la conductividad térmica de la capa.
        
        Retorna la conductividad especificada directamente en la capa si está disponible,
        de lo contrario obtiene la conductividad del material asociado.
        
        Returns:
            Optional[float]: Conductividad térmica en W/(m·K), o None si no está disponible.
        """
        if self.conductivity is not None:
            return self.conductivity
        return self.material.thermal_conductivity()

    def to_dict(self):
        """
        Convierte la capa a un diccionario para serialización.
        
        Returns:
            dict: Diccionario con los atributos principales de la capa.
        """
        return {
            "id": self.id,
            "material_id": self.material.id,
            "material_name": self.material.name,
            "thickness": self.thickness,
            "conductivity": self.get_conductivity(),
            "note": self.note,
        }
