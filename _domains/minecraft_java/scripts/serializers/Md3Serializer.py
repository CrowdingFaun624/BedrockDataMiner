from itertools import count, takewhile
from typing import TypedDict

from _domains.minecraft_common.scripts.Nbt.DataReader import DataReader
from _domains.minecraft_common.scripts.Nbt.NbtTypes import End
from Component.ComponentFunctions import component_function
from Serializer.Serializer import Serializer

# big thanks to https://icculus.org/~phaethon/q3a/formats/md3format.html

type vec3 = tuple[float, float, float]

class HeaderTypedDict(TypedDict):
    MD3_START: int
    IDENT: int
    VERSION: int
    NAME: str
    FLAGS: int
    NUM_FRAMES: int
    NUM_TAGS: int
    NUM_SKINS: int
    NUM_SURFACES: int
    OFS_FRAMES: int
    OFS_TAGS: int
    OFS_SURFACES: int
    OFS_EOF: int

class FrameTypedDict(TypedDict):
    MIN_BOUNDS: vec3
    MAX_BOUNDS: vec3
    LOCAL_ORIGIN: vec3
    RADIUS: float
    NAME: str

class TagTypedDict(TypedDict):
    NAME: str
    ORIGIN: vec3
    AXIS: tuple[vec3, vec3, vec3]

class ShaderTypedDict(TypedDict):
    NAME: str
    SHADER_INDEX: int

class TriangleTypedDict(TypedDict):
    INDEXES: tuple[int, int, int]

class TexCoordTypedDict(TypedDict):
    ST: tuple[float, float]

class VertexTypedDict(TypedDict):
    X: int
    Y: int
    Z: int
    NORMAL: int

class SurfaceHeaderTypedDict(TypedDict):
    SURFACE_START: int
    IDENT: int
    NAME: str
    FLAGS: int
    NUM_FRAMES: int
    NUM_SHADERS: int
    NUM_VERTS: int
    NUM_TRIANGLES: int
    OFS_TRIANGLES: int
    OFS_SHADERS: int
    OFS_ST: int
    OFS_XYZNORMAL: int
    OFS_END: int

class SurfaceTypedDict(TypedDict):
    header: SurfaceHeaderTypedDict
    shaders: list[ShaderTypedDict]
    triangles: list[TriangleTypedDict]
    tex_coords: list[TexCoordTypedDict]
    vertices: list[VertexTypedDict]

class Md3TypedDict(TypedDict):
    header: HeaderTypedDict
    frames: list[FrameTypedDict]
    tags: list[TagTypedDict]
    surfaces: list[SurfaceTypedDict]

MAX_QPATH:int = 64

def parse_s16(reader:DataReader) -> int:
    return reader.unpack_tuple("h", 2, End.LITTLE)

def parse_s32(reader:DataReader) -> int:
    return reader.unpack_tuple("i", 4, End.LITTLE)

def parse_f32(reader:DataReader) -> float:
    return reader.unpack_tuple("f", 4, End.LITTLE)

def parse_vec3(reader:DataReader) -> vec3:
    return reader.unpack("fff", 12, End.LITTLE)

# DEBUG: PLASE NO COMMITY
def no(thing:tuple[int,...]) -> bool:
    try:
        "".join(chr(byte) for byte in takewhile(lambda byte: byte != 0, thing))
        return False
    except:
        return True

def parse_string(reader:DataReader, length:int) -> str:
    output_bytes:tuple[int,...] = reader.unpack("B" * length, length, End.LITTLE)
    return "".join(chr(byte) for byte in takewhile(lambda byte: byte != 0, output_bytes))

def parse_string_newline_terminated(reader:DataReader) -> str:
    return "".join(chr(byte) for byte in takewhile(lambda byte: byte != 0x0A, (reader.unpack_tuple("B", 1, End.LITTLE) for _ in count())))

def parse_header(reader:DataReader) -> HeaderTypedDict:
    return {
        "MD3_START": 0, # assume no initial offset
        "IDENT": parse_s32(reader),
        "VERSION": parse_s32(reader),
        "NAME": parse_string(reader, MAX_QPATH),
        "FLAGS": parse_s32(reader),
        "NUM_FRAMES": parse_s32(reader),
        "NUM_TAGS": parse_s32(reader),
        "NUM_SURFACES": parse_s32(reader),
        "NUM_SKINS": parse_s32(reader),
        "OFS_FRAMES": parse_s32(reader),
        "OFS_TAGS": parse_s32(reader),
        "OFS_SURFACES": parse_s32(reader),
        "OFS_EOF": parse_s32(reader),
    }

def parse_frame(reader:DataReader) -> FrameTypedDict:
    return {
        "MIN_BOUNDS": parse_vec3(reader),
        "MAX_BOUNDS": parse_vec3(reader),
        "LOCAL_ORIGIN": parse_vec3(reader),
        "RADIUS": parse_f32(reader),
        "NAME": parse_string_newline_terminated(reader),
    }

def parse_tag(reader:DataReader) -> TagTypedDict:
    return {
        "NAME": parse_string(reader, MAX_QPATH),
        "ORIGIN": parse_vec3(reader),
        "AXIS": (parse_vec3(reader), parse_vec3(reader), parse_vec3(reader)),
    }

def parse_surface_header(reader:DataReader) -> SurfaceHeaderTypedDict:
    return {
        "SURFACE_START": reader.position,
        "IDENT": parse_s32(reader),
        "NAME": parse_string(reader, MAX_QPATH),
        "FLAGS": parse_s32(reader),
        "NUM_FRAMES": parse_s32(reader),
        "NUM_SHADERS": parse_s32(reader),
        "NUM_VERTS": parse_s32(reader),
        "NUM_TRIANGLES": parse_s32(reader),
        "OFS_TRIANGLES": parse_s32(reader),
        "OFS_SHADERS": parse_s32(reader),
        "OFS_ST": parse_s32(reader),
        "OFS_XYZNORMAL": parse_s32(reader),
        "OFS_END": parse_s32(reader),
    }

def parse_shader(reader:DataReader) -> ShaderTypedDict:
    return {
        "NAME": parse_string(reader, MAX_QPATH),
        "SHADER_INDEX": parse_s32(reader),
    }

def parse_triangle(reader:DataReader) -> TriangleTypedDict:
    return {
        "INDEXES": (parse_s32(reader), parse_s32(reader), parse_s32(reader)),
    }

def parse_tex_coord(reader:DataReader) -> TexCoordTypedDict:
    return {
        "ST": (parse_f32(reader), parse_f32(reader)),
    }

def parse_vertex(reader:DataReader) -> VertexTypedDict:
    return {
        "X": parse_s16(reader),
        "Y": parse_s16(reader),
        "Z": parse_s16(reader),
        "NORMAL": parse_s16(reader),
    }

def parse_surface(reader:DataReader) -> SurfaceTypedDict:
    header = parse_surface_header(reader)
    reader.position = header["SURFACE_START"] + header["OFS_SHADERS"]
    shaders = [parse_shader(reader) for _ in range(header["NUM_SHADERS"])]
    reader.position = header["SURFACE_START"] + header["OFS_TRIANGLES"]
    triangles = [parse_triangle(reader) for _ in range(header["NUM_TRIANGLES"])]
    reader.position = header["SURFACE_START"] + header["OFS_ST"]
    tex_coords = [parse_tex_coord(reader) for _ in range(header["NUM_VERTS"])]
    reader.position = header["SURFACE_START"] + header["OFS_XYZNORMAL"]
    vertices = [parse_vertex(reader) for _ in range(header["NUM_FRAMES"] * header["NUM_VERTS"])]
    reader.position = header["SURFACE_START"] + header["OFS_END"]
    return {
        "header": header,
        "shaders": shaders,
        "triangles": triangles,
        "tex_coords": tex_coords,
        "vertices": vertices,
    }

@component_function()
class Md3Serializer(Serializer):

    def deserialize(self, data: bytes) -> Md3TypedDict:
        reader = DataReader(data)
        header = parse_header(reader)
        reader.position = header["MD3_START"] + header["OFS_FRAMES"]
        frames = [parse_frame(reader) for _ in range(header["NUM_FRAMES"])]
        reader.position = header["MD3_START"] + header["OFS_TAGS"]
        tags = [parse_tag(reader) for _ in range(header["NUM_TAGS"])]
        reader.position = header["MD3_START"] + header["OFS_SURFACES"]
        surfaces = [parse_surface(reader) for _ in range(header["NUM_SURFACES"])]
        return {
            "header": header,
            "frames": frames,
            "tags": tags,
            "surfaces": surfaces
        }
