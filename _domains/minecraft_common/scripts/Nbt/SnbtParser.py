from typing import Callable, cast

import _domains.minecraft_common.scripts.Nbt.NbtExceptions as NbtExceptions
import _domains.minecraft_common.scripts.Nbt.NbtTypes as NbtTypes


class Reader():

    def __init__(self, data:str) -> None:
        self.data = data
        self.position = 0
        self.stack:list[int] = []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} pos {self.position}/{len(self.data)}, stacklen {self.stack}>"

    def read(self, amount:int=1) -> str:
        output = self.data[self.position:self.position+amount]
        self.position += amount
        return output

    def back(self, amount:int=1) -> None:
        self.position -= amount

    def add(self) -> "Reader":
        self.stack.append(self.position)
        return self

    def pop(self) -> "Reader":
        self.position = self.stack.pop()
        return self

    def remove_last(self) -> "Reader":
        self.stack.pop()
        return self

    def is_at_end(self) -> bool:
        return self.position == len(self.data)

def parse_compound(reader:Reader) -> NbtTypes.TAG_Compound:
    parse_whitespace(reader)
    if reader.read() != "{":
        raise NbtExceptions.SnbtParseError("Expected \"{\"", reader)
    if reader.read() == "}":
        return NbtTypes.TAG_Compound({})
    else:
        reader.back()
    output:dict[str,NbtTypes.TAG] = {}
    while True:
        parse_whitespace(reader)
        key = parse_string(reader, allow_unquoted_strings=True)
        parse_whitespace(reader)
        if reader.read() != ":":
            raise NbtExceptions.SnbtParseError("Expected \":\"", reader)
        parse_whitespace(reader)
        value = parse_thing(reader)
        output[key] = value
        parse_whitespace(reader)
        match reader.read():
            case ",":
                continue # next key-value pair
            case "}":
                break
            case "":
                raise NbtExceptions.SnbtParseError("Compound did not end before end", reader)
            case _:
                raise NbtExceptions.SnbtParseError("Expected \",\" or \"}\"", reader)
    return NbtTypes.TAG_Compound(output)

def parse_list(reader:Reader) -> NbtTypes.TAG_List:
    parse_whitespace(reader)
    if reader.read() != "[":
        raise NbtExceptions.SnbtParseError("Expected \"[\"", reader)
    if reader.read() == "]":
        return NbtTypes.TAG_List([])
    else:
        reader.back()
    output:list[NbtTypes.TAG] = []
    first_type = None
    index = -1
    while True:
        index += 1
        parse_whitespace(reader)
        item = parse_thing(reader)
        output.append(item)
        if first_type is None:
            first_type = type(item)
        else:
            if not isinstance(item, first_type):
                raise NbtExceptions.SnbtParseError(f"List type {index} type \"{item.__class__.__name__}\" does not match first item type \"{first_type.__name__}\"", reader)
        parse_whitespace(reader)
        match reader.read():
            case ",":
                continue # next item
            case "]":
                break
            case "":
                raise NbtExceptions.SnbtParseError("List did not end before end", reader)
            case _:
                raise NbtExceptions.SnbtParseError("Expected \",\" or \"]\"", reader)
    return NbtTypes.TAG_List(output)

def parse_byte_array(reader:Reader) -> NbtTypes.TAG_Byte_Array:
    parse_whitespace(reader)
    if reader.read() != "[":
        raise NbtExceptions.SnbtParseError("Expected \"[\"", reader)
    parse_whitespace(reader)
    if reader.read(2) != "B;":
        raise NbtExceptions.SnbtParseError("Expected \"B;\"", reader)
    if reader.read() == "]":
        return NbtTypes.TAG_Byte_Array([])
    else:
        reader.back()
    output:list[NbtTypes.TAG_Byte] = []
    while True:
        parse_whitespace(reader)
        item = parse_byte(reader)
        output.append(item)
        parse_whitespace(reader)
        match reader.read():
            case ",":
                continue # next item
            case "]":
                break
            case "":
                raise NbtExceptions.SnbtParseError("Byte array did not end before end", reader)
            case _:
                raise NbtExceptions.SnbtParseError("Expected \",\" or \"]\"", reader)
    return NbtTypes.TAG_Byte_Array(output)

def parse_int_array(reader:Reader) -> NbtTypes.TAG_Int_Array:
    parse_whitespace(reader)
    if reader.read() != "[":
        raise NbtExceptions.SnbtParseError("Expected \"[\"", reader)
    parse_whitespace(reader)
    if reader.read(2) != "I;":
        raise NbtExceptions.SnbtParseError("Expected \"I;\"", reader)
    if reader.read() == "]":
        return NbtTypes.TAG_Int_Array([])
    else:
        reader.back()
    output:list[NbtTypes.TAG_Int] = []
    while True:
        parse_whitespace(reader)
        item = parse_int(reader)
        output.append(item)
        parse_whitespace(reader)
        match reader.read():
            case ",":
                continue # next item
            case "]":
                break
            case "":
                raise NbtExceptions.SnbtParseError("Int array did not end before end", reader)
            case _:
                raise NbtExceptions.SnbtParseError("Expected \",\" or \"]\"", reader)
    return NbtTypes.TAG_Int_Array(output)

def parse_long_array(reader:Reader) -> NbtTypes.TAG_Long_Array:
    parse_whitespace(reader)
    if reader.read() != "[":
        raise NbtExceptions.SnbtParseError("Expected \"[\"", reader)
    parse_whitespace(reader)
    if reader.read(2) != "L;":
        raise NbtExceptions.SnbtParseError("Expected \"L;\"", reader)
    if reader.read() == "]":
        return NbtTypes.TAG_Long_Array([])
    else:
        reader.back()
    output:list[NbtTypes.TAG_Long] = []
    while True:
        parse_whitespace(reader)
        item = parse_long(reader)
        output.append(item)
        parse_whitespace(reader)
        match reader.read():
            case ",":
                continue # next item
            case "]":
                break
            case "":
                raise NbtExceptions.SnbtParseError("Long array did not end before end", reader)
            case _:
                raise NbtExceptions.SnbtParseError("Expected \",\" or \"]\"", reader)
    return NbtTypes.TAG_Long_Array(output)

def parse_byte(reader:Reader) -> NbtTypes.TAG_Byte:
    parse_whitespace(reader)
    if reader.read(4) == "true":
        return NbtTypes.TAG_Byte(1)
    else:
        reader.back(4)
    if reader.read(5) == "false":
        return NbtTypes.TAG_Byte(0)
    else:
        reader.back(5)
    if reader.read() == "-":
        is_negative = True
    else:
        is_negative = False
        reader.back()
    characters:list[str] = []
    while True:
        character = reader.read()
        if character.isalpha():
            if len(characters) == 0:
                raise NbtExceptions.SnbtParseError("Expected digit", reader)
            if character.lower() == "b":
                break
            else:
                raise NbtExceptions.SnbtParseError("Expected \"b\" or \"B\"", reader)
        elif character.isdigit():
            characters.append(character)
        elif character == ".":
            raise NbtExceptions.SnbtParseError("Decimal points are invalid in bytes", reader)
        else:
            raise NbtExceptions.SnbtParseError("Expected digit, \"b\", or \"B\"", reader)
    output = int("".join(characters))
    if is_negative: output = -output
    if output > 127:
        raise NbtExceptions.SnbtParseError("Byte value is greater than 127", reader)
    elif output < -128:
        raise NbtExceptions.SnbtParseError("Byte value is less than -128", reader)
    return NbtTypes.TAG_Byte(output)

def parse_short(reader:Reader) -> NbtTypes.TAG_Short:
    parse_whitespace(reader)
    if reader.read() == "-":
        is_negative = True
    else:
        is_negative = False
        reader.back()
    characters:list[str] = []
    while True:
        character = reader.read()
        if character.isalpha():
            if len(characters) == 0:
                raise NbtExceptions.SnbtParseError("Expected digit", reader)
            if character.lower() == "s":
                break
            else:
                raise NbtExceptions.SnbtParseError("Expected \"s\" or \"S\"", reader)
        elif character.isdigit():
            characters.append(character)
        elif character == ".":
            raise NbtExceptions.SnbtParseError("Decimal points are invalid in shorts", reader)
        else:
            raise NbtExceptions.SnbtParseError("Expected digit, \"s\", or \"S\"", reader)
    output = int("".join(characters))
    if is_negative: output = -output
    if output > 32767:
        raise NbtExceptions.SnbtParseError("Short value is greater than 32767", reader)
    elif output < -32768:
        raise NbtExceptions.SnbtParseError("Short value is less than -32768", reader)
    return NbtTypes.TAG_Short(output)

def parse_int(reader:Reader) -> NbtTypes.TAG_Int:
    parse_whitespace(reader)
    if reader.read() == "-":
        is_negative = True
    else:
        is_negative = False
        reader.back()
    characters:list[str] = []
    while True:
        character = reader.read()
        if character.isdecimal():
            characters.append(character)
        elif character == ".":
            raise NbtExceptions.SnbtParseError("Decimal points are invalid in ints", reader)
        else:
            reader.back()
            if len(characters) == 0:
                raise NbtExceptions.SnbtParseError("Expected digit", reader)
            break # ints don't have any ending character, so any non-decimal ending character could be a correct next character.
    output = int("".join(characters))
    if is_negative: output = -output
    if output > 2147483647:
        raise NbtExceptions.SnbtParseError("Int value is greater than 2147483647", reader)
    elif output < -2147483648:
        raise NbtExceptions.SnbtParseError("Int value is less than -2147483648", reader)
    return NbtTypes.TAG_Int(output)

def parse_long(reader:Reader) -> NbtTypes.TAG_Long:
    parse_whitespace(reader)
    if reader.read() == "-":
        is_negative = True
    else:
        is_negative = False
        reader.back()
    characters:list[str] = []
    while True:
        character = reader.read()
        if character.isdecimal():
            characters.append(character)
        elif character == ".":
            raise NbtExceptions.SnbtParseError("Decimal points are invalid in longs", reader)
        else:
            if character.lower() == "l":
                if len(characters) == 0:
                    raise NbtExceptions.SnbtParseError("Expected digit", reader)
                break
            else:
                raise NbtExceptions.SnbtParseError("Expected \"l\" or \"L\"", reader)
    output = int("".join(characters))
    if is_negative: output = -output
    if output > 9223372036854775807:
        raise NbtExceptions.SnbtParseError("Long value is greater than 9223372036854775807", reader)
    elif output < -9223372036854775808:
        raise NbtExceptions.SnbtParseError("Long value is less than -9223372036854775808", reader)
    return NbtTypes.TAG_Long(output)

def parse_float(reader:Reader) -> NbtTypes.TAG_Float:
    parse_whitespace(reader)
    if reader.read() == "-":
        is_negative = True
    else:
        is_negative = False
        reader.back()
    characters_pre_decimal:list[str] = []
    characters_post_decimal:list[str] = []
    while True:
        character = reader.read()
        if character.isdecimal():
            characters_pre_decimal.append(character)
        elif character == ".":
            if len(characters_pre_decimal) == 0:
                raise NbtExceptions.SnbtParseError("Expected digits before decimal", reader)
            break
        else:
            raise NbtExceptions.SnbtParseError("Expected digit", reader)
    while True:
        character = reader.read()
        if character.isdecimal():
            characters_post_decimal.append(character)
        elif character == ".":
            raise NbtExceptions.SnbtParseError("Expected digit, \"f\", or \"F\", not additional decimal point", reader)
        elif character.isalpha():
            if character.lower() == "f":
                if len(characters_post_decimal) == 0:
                    raise NbtExceptions.SnbtParseError("Expected digits after decimal", reader)
                break
            else:
                raise NbtExceptions.SnbtParseError("Expected digit", reader)
        else:
            raise NbtExceptions.SnbtParseError("Expected digit", reader)
    output = float("".join(characters_pre_decimal) + "." + "".join(characters_post_decimal))
    if is_negative: output = -output
    return NbtTypes.TAG_Float(output)

def parse_double(reader:Reader) -> NbtTypes.TAG_Double:
    parse_whitespace(reader)
    if reader.read() == "-":
        is_negative = True
    else:
        is_negative = False
        reader.back()
    characters_pre_decimal:list[str] = []
    characters_post_decimal:list[str] = []
    while True:
        character = reader.read()
        if character.isdecimal():
            characters_pre_decimal.append(character)
        elif character == ".":
            if len(characters_pre_decimal) == 0:
                raise NbtExceptions.SnbtParseError("Expected digits before decimal", reader)
            break
        else:
            raise NbtExceptions.SnbtParseError("Expected digit", reader)
    while True:
        character = reader.read()
        if character.isdecimal():
            characters_post_decimal.append(character)
        elif character == ".":
            raise NbtExceptions.SnbtParseError("Expected digit, \"d\", or \"D\", not additional decimal point", reader)
        else:
            if len(characters_post_decimal) == 0:
                raise NbtExceptions.SnbtParseError("Expected digits after decimal", reader)
            if character.lower() == "d":
                break
            else:
                reader.back()
                break
    output = float("".join(characters_pre_decimal) + "." + "".join(characters_post_decimal))
    if is_negative: output = -output
    return NbtTypes.TAG_Double(output)

def parse_string(reader:Reader, allow_unquoted_strings:bool=False) -> NbtTypes.TAG_String:
    parse_whitespace(reader)
    character = reader.read()
    if character in "\"'":
        is_quoted = True
        quote_type = character
    else:
        if allow_unquoted_strings:
            reader.back()
            is_quoted = False
            quote_type = None
        else:
            raise NbtExceptions.SnbtParseError("Unquoted strings are not allowed", reader)
    is_escaped = False
    output = ""
    while True:
        character = reader.read()
        if len(character) == 0:
            raise NbtExceptions.SnbtParseError("String did not end before end", reader)
        if is_quoted:
            quote_type = cast(str, quote_type)
            if is_escaped:
                if character == "\\": output += "\\"
                elif character == quote_type: output += quote_type
                else: raise NbtExceptions.SnbtParseError(f"Expected escaped character to be \"\\\" or \"{quote_type}\"", reader)
                is_escaped = False
            else:
                if character == "\\": is_escaped = True; continue
                elif character == quote_type: break
                else: output += character
        else:
            if character.isalnum() or character in "_-.+":
                output += character
            else:
                if len(output) == 0:
                    raise NbtExceptions.SnbtParseError("Expected character", reader)
                reader.back()
                break
    return NbtTypes.TAG_String(output)

def parse_whitespace(reader:Reader) -> None:
    while reader.read() in [" ", "\t", "\n"]:
        pass
    reader.back() # since the last character it read is not whitespace

def parse_thing(reader:Reader) -> NbtTypes.TAG:
    functions:list[Callable[[Reader],NbtTypes.TAG]] = [parse_compound, parse_byte_array, parse_int_array, parse_long_array, parse_list, parse_byte, parse_short, parse_long, parse_float, parse_double, parse_int, parse_string]
    exceptions:list[NbtExceptions.SnbtParseError] = []
    for function in functions:
        try:
            thing = function(reader.add())
        except NbtExceptions.SnbtParseError as e:
            # traceback.print_exception(e)
            exceptions.append(e)
            reader.pop()
            continue
        else:
            reader.remove_last()
            return thing
    else:
        raise NbtExceptions.SnbtParseError("Unknown data", reader, exceptions)

def parse(data:str) -> NbtTypes.TAG:
    reader = Reader(data)
    output = parse_thing(reader)
    if not reader.is_at_end():
        raise NbtExceptions.SnbtParseError("Trailing data", reader)
    return output
