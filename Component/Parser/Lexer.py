from typing import Final, Sequence

from Component.Field.Errors import Errors
from Component.Parser.Reader import Reader

WHITESPACE_NO_SEPARATOR:Final = " \t\r\f\v"
BREAKING_NAME_CHARS:Final = set(" \t\r\n\f\v!@#$%()=+[]{}\\,/") # subset INVALID_NAME_CHARS to make error messages better for invalid identifiers
INVALID_NAME_CHARS:Final  = set(" \t\r\n\f\v!@#$%^&*()=+[]{}\\|;'\",<>/?`") # most puncuation characters except "._:"
INVALID_NAME_STRINGED_CHARS:Final = set("\t\r\n\f\v")

class Token():
    """
    A itty bitty piece of a .cmp file.

    :param content: The content that this Token contains.
    :param start_index: The start (0-based) index of the start of the Token in its text file.
    :param end_index: The end (0-based) index of the end of the Token in its text file.
    """

    __slots__ = (
        "content",
        "end_index",
        "error",
        "start_index",
    )

    def __init__(self, content:str, start_index:int, end_index:int, error:Errors=Errors.fine) -> None:
        self.content = content
        self.start_index = start_index
        self.end_index = end_index
        self.error = error

class OpenObjectToken(Token): __slots__ = () # {
class CloseObjectToken(Token): __slots__ = () # }
class OpenListToken(Token): __slots__ = () # [
class CloseListToken(Token): __slots__ = () # ]
class OpenParenToken(Token): __slots__ = () # (
class CloseParenToken(Token): __slots__ = () # )
class SeparatorToken(Token): __slots__ = () # abstract
class CommaToken(SeparatorToken): __slots__ = () # ,
class NewlineToken(SeparatorToken): __slots__ = () # \n
class AbstractStringToken(Token):
    """
    :param string_content: The content the string represents.
    :param content: The characters used to create this string, including any quotes.
    """

    __slots__ = (
        "string_content",
    )

    def __init__(self, string_content:str, content: str, start_index: int, end_index: int, error: Errors = Errors.fine) -> None:
        super().__init__(content, start_index, end_index, error)
        self.string_content = string_content

class StringToken(AbstractStringToken): __slots__ = () # "string"
class IdentifierToken(AbstractStringToken): __slots__ = () # 'identifier' or identifier
class NumberToken(Token):
    """
    :param number: The integer or float of the number.
    :param content: The characters used to create the number.
    """

    __slots__ = (
        "number",
    )

    def __init__(self, number:int|float, content: str, start_index: int, end_index: int, error: Errors = Errors.fine) -> None:
        super().__init__(content, start_index, end_index, error)
        self.number = number

class BooleanToken(Token):
    """
    :param value: The boolean value.
    :param content: The string version of the value.
    """

    __slots__ = (
        "value",
    )

    def __init__(self, value:bool, content: str, start_index: int, end_index: int, error: Errors = Errors.fine) -> None:
        super().__init__(content, start_index, end_index, error)
        self.value = value

class NullToken(Token): __slots__ = () # null
class InheritToken(Token): __slots__ = () # inherit
class AbstractToken(Token): __slots__ = () # abstract (not actually abstract, just the literal text "abstract")
class SettingsToken(Token): __slots__ = () # settings
class PlusToken(Token): __slots__ = () # +
class BangToken(Token): __slots__ = () # !
class AtToken(Token): __slots__ = () # @
class PoundToken(Token): __slots__ = () # #
class DollarToken(Token): __slots__ = () # $
class PercentToken(Token): __slots__ = () # %
class EqualToken(Token): __slots__ = () # =
class SlashToken(Token): __slots__ = () # /

def parse_line_comment(reader:Reader, /) -> Errors:
    """
    Parses a comment beginning with "//".

    :param reader: A Reader whose next two characters are "//".
    """
    assert reader.next_is("//", False, False)
    error = Errors.fine
    reader.move_while(lambda char: char not in "\n")
    return error

def parse_multiline_comment(reader:Reader, /) -> Errors:
    """
    Parses a comment beginning with "/*".

    :param reader: A Reader whose next to characters are "/*".
    """
    with reader.focus():
        error = Errors.fine
        while True:
            reader.move_while(lambda char: char not in "*")
            if reader.next_is("*/", True, False):
                break
            else:
                reader.move(1) # move past this asterisk
            if reader.at_last():
                reader.exception(RuntimeError("Unexpected end of comment"))
                error = error.narrow(Errors.create_field)
                break
    return error

def parse_whitespace(reader:Reader) -> Errors:
    """
    Consumes all characters in `WHITESPACE_NO_SEPARATOR`.
    """
    error = Errors.fine
    total_whitespace:int = 0
    while True:
        total_whitespace += reader.move_while(lambda char: char in WHITESPACE_NO_SEPARATOR)
        if reader.next_is("//", True, True):
            error = error.narrow(parse_line_comment(reader))
        elif reader.next_is("/*", True, True):
            error = error.narrow(parse_multiline_comment(reader))
        elif reader.next_is("\\\n", True, False):
            pass # \newline can split anything on a newline, even stuff that normally only fits on one line.
        else:
            break
    return error

def parse_unicode_escape(reader:Reader) -> tuple[int, Errors]:
    """
    :param reader: A reader whose next character is the first hexadecimal digit.
    :returns: The integer encoded by the four hexadecimal digits and Errors.
    """
    error = Errors.fine
    output:list[str] = [] # digits
    for i in range(4):
        char = reader.read(1)
        if char.isdigit() or char.lower() in {"abcdef"}: # case-insensitive
            output.append(char)
        else: # early exit
            reader.move(-1)
            reader.exception(RuntimeError("Four hexadecimal digits are required."))
            error = error.narrow(Errors.create_field)
            break
    return int("".join(output), 16), error

def pow(a:int, b:int) -> int: # ???? why isn't this default behavior? Why is it Any???
    return a ** b

def parse_string(reader:Reader, quote_style:str) -> tuple[str,str,int,int,Errors]:
    """
    :param reader: A Reader whose next character is the quote.
    :param quote_style: The type of quotes that this string is surrounded by.
    :returns: The encoded string, the actual contents of the string (including
    quotes), the start index, the end index, and the Errors.
    """
    with reader.focus():
        error = Errors.fine
        start_index = reader.index
        assert reader.next_is(quote_style, False, False) # assumption
        string:list[str] = []
        escaped:bool = False
        while True:
            with reader.highlight():
                char = reader.read(1)
                if char == "": # meaning end of file
                    raise RuntimeError("Unexpected end of file")
                if escaped:
                    if char == "t":   string.append("\t")
                    elif char == "n": string.append("\n")
                    elif char == "r": string.append("\r")
                    elif char == "\\": string.append("\\")
                    elif char == "\"": string.append("\"")
                    elif char == "'": string.append("'") # both styles available
                    elif char == "u":
                        code, new_error = parse_unicode_escape(reader)
                        error = error.narrow(new_error)
                        try:
                            string.append(code.to_bytes(2).decode("utf-8"))
                        except UnicodeDecodeError as e:
                            reader.exception(e)
                            error = error.narrow(Errors.create_field)
                    else:
                        reader.exception(RuntimeError(f"Unknown backslash code \"\\{char}"))
                        error = error.narrow(Errors.create_field)
                        pass
                    escaped = False
                else:
                    if char == "\\": escaped = True
                    elif char == quote_style: break
                    elif char == "\n":
                        raise RuntimeError("String did not terminate") # catastrophic error, no more parsing allowed.
                    else:             string.append(char)
        end_index = reader.index
    return "".join(string), reader.source[start_index:end_index], start_index, end_index, error

def parse_number(reader:Reader) -> tuple[int|float, str, int, int, Errors]:
    """
    :param reader: A Reader whose next character is the first digit or negative sign.
    :returns: The number, the string used to create the number, the start index, the end index, and the Errors.
    """
    start_index:int = reader.index
    error = Errors.fine
    is_negative = reader.next_is("-", True, False)
    with reader.highlight():
        integer_part = reader.read_while(lambda char: char.isdigit())
        if len(integer_part) == 0:
            reader.exception(RuntimeError("No digits in the exponent despite an exponent being present."))
            error = error.narrow(Errors.create_field)
            integer_part = "0"

    fraction_part:str|None = None
    if reader.next_is(".", True, False): # fraction
        with reader.highlight():
            fraction_part = reader.read_while(lambda char: char.isdigit())
            if len(fraction_part) == 0:
                reader.exception(RuntimeError("No digits after the decimal"))
                error = error.narrow(Errors.create_field)
                fraction_part = "0"

    exponent_negative:bool = False
    exponent_part:str|None = None
    if reader.next_in("eE", True, False): # exponent
        with reader.highlight():
            if reader.next_is("-", True, False): exponent_negative = True
            elif reader.next_is("+", True, False): exponent_negative = False
            exponent_part = reader.read_while(lambda char: char.isdigit())
            if len(exponent_part) == 0:
                reader.exception(RuntimeError("No digits in the exponent despite an exponent being present."))
                error = error.narrow(Errors.create_field)
                exponent_part = "0"

    end_index = reader.index
    return (-1 if is_negative else 1) * (int(integer_part) + (float("." + fraction_part) if fraction_part is not None else 0)) * \
           (pow(10, (-1 if exponent_negative else 1) * int(exponent_part)) if exponent_part is not None else 1), \
           reader.source[start_index:end_index], start_index, end_index, error

def validate_identifier(reader:Reader, name:str, stringed:bool) -> Errors:
    error = Errors.fine
    if len(name) == 0:
        reader.exception(RuntimeError("Identifier name cannot be empty"))
        error = error.narrow(Errors.create_field)
    if not stringed and any(char in INVALID_NAME_CHARS for char in name):
        message = ". Consider placing it in single quotes" if not any(char in INVALID_NAME_STRINGED_CHARS for char in name) else ""
        reader.exception(RuntimeError(f"Identifier name {name} is invalid because it contains chars in {INVALID_NAME_CHARS} and whitespace characters{message}"))
        error = error.narrow(Errors.create_field)
    if stringed and any(char in INVALID_NAME_STRINGED_CHARS for char in name):
        reader.exception(RuntimeError(f"Identifier name {name} is invalid because it contains whitespace characters"))
        error = error.narrow(Errors.create_field)
    return error

def parse_identifier(reader:Reader, /) -> tuple[str, int, int, Errors]:
    """
    Parses an identifier without quotes.
    """
    error = Errors.fine
    start_index = reader.index
    with reader.highlight():
        output = reader.read_while(lambda char: char not in BREAKING_NAME_CHARS)
        end_index = reader.index
        if len(output) == 0:
            # can only happen if something goes very wrong.
            # if we do nothing, it may get stuck in an endless loop.
            raise RuntimeError("Identifier is invalid")
        error = error.narrow(validate_identifier(reader, output, False))
    return output, start_index, end_index, error

def lex_token(reader:Reader) -> Token:
    """
    :returns: The Token and Errors that may be different from the Token's Errors.
    """
    if reader.next_is("{",  True, False): return OpenObjectToken    ("{",  reader.index - 1, reader.index)
    if reader.next_is("}",  True, False): return CloseObjectToken   ("}",  reader.index - 1, reader.index)
    if reader.next_is("[",  True, False): return OpenListToken      ("[",  reader.index - 1, reader.index)
    if reader.next_is("]",  True, False): return CloseListToken     ("]",  reader.index - 1, reader.index)
    if reader.next_is("(",  True, False): return OpenParenToken     ("[",  reader.index - 1, reader.index)
    if reader.next_is(")",  True, False): return CloseParenToken    ("]",  reader.index - 1, reader.index)
    if reader.next_is(",",  True, False): return CommaToken         (",",  reader.index - 1, reader.index)
    if reader.next_is("\n", True, False): return NewlineToken       ("\n", reader.index - 1, reader.index)
    if reader.next_is("+",  True, False): return PlusToken          ("+",  reader.index - 1, reader.index)
    if reader.next_is("!",  True, False): return BangToken          ("!",  reader.index - 1, reader.index)
    if reader.next_is("@",  True, False): return AtToken            ("!",  reader.index - 1, reader.index)
    if reader.next_is("#",  True, False): return PoundToken         ("!",  reader.index - 1, reader.index)
    if reader.next_is("$",  True, False): return DollarToken        ("!",  reader.index - 1, reader.index)
    if reader.next_is("%",  True, False): return PercentToken       ("!",  reader.index - 1, reader.index)
    if reader.next_is("=",  True, False): return EqualToken         ("!",  reader.index - 1, reader.index)
    if reader.next_is("/",  True, False): return SlashToken         ("!",  reader.index - 1, reader.index)
    if reader.next_is("\"", True, True):
        string_content, content, start_index, end_index, error = parse_string(reader, "\"")
        return StringToken(string_content, content, start_index, end_index, error)
    if reader.next_is("'", True, True): # identifier
        string_content, content, start_index, end_index, error = parse_string(reader, "'")
        error = error.narrow(validate_identifier(reader, string_content, True))
        return IdentifierToken(string_content, content, start_index, end_index, error)
    if reader.next_in("-0123456789", True, True):
        number, content, start_index, end_index, error = parse_number(reader)
        return NumberToken(number, content, start_index, end_index, error)
    content, start_index, end_index, error = parse_identifier(reader)
    if content == "true": return BooleanToken(True, content, start_index, end_index, error)
    if content == "false": return BooleanToken(False, content, start_index, end_index, error)
    if content == "null": return NullToken(content, start_index, end_index, error)
    if content == "inherit": return InheritToken(content, start_index, end_index)
    if content == "abstract": return AbstractToken(content, start_index, end_index, error)
    if content == "settings": return SettingsToken(content, start_index, end_index, error)
    return IdentifierToken(content, content, start_index, end_index)

def lex(reader:Reader) -> tuple[Sequence[Token], Errors]:
    """
    :returns: A sequence of Tokens and an Errors.
    :raises: An Exception if there is a catastrophic error while lexing.
    """
    error = Errors.fine
    output:list[Token] = []
    with reader.highlight():
        error = error.narrow(parse_whitespace(reader))
    while not reader.at_last():
        token = lex_token(reader)
        output.append(token)
        with reader.highlight():
            error = error.narrow(parse_whitespace(reader))
    return output, error
