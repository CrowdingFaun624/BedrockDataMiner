from typing import Any

import Serializer.Serializer as Serializer

__all__ = ["ManifestSerializer"]

class LineReader():
    
    def __init__(self, lines:list[str]) -> None:
        self.lines = lines
        self.offset = 0
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len {len(self.lines)} at {self.offset}>"

    def read_line(self) -> str:
        output = self.lines[self.offset]
        self.offset += 1
        return output

    def __bool__(self) -> bool:
        return self.offset < len(self.lines)

class ManifestSerializer(Serializer.Serializer):
    
    def parse_clump(self, line_reader:LineReader) -> dict[str,str]:
        lines:list[str] = []
        while line_reader:
            line = line_reader.read_line()
            if len(line.strip()) == 0:
                break
            lines.append(line)
        combined_lines:list[str] = []
        for line in lines:
            if line.startswith(" "):
                combined_lines[-1] += line[1:]
            else:
                combined_lines.append(line)
        output:dict[str,str] = {}
        for combined_line in combined_lines:
            key, value = combined_line.split(": ", maxsplit=1)
            output[key] = value
        return output
    
    def deserialize(self, data: bytes) -> dict[str,Any]:
        lines = data.decode("UTF8").splitlines()
        line_reader = LineReader(lines)
        header_clump:dict[str,Any] = self.parse_clump(line_reader)
        assert "files" not in header_clump
        files:dict[str,str] = {}
        while line_reader:
            clump = self.parse_clump(line_reader)
            assert clump.keys() == {"Name", "SHA-384-Digest"}
            files[clump["Name"]] = clump["SHA-384-Digest"]
        header_clump["files"] = files
        return header_clump
