from typing import Any

import Utilities.File as File

__all__ = ["blocks_client_normalize"]

def blocks_client_normalize(data:dict[str,File.File[dict[str,Any]]]) -> File.FakeFile[dict[str,dict[str,Any]]]:
    output:dict[str,dict[str,Any]] = {}
    file_hashes:list[int] = []
    for pack_name, blocks in data.items():
        file_hashes.append(blocks.hash)
        for block_name, block_data in blocks.data.items():
            if block_name == "format_version": continue
            if block_name not in output:
                output[block_name] = {}
            output[block_name][pack_name] = block_data
    combined_hash = hash(tuple(file_hashes))
    return File.FakeFile("combined_blocks_file", output, combined_hash)
