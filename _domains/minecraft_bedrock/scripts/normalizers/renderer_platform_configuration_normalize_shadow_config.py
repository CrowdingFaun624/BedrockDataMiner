from typing import Any

__all__ = ["renderer_platform_configurations_normalize_shadow_config"]

def renderer_platform_configurations_normalize_shadow_config(data:Any) -> Any|None:
    if "file" in data:
        return {"shadow_config": data}
