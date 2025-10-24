# materials/database.py
"""
Very small SQLite-backed persistence for Materials and Layers.
Uses Python's sqlite3 from the stdlib.
"""
import sqlite3
from typing import Iterable, Optional, List, Dict, Any
from .material import Material
from .layer import Layer
import json

CREATE_MATERIALS = """
CREATE TABLE IF NOT EXISTS materials (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    props TEXT
);
"""

CREATE_LAYERS = """
CREATE TABLE IF NOT EXISTS layers (
    id TEXT PRIMARY KEY,
    material_id TEXT NOT NULL,
    thickness REAL NOT NULL,
    note TEXT,
    FOREIGN KEY(material_id) REFERENCES materials(id)
);
"""


class Database:
    def __init__(self, path: str = ":memory:"):
        self.path = path
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        cur = self._conn.cursor()
        cur.execute(CREATE_MATERIALS)
        cur.execute(CREATE_LAYERS)
        self._conn.commit()

    def add_material(self, material: Material) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO materials (id, name, props) VALUES (?, ?, ?)",
            (material.id, material.name, json.dumps(material.props)),
        )
        self._conn.commit()

    def get_material(self, material_id: str) -> Optional[Material]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
        row = cur.fetchone()
        if row is None:
            return None
        props = json.loads(row["props"]) if row["props"] else {}
        return Material(name=row["name"], props=props, id=row["id"])

    def list_materials(self) -> List[Material]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM materials")
        rows = cur.fetchall()
        result = []
        for r in rows:
            props = json.loads(r["props"]) if r["props"] else {}
            result.append(Material(name=r["name"], props=props, id=r["id"]))
        return result

    def add_layer(self, layer: Layer) -> None:
        # Ensure material exists
        if self.get_material(layer.material.id) is None:
            raise ValueError("Material must be added to DB before adding a layer that references it.")
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO layers (id, material_id, thickness, note) VALUES (?, ?, ?, ?)",
            (layer.id, layer.material.id, layer.thickness, layer.note),
        )
        self._conn.commit()

    def list_layers(self) -> List[Layer]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT l.id as lid, l.thickness, l.note, m.id as mid, m.name as mname, m.props as mprops "
            "FROM layers l JOIN materials m ON l.material_id = m.id"
        )
        rows = cur.fetchall()
        result: List[Layer] = []
        for r in rows:
            props = json.loads(r["mprops"]) if r["mprops"] else {}
            mat = Material(name=r["mname"], props=props, id=r["mid"])
            layer = Layer(material=mat, thickness=r["thickness"], note=r["note"], id=r["lid"])
            result.append(layer)
        return result

    def close(self):
        self._conn.close()
