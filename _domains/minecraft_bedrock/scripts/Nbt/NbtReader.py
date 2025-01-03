import gzip
import traceback
from typing import BinaryIO

import _domains.minecraft_bedrock.scripts.Nbt.DataReader as DataReader
import _domains.minecraft_bedrock.scripts.Nbt.Endianness as Endianness
import _domains.minecraft_bedrock.scripts.Nbt.NbtExceptions as NbtExceptions
import _domains.minecraft_bedrock.scripts.Nbt.NbtTypes as NbtTypes
import _domains.minecraft_bedrock.scripts.Nbt.SnbtParser as SnbtParser
import Utilities.UserInput as UserInput


def unpack_bytes(data:bytes, gzipped:bool=True, endianness:Endianness.End|None=None) -> tuple[str|None,NbtTypes.TAG]:
    if endianness is None: endianness = Endianness.End.BIG
    if gzipped:
        data = gzip.decompress(data)
    data_reader = DataReader.DataBytesReader(data)
    name, output = NbtTypes.parse_compound_item_from_bytes(data_reader, endianness)
    return name, output

def unpack_file(data:BinaryIO, gzipped:bool=True, endianness:Endianness.End|None=None) -> tuple[str|None,NbtTypes.TAG]:
    if endianness is None: endianness = Endianness.End.BIG
    if gzipped:
        return unpack_bytes(data.read(), gzipped=True, endianness=endianness)
    data_reader = DataReader.DataFileReader(data)
    name, output = NbtTypes.parse_compound_item_from_bytes(data_reader, endianness)
    return name, output

def unpack_snbt(data:str) -> NbtTypes.TAG:
    return SnbtParser.parse(data)

def main_read_file() -> None:
    from pathlib import Path
    user_input = None
    path = None
    while path is None or not path.exists():
        user_input = input("Place nbt file in Programs directory and type its name: ")
        path = Path(f"./Programs/{user_input}")
    is_gzipped, endianness = UserInput.input_single({"yl": (True, Endianness.End.LITTLE), "yb": (True, Endianness.End.BIG), "nl": (False, Endianness.End.LITTLE), "nb": (False, Endianness.End.BIG)}, "g-zippedness and endianness", show_options=True)
    with open(path, "rb") as f:
        data = unpack_file(f, gzipped=is_gzipped, endianness=endianness)
    print(*data)

def string_test(data:NbtTypes.TAG|type[Exception], data_string:str|None=None) -> None:
    if data_string is None:
        data_string = str(data)
    reparsed_data = None
    try:
        reparsed_data = SnbtParser.parse(data_string)
    except Exception as e:
        if not isinstance(data, Exception):
            traceback.print_exception(e)
        else:
            if type(e) != data:
                raise NbtExceptions.NbtTestFailureError(f"Error is not expected from {data_string}!")
    if not isinstance(data, Exception):
        if reparsed_data is None:
            raise NbtExceptions.NbtTestFailureError(f"Failed to parse data {data_string}!")
        if data != reparsed_data:
            raise NbtExceptions.NbtTestFailureError(f"Parsed data is not equal to original data: original: {data}, reparsed: {reparsed_data}")
    else:
        if reparsed_data is not None:
            raise NbtExceptions.NbtTestFailureError(f"Expected an error from {data_string}, {reparsed_data}")

def main_string_demo() -> None:
    # byte test
    string_test(NbtTypes.TAG_Byte(0))
    string_test(NbtTypes.TAG_Byte(1))
    string_test(NbtTypes.TAG_Byte(127))
    string_test(NbtTypes.TAG_Byte(0), "false")
    string_test(NbtTypes.TAG_Byte(1), "true")
    string_test(NbtTypes.TAG_Byte(-128))
    string_test(NbtExceptions.SnbtParseError, "-129b")
    string_test(NbtExceptions.SnbtParseError, "128b")
    string_test(NbtTypes.TAG_Byte(55), "55B")

    # short test
    string_test(NbtTypes.TAG_Short(32767))
    string_test(NbtTypes.TAG_Short(-32768))
    string_test(NbtTypes.TAG_Short(0))
    string_test(NbtExceptions.SnbtParseError, "32768s")
    string_test(NbtExceptions.SnbtParseError, "-32769s")
    string_test(NbtTypes.TAG_Short(256), "256S")

    # int test
    string_test(NbtTypes.TAG_Int(2147483647))
    string_test(NbtTypes.TAG_Int(-2147483648))
    string_test(NbtTypes.TAG_Int(0))
    string_test(NbtExceptions.SnbtParseError, "2147483648")
    string_test(NbtExceptions.SnbtParseError, "-2147483649")
    string_test(NbtExceptions.SnbtParseError, "333i")

    # long test
    string_test(NbtTypes.TAG_Long(9223372036854775807))
    string_test(NbtTypes.TAG_Long(-9223372036854775808))
    string_test(NbtTypes.TAG_Long(0))
    string_test(NbtExceptions.SnbtParseError, "9223372036854775808l")
    string_test(NbtExceptions.SnbtParseError, "-9223372036854775809l")
    string_test(NbtTypes.TAG_Long(3037), "3037L")

    # float test
    string_test(NbtTypes.TAG_Float(937.50)) # keeping the decimal as a power of two because it's a float
    string_test(NbtTypes.TAG_Float(-123.125))
    string_test(NbtExceptions.SnbtParseError, "123.f")
    string_test(NbtTypes.TAG_Float(999.96875), "999.96875F")

    # double test
    string_test(NbtTypes.TAG_Double(937.50), "937.50")
    string_test(NbtTypes.TAG_Double(937.50), "937.50d")
    string_test(NbtTypes.TAG_Double(937.50), "937.50D")
    string_test(NbtTypes.TAG_Double(-123.125))
    string_test(NbtExceptions.SnbtParseError, "123.d")

    # string test
    string_test(NbtTypes.TAG_String("Hi"))
    string_test(NbtTypes.TAG_String("Woah there buckaroo")) # for some reason is my default random string
    string_test(NbtTypes.TAG_String(""))
    string_test(NbtTypes.TAG_String("Hi"), "'Hi'")
    string_test(NbtTypes.TAG_String("英語以外の文字をテストする"))
    string_test(NbtTypes.TAG_String("This thi\\ng has \t\\\"escape\" characters!"), "\"This thi\\\\ng has \t\\\\\\\"escape\\\" characters!\"")
    string_test(NbtExceptions.SnbtParseError, "'Hi\"")
    string_test(NbtExceptions.SnbtParseError, "\"Hi'")
    string_test(NbtExceptions.SnbtParseError, "\"Hi")
    string_test(NbtExceptions.SnbtParseError, "\"Hi\\")
    string_test(NbtExceptions.SnbtParseError, "\"")
    string_test(NbtExceptions.SnbtParseError, "bob") # quoteless strings are not supported to avoid silent errors

    # list test
    string_test(NbtTypes.TAG_List([NbtTypes.TAG_Byte(125)]))
    string_test(NbtTypes.TAG_List([NbtTypes.TAG_Byte(125), NbtTypes.TAG_Byte(123)]))
    string_test(NbtTypes.TAG_List([NbtTypes.TAG_Double(125.25), NbtTypes.TAG_Double(123.875)]))
    string_test(NbtTypes.TAG_List([NbtTypes.TAG_String("wow"), NbtTypes.TAG_String("truly incredible")]))
    string_test(NbtTypes.TAG_List([]))
    string_test(NbtTypes.TAG_List([NbtTypes.TAG_String("wow"), NbtTypes.TAG_String("truly incredible")]), "[   \"wow\"  , \"truly incredible\"  ]")
    string_test(NbtExceptions.SnbtParseError, "[66b, 4299L]")
    string_test(NbtExceptions.SnbtParseError, "[66l, 4299L")
    string_test(NbtExceptions.SnbtParseError, "[")

    # byte array test
    string_test(NbtTypes.TAG_Byte_Array([NbtTypes.TAG_Byte(125)]))
    string_test(NbtTypes.TAG_Byte_Array([NbtTypes.TAG_Byte(125), NbtTypes.TAG_Byte(123)]))
    string_test(NbtTypes.TAG_Byte_Array([]))
    string_test(NbtTypes.TAG_Byte_Array([NbtTypes.TAG_Byte(1), NbtTypes.TAG_Byte(0)]), "[B;   true , false ]")
    string_test(NbtExceptions.SnbtParseError, "[B; 0b, 1]")
    string_test(NbtExceptions.SnbtParseError, "[B; 0b, 1b")
    string_test(NbtExceptions.SnbtParseError, "[B;")

    # int array test
    string_test(NbtTypes.TAG_Int_Array([NbtTypes.TAG_Int(125)]))
    string_test(NbtTypes.TAG_Int_Array([NbtTypes.TAG_Int(125), NbtTypes.TAG_Int(123)]))
    string_test(NbtTypes.TAG_Int_Array([]))
    string_test(NbtTypes.TAG_Int_Array([NbtTypes.TAG_Int(1), NbtTypes.TAG_Int(0)]), "[I;   1 , 0 ]")
    string_test(NbtExceptions.SnbtParseError, "[I; 0b, 1]")
    string_test(NbtExceptions.SnbtParseError, "[I; 0, 1")
    string_test(NbtExceptions.SnbtParseError, "[I;")

    # long array test
    string_test(NbtTypes.TAG_Long_Array([NbtTypes.TAG_Long(125)]))
    string_test(NbtTypes.TAG_Long_Array([NbtTypes.TAG_Long(125), NbtTypes.TAG_Long(123)]))
    string_test(NbtTypes.TAG_Long_Array([]))
    string_test(NbtTypes.TAG_Long_Array([NbtTypes.TAG_Long(1), NbtTypes.TAG_Long(0)]), "[L;   1l , 0l ]")
    string_test(NbtExceptions.SnbtParseError, "[L; 0l, 1]")
    string_test(NbtExceptions.SnbtParseError, "[L; 0l, 1l")
    string_test(NbtExceptions.SnbtParseError, "[L;")

    # compound test
    string_test(NbtTypes.TAG_Compound({}))
    string_test(NbtTypes.TAG_Compound({"": NbtTypes.TAG_String("hi")}))
    string_test(NbtTypes.TAG_Compound({"wow": NbtTypes.TAG_String("hi")}), "{wow: \"hi\"}")
    string_test(NbtTypes.TAG_Compound({"wow": NbtTypes.TAG_String("hi")}), "{\"wow\": \"hi\"}")
    string_test(NbtTypes.TAG_Compound({"wow": NbtTypes.TAG_Int(42), "truly_incredible": NbtTypes.TAG_Long(444222)}))
    string_test(NbtExceptions.SnbtParseError, "{")
    string_test(NbtExceptions.SnbtParseError, "{\"")
    string_test(NbtExceptions.SnbtParseError, "{\"wow\"")
    string_test(NbtExceptions.SnbtParseError, "{\"wow\":")
    string_test(NbtExceptions.SnbtParseError, "{\"wow\": \"")
    string_test(NbtExceptions.SnbtParseError, "{\"wow\": \"hi\"")
    string_test(NbtTypes.TAG_Compound({
        "": NbtTypes.TAG_Byte(0),
        "test1": NbtTypes.TAG_Short(32),
        "test 2": NbtTypes.TAG_Int(9999),
        "test 3": NbtTypes.TAG_Long(9999999990),
        "test 4": NbtTypes.TAG_Compound({
            "": NbtTypes.TAG_Byte(0),
            "test1": NbtTypes.TAG_Short(32),
            "test 2": NbtTypes.TAG_Int(9999),
            "test 3": NbtTypes.TAG_Long(9999999990),
        })
    }))

    # miscellaneous tests
    string_test(NbtExceptions.SnbtParseError, "please error")
    string_test(NbtExceptions.SnbtParseError, "pleaseerror")

def main() -> None:
    PROGRAMS = {
        "read_file": main_read_file,
        "string_demo": main_string_demo,
    }
    UserInput.input_single(PROGRAMS, "program", show_options=True, close_enough=True)()

if __name__ == "__main__":
    main()
