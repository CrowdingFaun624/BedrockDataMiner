from typing import Any

__all__ = ["ui_separate_variables"]

def ui_separate_variables(data:dict[str,Any]) -> None:
    variables:dict[str,Any] = {}
    for parameter_name, parameter_value in data.items():
        if parameter_name.startswith("$"):
            variables[parameter_name] = parameter_value
    for variable_name in variables.keys():
        del data[variable_name] # variables are not wanted in the element afterward
    assert "$variables" not in data
    data["$variables"] = variables
