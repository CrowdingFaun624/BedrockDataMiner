import json
from itertools import count
from pathlib import Path
from string import whitespace
from typing import Callable, Container, Final, Literal, Sequence

import Domain.Domain as Domain
from Component.Field.ComponentField import ComponentField
from Component.Field.ComponentTypeField import ComponentTypeField
from Component.Field.ConcatenationField import ConcatenationField
from Component.Field.CTypeField import CTypeField
from Component.Field.DictField import DictField
from Component.Field.DomainField import DomainField
from Component.Field.Errors import Errors
from Component.Field.FieldFactory import FieldFactory
from Component.Field.GroupField import GroupField
from Component.Field.ListField import ListField
from Component.Field.PrimitiveField import PrimitiveField
from Component.Field.ReferenceField import ReferenceField
from Component.Field.ScriptField import ScriptField
from Component.Field.TypeField import TypeField
from Component.Field.Variable import Variable
from Component.Field.VariableReferenceField import VariableReferenceField
from Component.Group import Aliases, Group, GroupSettings
from Component.Reader import Reader
from Component.Scope import Scope

# wow look at that it's descriptive instead of prescriptive
# fun fact: I rewrote the entire Component system because ConcatenationExpression didn't work.

SEPARATOR_CHARS:Final = ",\n"
WHITESPACE_NO_SEPARATOR:Final = " \t\r\f\v"

INVALID_NAME_CHARS:Final  = set(" \t\r\n\f\v!@#$%^&*()=+[]{}\\|;'\",<>/?`") # most puncuation characters except "._:"
BREAKING_NAME_CHARS:Final = set(" \t\r\n\f\v!@#$%()=+[]{}\\,/") # subset INVALID_NAME_CHARS to make error messages better for invalid identifiers
INVALID_NAME_CHARS_DISPLAY:Final =    list("!@#$%^&*()=[]{}\\|;'\",<>/?`")
INVALID_NAME_STRINGED_CHARS:Final = set("\t\r\n\f\v")

INVALID_NAME_CHARS_FILE:Final = set("<>:\"\\/|?*")
INVALID_NAMES_FILE:Final[set[str]] = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(0, 10)} | {f"LPT{i}" for i in range(0, 10)}

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
    if not stringed and len(name) >= 1 and name[0].isdigit() or len(name) >= 2 and name[0] == "-" and name[1].isdigit():
        reader.exception(RuntimeError(f"Identifier name {name} is invalid because it looks like a number"))
        error = error.narrow(Errors.create_field)
    return error

def parse_line_comment(reader:Reader, /) -> Errors:
    error = Errors.fine
    if not reader.next_is("//", True, False):
        reader.exception(RuntimeError("Expected \"//\""))
        error = error.narrow(Errors.create_field)
    reader.move_while(lambda char: char not in "\n")
    return error

def parse_multiline_comment(reader:Reader, /) -> Errors:
    error = Errors.fine
    if not reader.next_is("/*", True, False):
        reader.exception(RuntimeError("Expected \"/*\""))
        error = error.narrow(Errors.create_field)
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

def parse_whitespace(reader:Reader, /, at_least:int=0, chars:Container[str]=whitespace, allow_comments:bool=True) -> Errors:
    '''
    Consumes all characters in `string.whitespace`.
    '''
    error = Errors.fine
    total_whitespace:int = 0
    while True:
        total_whitespace += reader.move_while(lambda char: char in chars)
        if allow_comments and reader.next_is("//", True, True):
            error = error.narrow(parse_line_comment(reader))
        elif allow_comments and reader.next_is("/*", True, True):
            error = error.narrow(parse_multiline_comment(reader))
        elif reader.next_is("\\\n", True, False):
            pass # \newline can split anything on a newline, even stuff that normally only fits on one line.
        else:
            break
    if total_whitespace < at_least:
        reader.exception(RuntimeError(f"Expected at least {at_least} whitespace"))
        error = error.narrow(Errors.create_field)
    return error

def parse_separator(reader:Reader, /, allow_comments:bool=True) -> Errors:
    '''
    Consumes all whitespace before and after the separator.
    The separator may be a newline or a comma.
    '''
    error = Errors.fine
    between_chars:list[str] = []
    with reader.highlight():
        while True:
            between_chars.append(reader.read_while(lambda char: char in WHITESPACE_NO_SEPARATOR))
            if allow_comments and reader.next_is("//", True, True):
                error = error.narrow(parse_line_comment(reader))
            elif allow_comments and reader.next_is("/*", True, True):
                error = error.narrow(parse_multiline_comment(reader))
            elif reader.next_in(("\n", ","), True, True):
                between_chars.append(reader.read(1))
                continue
            else:
                break
    separator_chars = "".join(between_chars)
    if (comma_count := separator_chars.count(",")) > 0:
        if comma_count > 1:
            reader.exception(RuntimeError("Cannot have two commas as separators"))
            error = error.narrow(Errors.create_field)
    elif separator_chars.count("\n") > 0:
        pass
    else:
        reader.exception(RuntimeError("Expected separator"))
        error = error.narrow(Errors.create_field)
    return error

def parse_string(reader:Reader, /, quote_style:str) -> tuple[str, Errors]:
    error = Errors.fine
    if not reader.next_is(quote_style, True, False):
        reader.exception(RuntimeError(f"This string must begin with {quote_style}"))
        error = error.narrow(Errors.returning)
        if reader.next_in(("\"", "'"), True, True):
            quote_style = reader.read(1) # match up with the same beginning quote.
        else:
            return parse_identifier(reader)
    string:list[str] = []
    escaped:bool = False
    while True:
        char = reader.read(1)
        if char == "": # meaning end of file
            reader.exception(RuntimeError("Unexpected end of file"))
            error = error.narrow(Errors.create_field)
            break
        if escaped:
            if char == "t":   string.append("\t")
            elif char == "n": string.append("\n")
            elif char == "r": string.append("\r")
            elif char == "\\": string.append("\\")
            elif char == "\"": string.append("\"")
            else:
                reader.exception(RuntimeError(f"Unknown backslash code \"\\{char}"))
                error = error.narrow(Errors.create_field)
                pass
            escaped = False
        else:
            if char == "\\": escaped = True
            elif char == quote_style: break
            elif char == "\n":
                reader.exception(RuntimeError("String did not terminate"))
                error = error.narrow(Errors.create_field)
                break
            else:             string.append(char)
    return "".join(string), error

def parse_identifier(reader:Reader, /) -> tuple[str, Errors]:
    '''
    Parses an identifier, making sure it is valid.
    '''
    with reader.highlight():
        error = Errors.fine
        if reader.next_in(("\"", "'"), True, True): # double quote isn't allowed, but doing it for error messages
            output, new_error = parse_string(reader, "'")
            error = error.narrow(new_error)
            error = error.narrow(validate_identifier(reader, output, True))
        else:
            output = reader.read_while(lambda char: char not in BREAKING_NAME_CHARS)
            if len(output) == 0:
                # can only happen if something goes very wrong.
                # if we do nothing, it may get stuck in an endless loop.
                output = reader.read(1)
            error = error.narrow(validate_identifier(reader, output, False))
        return output, error

def parse_field_assignment(reader:Reader, /) -> tuple[str,FieldFactory,Errors]:
    with reader.focus():
        error = Errors.fine
        with reader.focus():
            field_name, new_error = parse_identifier(reader)
        error = error.narrow(new_error)
        error = error.narrow(parse_whitespace(reader))
        if not reader.next_is("=", False, False):
            reader.exception(RuntimeError("Expected \"=\""))
            error = Errors.create_field
        error = error.narrow(parse_whitespace(reader))
        field_value = parse_field(reader, False)
        return field_name, field_value, error

def parse_variable_assignment(reader:Reader, /) -> tuple[str,FieldFactory[Variable],Errors]:
    error = Errors.fine
    variable_fields:list[tuple[str,FieldFactory]] = []
    error = error.narrow(parse_whitespace(reader))
    with reader.highlight():
        if reader.next_is("(", True, True):
            variable_types = parse_ctype_field(reader, abstract=False)
            error = error.narrow(parse_whitespace(reader, 1))
            variable_fields.append(("types", variable_types))
        else:
            variable_types = None
    with reader.highlight():
        key, new_error = parse_identifier(reader)
        error = error.narrow(new_error)
    error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR))
    value = None
    with reader.highlight():
        if reader.next_is("=", True, False):
            error = error.narrow(parse_whitespace(reader))
            value = parse_field(reader, False)
            variable_fields.append(("value", value))
        else: value = None
    if variable_types is None and value is None:
        reader.exception(RuntimeError("Variable must have at least one of types or value"))
        error = error.narrow(Errors.create_field)
    return key, FieldFactory(reader, False, error, variable_fields, Variable, lambda factory, scope: Variable(factory, scope, error, variable_types, value)), error

def parse_aliases(reader:Reader, /) -> Aliases:
    '''
    Parses the aliases of settings, including the keyword "aliases".
    '''
    with reader.focus():
        error = Errors.fine
        domain_aliases:dict[str,FieldFactory[DomainField]] = {}
        group_aliases:dict[str,FieldFactory[GroupField]] = {}
        if not reader.next_is("aliases", True, False):
            reader.exception(RuntimeError("Expected \"aliases\""))
            error = error.narrow(Errors.create_field)
        error = error.narrow(parse_whitespace(reader, 1))
        if not reader.next_is("{", True, False):
            reader.exception(RuntimeError("Expected \"{\""))
            error = error.narrow(Errors.create_field)
        error = error.narrow(parse_whitespace(reader))
        while True:
            if reader.next_is("}", True, False): # there is a trailing comma
                break
            alias_name, alias_value, new_error = parse_field_assignment(reader)
            error = error.narrow(new_error)
            if issubclass(alias_value.field_type, DomainField):
                domain_aliases[alias_name] = alias_value
            elif issubclass(alias_value.field_type, GroupField):
                group_aliases[alias_name] = alias_value
            else:
                reader.exception(RuntimeError(f"{alias_value.field_type.__name__} cannot be an alias"))
                error.narrow(Errors.returning) # since it has no other effect
            error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR))
            if reader.next_is("}", True, False): # there is no trailing comma
                break
            elif reader.at_last():
                reader.exception(RuntimeError("Unexpected end of file"))
                error = error.narrow(Errors.create_field)
                break
            error = error.narrow(parse_separator(reader))
        return Aliases(domain_aliases, group_aliases, error)

def parse_settings(reader:Reader, /) -> GroupSettings:
    '''
    Parses the Group settings, including the keyword "settings".
    '''
    with reader.focus():
        error = Errors.fine
        if not reader.next_is("settings", True, False):
            reader.exception(RuntimeError("Expected \"settings\""))
            error = error.narrow(Errors.create_field)
        error = error.narrow(parse_whitespace(reader, 1))
        if not reader.read(1) == "{":
            reader.exception(RuntimeError("Expected \"{\""))
            error = error.narrow(Errors.create_field)
        error = error.narrow(parse_whitespace(reader))
        aliases:Aliases|None = None
        while True:
            if reader.next_is("}", True, False): # there is a trailing comma
                break
            if reader.next_is("aliases", True, True):
                aliases = parse_aliases(reader)
            else:
                reader.exception(RuntimeError(f"Expected settings key in { {"aliases"} }"))
                error = error.narrow(Errors.create_field)
                break
            error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR))
            if reader.next_is("}", True, False): # there is no trailing comma
                break
            elif reader.at_last():
                reader.exception(RuntimeError("Unexpected end of file"))
                error = error.narrow(Errors.create_field)
                break
            error = error.narrow(parse_separator(reader))
        if aliases is None:
            aliases = Aliases({}, {}, Errors.fine)
        return GroupSettings(aliases, error)

INVALID_NAME_CHARS_LIST:Final = sorted("".join(INVALID_NAME_CHARS).replace("'", ""))

def parse_reference_field(reader:Reader, /, abstract:bool) -> FieldFactory[ReferenceField]|FieldFactory[ScriptField]|FieldFactory[GroupField]|FieldFactory[DomainField]:
    error = Errors.fine
    is_script:bool = False
    is_inherit:bool = False
    is_built_in:bool = False
    with reader.highlight():
        while True: # modifiers
            minimum_whitespace:int = 0
            # we check for is_inherit here just in case there's a Domain/Group named "inherit"
            if not is_inherit and reader.next_is("inherit", True, False):
                is_inherit = True
                minimum_whitespace = 1
            elif reader.next_is("@", True, False):
                is_built_in = True # means nothing when not a Script reference
            elif reader.next_is("%", True, False):
                is_script = True
            else:
                break
            error = error.narrow(parse_whitespace(reader, at_least=minimum_whitespace, chars=WHITESPACE_NO_SEPARATOR, allow_comments=False))

    parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR, allow_comments=False)
    path_items:list[str] = []
    end_separator:Literal["!", "/"]|None = None
    domain:str|None = None
    last_item:str
    for index in count():
        with reader.highlight():
            item, new_error = parse_identifier(reader)
            error = error.narrow(new_error)
            last_item = item
            error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR, allow_comments=True))
            before_separator_read:int = reader.index
            separator = reader.read(1)
            if separator == "!":
                if index != 0:
                    reader.exception(RuntimeError("Domain must be declared at the start of the reference"))
                    error = Errors.returning
                domain = item
            elif separator == "/":
                path_items.append(item)
            else:
                reader.set(before_separator_read)
                break
            error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR, allow_comments=False))
            if reader.next_in(INVALID_NAME_CHARS_LIST, True, True):
                # if it ends in a separator, it's a GroupField or DomainField.
                end_separator = separator
                break

    if is_script: # ScriptField
        script_object_name = None if end_separator is not None else last_item
        if is_inherit:
            reader.exception(RuntimeError("ScriptField cannot be inherit; use \"@\" instead of \"inherit\""))
            error = error.narrow(Errors.returning)
        return FieldFactory(reader, abstract, error, (), ScriptField, lambda factory, scope: ScriptField(factory, scope, error, domain, None if len(path_items) == 0 else path_items, script_object_name, is_built_in))
    else:
        if end_separator == "!": # DomainField
            if is_inherit:
                reader.exception(RuntimeError("DomainField cannot be inherit; use \"@\" instead of \"inherit\""))
                error = error.narrow(Errors.returning)
            assert domain is not None
            return FieldFactory(reader, abstract, error, (), DomainField, lambda factory, scope: DomainField(factory, scope, error, domain))
        elif end_separator == "/": # GroupField
            if is_inherit:
                reader.exception(RuntimeError("GroupField cannot be inherit; use \"@\" instead of \"inherit\""))
                error = error.narrow(Errors.returning)
            return FieldFactory(reader, abstract, error, (), GroupField, lambda factory, scope: GroupField(factory, scope, error, domain, path_items))
        else: # ReferenceField
            fields: Sequence[tuple[str, FieldFactory]]
            if reader.next_is("{", True, True):
                fields, new_error = parse_component_fields(reader)
                error = error.narrow(new_error)
            else:
                fields = ()
            return FieldFactory(reader, abstract, error, fields, ReferenceField, lambda factory, scope: ReferenceField(factory, scope, error, domain, path_items, last_item, fields, not is_inherit))

def parse_type_field(reader:Reader, /, abstract:bool) -> FieldFactory[TypeField]:
    error = Errors.fine
    with reader.highlight():
        if not reader.next_is("#", True, False):
            reader.exception(RuntimeError("Expected \"#\""))
            error = error.narrow(Errors.create_field)
    error = error.narrow(parse_whitespace(reader))
    name, new_error = parse_identifier(reader)
    error = error.narrow(new_error)
    return FieldFactory(reader, abstract, error, (), TypeField, lambda factory, scope: TypeField(factory, scope, error, name))

def _get_dict_key_field(key_error:Errors, key_string:str) -> Callable[[FieldFactory, Scope], PrimitiveField]:
    return lambda factory, scope: PrimitiveField(factory, scope, key_error, key_string)

def parse_dict_field(reader:Reader, /, abstract:bool) -> FieldFactory[DictField]:
    error = Errors.fine
    with reader.highlight():
        if not reader.next_is("{", True, False):
            reader.exception(RuntimeError("Expected \"{\""))
            error = error.narrow(Errors.create_field)
    output_fields:list[tuple[int, str, FieldFactory, FieldFactory]] = []
    output_variables:list[tuple[int,str, FieldFactory[Variable]]] = []
    all_fields:list[tuple[str,FieldFactory]] = []
    index:int = 0
    while True:
        error = error.narrow(parse_whitespace(reader))
        if reader.next_is("}", True, False): # there is a trailing comma
            break

        if reader.next_is("$", True, False):
            key, value, new_error = parse_variable_assignment(reader)
            error = error.narrow(new_error)
            all_fields.append((f"${key}", value))
            output_variables.append((index, key, value))

        else:
            with reader.focus():
                key_string: str
                if reader.next_is("\"", True, True):
                    key_string, key_error = parse_string(reader, "\"")
                    key = FieldFactory(reader, False, key_error, (), PrimitiveField, _get_dict_key_field(key_error, key_string))
                else:
                    key_string = str(index)
                    key = parse_field(reader, False)
                all_fields.append((f"Key {key_string}", key))

            error = error.narrow(parse_whitespace(reader))
            if not reader.next_is("=", True, False):
                reader.exception(RuntimeError("Expected \"=\""))
                error = error.narrow(Errors.create_field)
            error = error.narrow(parse_whitespace(reader))

            value = parse_field(reader, abstract)
            error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR))
            all_fields.append((key_string, value))
            output_fields.append((index, key_string, key, value))

        index += 1
        if reader.next_is("}", True, False): # there is no trailing comma
            break
        elif reader.at_last():
            reader.exception(RuntimeError("Unexpected end of file"))
            error = error.narrow(Errors.create_field)
            break
        error = error.narrow(parse_separator(reader))
    return FieldFactory(reader, abstract, error, all_fields, DictField, lambda factory, scope: DictField(factory, scope, error, output_fields, output_variables))

def parse_list_field(reader:Reader, /, abstract:bool) -> FieldFactory[ListField]:
    error = Errors.fine
    with reader.highlight():
        if not reader.next_is("[", True, False):
            reader.exception(RuntimeError("Expected \"[\""))
            error = error.narrow(Errors.create_field)
    output:list[tuple[str,FieldFactory]] = []
    while True:
        error = error.narrow(parse_whitespace(reader))
        if reader.next_is("]", True, False): # there is a trailing comma
            break

        if reader.next_is("$", True, False):
            key, value, new_error = parse_variable_assignment(reader)
            error = error.narrow(new_error)
            output.append((key, value))

        else:
            value = parse_field(reader, abstract)
            output.append((str(len(output)), value))

        error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR))
        if reader.next_is("]", True, False): # there is no trailing comma
            break
        elif reader.at_last():
            reader.exception(RuntimeError("Unexpected end of file"))
            error = error.narrow(Errors.create_field)
            break
        error = error.narrow(parse_separator(reader))
    return FieldFactory(reader, abstract, error, output, ListField, lambda factory, scope: ListField(factory, scope, error, output))

def parse_component_field(reader:Reader, /, abstract:bool) -> FieldFactory[ComponentField]|FieldFactory[ComponentTypeField]:
    error = Errors.fine
    with reader.highlight():
        if not reader.next_is(":", True, False):
            reader.exception(RuntimeError("Expected \":\""))
            error = error.narrow(Errors.create_field)
    component_type, new_error = parse_identifier(reader)
    error = error.narrow(new_error)
    error = error.narrow(parse_whitespace(reader))
    if reader.next_is("{", True, True):
        fields, new_error = parse_component_fields(reader)
        error.narrow(new_error)
        return FieldFactory(reader, abstract, error, fields, ComponentField, lambda factory, scope: ComponentField(factory, scope, error, component_type, fields))
    else:
        return FieldFactory(reader, abstract, error, (), ComponentTypeField, lambda factory, scope: ComponentTypeField(factory, scope, error, component_type))

def parse_number_field(reader:Reader, /, abstract:bool) -> FieldFactory[PrimitiveField[int|float]]:
    error = Errors.fine
    with reader.highlight():
        number_string = reader.read_while(lambda char: char in "0123456789.eE+-")
        try:
            number = json.loads(number_string)
        except Exception as e:
            reader.exception(e)
            number = 0
            error = error.narrow(Errors.create_field)
        return FieldFactory(reader, abstract, error, (), PrimitiveField, lambda factory, scope: PrimitiveField(factory, scope, error, number))

def parse_field(reader:Reader, /, abstract:bool, error:Errors=Errors.fine) -> FieldFactory: # `abstract` is if the keyword "abstract" is immediately before this Field.
    with reader.focus():
        if reader.next_is("\"", True, True):
            string, new_error = parse_string(reader, "\"")
            error = error.narrow(new_error)
            output = FieldFactory(reader, abstract, error, (), PrimitiveField, lambda factory, scope: PrimitiveField(factory, scope, error, string)) # string
        elif reader.next_is("'", True, True):
            string, new_error = parse_string(reader, "'")
            error = error.narrow(new_error)
            output = FieldFactory(reader, abstract, error, (), VariableReferenceField, lambda factory, scope: VariableReferenceField(factory, scope, error, string)) # variable
        elif reader.next_in(("@", "%"), True, True):
            output = parse_reference_field(reader, abstract) # reference Field
        elif reader.next_is(":", True, True):
            output = parse_component_field(reader, abstract) # inline Component
        elif reader.next_is("#", True, True):
            output = parse_type_field(reader, abstract) # type
        elif reader.next_is("{", True, True):
            output = parse_dict_field(reader, abstract) # dict
        elif reader.next_is("[", True, True):
            output = parse_list_field(reader, abstract) # list
        elif reader.read(1, 1).isdigit() or len(chars := reader.read(2, 2)) >= 2 and chars[0] == "-" and chars[1].isdigit():
            output = parse_number_field(reader, abstract)
        else:
            if reader.next_is("'", True, True):
                string, new_error = parse_identifier(reader)
                error = error.narrow(new_error)
                output = FieldFactory(reader, abstract, error, (), VariableReferenceField, lambda factory, scope: VariableReferenceField(factory, scope, error, string))
            else:
                before_read_index = reader.index
                identifier, new_error = parse_identifier(reader)
                error = error.narrow(new_error)
                if   identifier == "true":  output = FieldFactory(reader, abstract, error, (), PrimitiveField, lambda factory, scope: PrimitiveField(factory, scope, error, True))
                elif identifier == "false": output = FieldFactory(reader, abstract, error, (), PrimitiveField, lambda factory, scope: PrimitiveField(factory, scope, error, False))
                elif identifier == "null":  output = FieldFactory(reader, abstract, error, (), PrimitiveField, lambda factory, scope: PrimitiveField(factory, scope, error, None))
                elif identifier == "inherit": reader.set(before_read_index); output = parse_reference_field(reader, abstract)
                elif identifier == "abstract":
                    if abstract:
                        reader.exception(RuntimeError("Two \"abstract\" keywords are present"))
                        error = error.narrow(Errors.returning)
                    error = error.narrow(parse_whitespace(reader, 1))
                    output = parse_field(reader, True, error)
                else: output = FieldFactory(reader, abstract, error, (), VariableReferenceField, lambda factory, scope: VariableReferenceField(factory, scope, error, identifier))

        parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR)
        if reader.next_is("+", True, False):
            parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR)
            concatenation_field1:FieldFactory = output
            concatenation_field2 = parse_field(reader, False, error)
            output = FieldFactory(reader, abstract, error, (("0", concatenation_field1), ("1", concatenation_field2)), ConcatenationField, lambda factory, scope: ConcatenationField(factory, scope, error, concatenation_field1, concatenation_field2))
        return output
    raise RuntimeError()

def parse_ctype_field(reader:Reader, /, abstract:bool) -> FieldFactory[CTypeField]:
    error = Errors.fine
    with reader.highlight():
        if not reader.next_is("(", True, False):
            reader.exception(RuntimeError("Expected \"(\""))
    output:list[tuple[str,FieldFactory]] = []
    while True:
        error = error.narrow(parse_whitespace(reader))
        # must have at least one item
        if reader.next_is(")", True, False): # there is a trailing separator or it's empty
            break
        value = parse_field(reader, abstract=False)
        error = error.narrow(parse_whitespace(reader))
        output.append((str(len(output)), value))
        if reader.next_is("|", True, False):
            pass
        elif reader.next_is(")", True, False) or reader.at_last(): # there is no trailing separator
            break
        elif reader.at_last():
            reader.exception(RuntimeError("Unexpected end of file"))
            error = error.narrow(Errors.create_field)
            break
        else:
            reader.exception(RuntimeError("Expected \"|\" or \")\""))
            error = error.narrow(Errors.create_field)
    return FieldFactory(reader, abstract, error, output, CTypeField, lambda factory, scope: CTypeField(factory, scope, error, output))

def parse_component_fields(reader:Reader, /) -> tuple[Sequence[tuple[str,FieldFactory]], Errors]:
    error = Errors.fine
    with reader.highlight():
        if not reader.next_is("{", True, False):
            reader.exception(RuntimeError("Expected \"{\""))
            error = error.narrow(Errors.create_field)
    output:list[tuple[str,FieldFactory]] = []
    already_fields:set[str] = set()
    while True:
        error = error.narrow(parse_whitespace(reader))
        if reader.next_is("}", True, False): # there is a trailing comma
            break

        if reader.next_is("$", True, False):
            key, value, new_error = parse_variable_assignment(reader)
            error = error.narrow(new_error)
            output.append((key, value))
        else:
            key, value, new_error = parse_field_assignment(reader)
            error = error.narrow(new_error)
            if key in already_fields:
                reader.exception(RuntimeError(f"Duplicate key {key}"))
                error = error.narrow(Errors.returning)
            already_fields.add(key)
            output.append((key, value))

        error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR))
        if reader.next_is("}", True, False): # there is no trailing comma
            break
        elif reader.at_last():
            reader.exception(RuntimeError("Unexpected end of file"))
            error = error.narrow(Errors.create_field)
            break
        error = error.narrow(parse_separator(reader))
    return output, error

def parse_component_assignment(reader:Reader, /) -> tuple[str,FieldFactory]:
    '''
    Parses top-level Component assignments.
    '''
    name, error = parse_identifier(reader)
    error = error.narrow(parse_whitespace(reader, 1))
    component_field = parse_field(reader, False)
    component_field.narrow(error)
    return name, component_field

def parse_file(reader:Reader, /, domain:"Domain.Domain", path:Path) -> Group:
    error = Errors.fine
    error = error.narrow(parse_whitespace(reader))
    settings:GroupSettings|None = None
    fields:dict[str,FieldFactory] = {}
    while not reader.at_last():
        if reader.next_is("settings", True, True):
            if settings is not None:
                reader.exception(RuntimeError("Settings is already defined"))
                error = error.narrow(Errors.create_field)
            else:
                settings = parse_settings(reader)
        else:
            field_name, field = parse_component_assignment(reader)
            if field_name in fields:
                reader.exception(RuntimeError(f"Duplicate Component name: {field_name}"))
                field.narrow(Errors.link_final)
                fields[field_name].narrow(Errors.link_final)
            fields[field_name] = field
        error = error.narrow(parse_whitespace(reader, chars=WHITESPACE_NO_SEPARATOR))
        if reader.at_last(): # there is no trailing newline/comma
            break
        error = error.narrow(parse_separator(reader))
    if settings is None:
        settings = GroupSettings(Aliases({}, {}, Errors.fine), Errors.fine)
    return Group(domain, path, settings, fields, reader, error)
