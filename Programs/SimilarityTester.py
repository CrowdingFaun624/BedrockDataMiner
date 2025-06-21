from types import EllipsisType
from typing import Any

import Domain.Domain as Domain
from Structure.Structure import Structure
from Structure.StructureEnvironment import (
    ComparisonEnvironment,
    EnvironmentType,
    StructureEnvironment,
)
from Structure.StructureInfo import StructureInfo
from Utilities.Exceptions import StructureError
from Utilities.Trace import Trace


def try_open_json(data_string:str, domain:"Domain.Domain") -> Any|EllipsisType:
    try:
        return domain.json_decoder().decode(data_string)
    except:
        return ...

def try_open_file(data_string:str, domain:"Domain.Domain") -> Any|EllipsisType:
    try:
        with open(data_string, "rt") as f:
            return domain.json_decoder().decode(f.read())
    except:
        return ...

DATA_OPEN_FUNCTION = [try_open_json]

def parse_data(data_string:str, domain:"Domain.Domain") -> Any:
    data = ...
    for function in DATA_OPEN_FUNCTION:
        if (data := function(data_string, domain)):
            break
    if data is ...:
        raise RuntimeError()
    return data

def ensure_not_ellipsis[A](data:A|EllipsisType, trace:Trace, structure:Structure, domain:"Domain.Domain") -> A:
    texts:list[str] = list(trace.stringify())
    if trace.has_exceptions:
        if (log := domain.logs.get("structure_log")) is not None and log.supports_type(log, str):
            log.write(f"-------- {trace.exception_count} EXCEPTIONS IN {structure.full_name} --------\n\n")
            log.write("\n".join(texts))
        for text in texts:
            print(text)
    if data is ... or trace.has_exceptions:
        raise StructureError(structure)
    return data

def main(domain:"Domain.Domain") -> None:
    version = domain.versions[next(reversed(domain.versions))] # type: ignore
    structure_name = input("Structure full name: ")
    structure = domain.script_referenceable.get(structure_name, Structure)
    data1 = parse_data(input("Normalized data 1: "), domain)
    data2 = parse_data(input("Normalized data 2: "), domain)
    trace = Trace()
    structure_environment = StructureEnvironment(EnvironmentType.similarity_testing, domain)
    environment = ComparisonEnvironment(structure_environment, None, [(version, StructureInfo({}, domain, ""))], [])
    containerized_data1 = ensure_not_ellipsis(structure.containerize(data1, trace, environment[0]), trace, structure, domain)
    containerized_data2 = ensure_not_ellipsis(structure.containerize(data2, trace, environment[0]), trace, structure, domain)
    similarity, identical = ensure_not_ellipsis(structure.get_similarity(containerized_data1, containerized_data2, 0, 0, trace, environment), trace, structure, domain)
    if similarity == 1.0:
        print(f"Similarity of {similarity:.5f}; {"completely" if identical else "not"} identical")
    else:
        print(f"Similarity of {similarity:.5f}")
