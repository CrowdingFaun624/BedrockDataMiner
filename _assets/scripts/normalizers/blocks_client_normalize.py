from typing import Any

import Utilities.File as File

__all__ = ["blocks_client_normalize"]

def blocks_client_normalize(data:dict[str,File.File[dict[str,Any]]]) -> dict[str,dict[str,Any]]:
    output:dict[str,dict[str,Any]] = {}
    for pack_name, blocks in data.items():
        for block_name, block_data in blocks.read().items():
            if block_name == "format_version": continue
            if block_name not in output:
                output[block_name] = {}
            output[block_name][pack_name] = block_data
    return output
