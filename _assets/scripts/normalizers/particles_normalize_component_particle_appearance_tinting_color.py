from typing import Any

__all__ = ["particles_normalize_component_particle_appearance_tinting_color"]

def particles_normalize_component_particle_appearance_tinting_color(data:dict|str|list) -> list|dict|None:
    if isinstance(data, (str, list)):
        return [data]
