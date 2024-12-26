import enum
import re
from collections import defaultdict
from typing import Any, Callable

import Component.Importer as Importer
import DataMiner.DataMiner as DataMiner
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import Structure.DataPath as DataPath
import Structure.StructureTag as StructureTag
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

TAG_CHARACTERS = re.compile(r"[^\s\\\+\*\?\[\]\(\)\{\}\=\!\<\>\|\-\/\~]") # using exclusive because of multitudinous language characters
# valid tag characters are a-zA-Z0-9, _, ., and non-ascii not-whitespace characters

class BinaryOperator(enum.Enum):
    union = "|"
    intersection = "&"
    difference = "-"
    symmetric_difference = "^"

class UnaryOperator(enum.Enum):
    embedded_data = "/"
    last_key = "~"
    remove_embedded_data = "?"

unary_operator_letters = [operator.value for operator in UnaryOperator]

class DataReader():

    def __init__(self, data:str) -> None:
        self.data = data
        self.position = 0

    def __repr__(self) -> str:
        return "<%s pos %i/%i>" % (self.__class__.__name__, self.position, len(self.data))

    def read(self, amount:int=1, back:int=0) -> str:
        output = self.data[self.position : self.position+amount]
        self.position += amount
        self.position -= back
        return output

    def forward(self, amount:int=1) -> None:
        self.position += amount

    def back(self, amount:int=1) -> None:
        self.position -= amount

    def is_at_last_index(self) -> bool:
        return self.position == len(self.data)

def parse_tag(data:DataReader) -> tuple[Callable[[dict[str, set[DataPath.DataPath]]], set[DataPath.DataPath]], str]:
    letters:list[str] = []
    while True:
        letter = data.read()
        if not re.match(TAG_CHARACTERS, letter):
            break
        letters.append(letter)
    data.back()
    tag_name = "".join(letters)
    return lambda all_mentioned_tags: all_mentioned_tags[tag_name], tag_name

def parse_binary_operator(data:DataReader) -> BinaryOperator:
    letters:list[str] = []
    while True:
        letter = data.read()
        if letter == " " or re.match(TAG_CHARACTERS, letter):
            break
        letters.append(letter)
    data.back()
    operator = "".join(letters)
    return BinaryOperator(operator)

def parse_unary_operator(data:DataReader) -> UnaryOperator:
    letters:list[str] = []
    while True:
        letter = data.read()
        if letter in "( " or re.match(TAG_CHARACTERS, letter):
            break
        letters.append(letter)
    data.back()
    operator = "".join(letters)
    return UnaryOperator(operator)

def parse_whitespace(data:DataReader) -> None:
    while data.read() == " ": pass
    data.back()

def parse_expression(data:DataReader) -> tuple[Callable[[dict[str, set[DataPath.DataPath|Any]]], set[DataPath.DataPath|Any]], set[str]]:
    parse_whitespace(data)
    character = data.read(1, 1)
    if re.match(TAG_CHARACTERS, character):
        tag_function, tag_name = parse_tag(data)
        return tag_function, set([tag_name])
    elif character == "(":
        mentioned_tags:set[str] = set()
        data.forward(1) # because it just went back in condition
        parse_whitespace(data)
        argument1, new_tags = parse_expression(data)
        mentioned_tags.update(new_tags)
        parse_whitespace(data)
        operator = parse_binary_operator(data)
        parse_whitespace(data)
        argument2, new_tags = parse_expression(data)
        mentioned_tags.update(new_tags)
        parse_whitespace(data)
        if data.read(1) != ")":
            raise Exceptions.TagSearcherParseError(data, "Expected \")\"")
        match operator:
            case BinaryOperator.union:
                return lambda all_mentioned_tags: argument1(all_mentioned_tags) | argument2(all_mentioned_tags), mentioned_tags
            case BinaryOperator.intersection:
                return lambda all_mentioned_tags: argument1(all_mentioned_tags) & argument2(all_mentioned_tags), mentioned_tags
            case BinaryOperator.difference:
                return lambda all_mentioned_tags: argument1(all_mentioned_tags) - argument2(all_mentioned_tags), mentioned_tags
            case BinaryOperator.symmetric_difference:
                return lambda all_mentioned_tags: argument1(all_mentioned_tags) ^ argument2(all_mentioned_tags), mentioned_tags
    elif character in unary_operator_letters:
        mentioned_tags:set[str] = set()
        operator = parse_unary_operator(data)
        parse_whitespace(data)
        argument, new_tags = parse_expression(data)
        mentioned_tags.update(new_tags)
        match operator:
            case UnaryOperator.embedded_data:
                return lambda all_mentioned_tags: {data_path.embedded_data for data_path in argument(all_mentioned_tags)}, mentioned_tags
            case UnaryOperator.last_key:
                return lambda all_mentioned_tags: {data_path.last_key() for data_path in argument(all_mentioned_tags)}, mentioned_tags
            case UnaryOperator.remove_embedded_data:
                return lambda all_mentioned_tags: {data_path.remove_embedded_data() for data_path in argument(all_mentioned_tags)}, mentioned_tags
    else:
        raise Exceptions.TagSearcherParseError(data, "Unexpected character \"%s\"" % (character,))

def parse(string:str) -> tuple[Callable[[dict[str, set[DataPath.DataPath|Any]]], set[DataPath.DataPath|Any]], set[str]]:
    data = DataReader(string)
    output = parse_expression(data)
    if not data.is_at_last_index():
        raise Exceptions.TagSearcherParseError(data, "Tag expression finished before completing")
    return output


class TagSearcherDataMiner(DataMiner.DataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("sort_output", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("none_okay", "a bool", False, bool),
    )

    @classmethod
    def manipulate_arguments(cls, arguments: dict[str, Any]) -> None:
        arguments["tag_function"], arguments["tag_names"] = parse(arguments["tags"])

    def initialize(self, tags:str, tag_function:Callable[[dict[str, set[DataPath.DataPath|Any]]], set[DataPath.DataPath|Any]], tag_names:set[str], sort_output:bool, none_okay:bool=False) -> None:
        self.tags = tags
        self.tag_function = tag_function
        self.tag_names = tag_names
        self.sort_output = sort_output
        self.none_okay = none_okay

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataPath.DataPath|Any]:
        dependencies = set(self.dependencies)
        all_tags = Importer.structure_tags
        printer_environment = environment.get_printer_environment(self.version)
        tag_dataminer_collections:defaultdict[AbstractDataMinerCollection.AbstractDataMinerCollection,list[StructureTag.StructureTag]] = defaultdict(lambda: [])
        for tag in self.tag_names:
            if tag not in all_tags:
                raise Exceptions.UnrecognizedStructureTagError(self.tags, tag)
            for dataminer_collection in Importer.dataminer_collections.values():
                if dataminer_collection.has_tag(all_tags[tag]):
                    if dataminer_collection not in dependencies:
                        raise Exceptions.TagSearcherDependencyError(self, all_tags[tag], dataminer_collection)
                    tag_dataminer_collections[dataminer_collection].append(all_tags[tag])
        mentioned_tags:defaultdict[str,set[DataPath.DataPath]] = defaultdict(lambda: set())
        for dataminer_collection, tags in tag_dataminer_collections.items():
            for tag, paths in dataminer_collection.get_tag_paths(self.version, tags, printer_environment).items():
                mentioned_tags[tag.name].update(paths)
        output = self.tag_function(mentioned_tags)

        if not self.none_okay and len(output) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        output_list = list(output)
        if self.sort_output:
            output_list.sort() # type: ignore
        return output_list
