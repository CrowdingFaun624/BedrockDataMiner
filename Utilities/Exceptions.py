from datetime import date, datetime
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Container, Literal, Optional, Sequence

if TYPE_CHECKING:
    from Component.Capabilities import Capabilities
    from Component.Component import Component
    from Component.ComponentTyping import ComponentTypedDicts
    from Component.Field.Field import Field
    from Component.Group import Group
    from Component.Pattern import Pattern
    from Component.Version.VersionComponent import VersionComponent
    from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
    from Dataminer.BuiltIns.TagSearcherDataminer import DataReader
    from Dataminer.Dataminer import Dataminer, NullDataminer
    from Dataminer.DataminerEnvironment import DataminerDependencies
    from Dataminer.DataminerSettings import DataminerSettings
    from Downloader.Accessor import Accessor
    from Serializer.Serializer import Serializer
    from Structure.DataPath import DataPath
    from Structure.Delegate.Delegate import Delegate
    from Structure.Normalizer import Normalizer
    from Structure.Structure import Structure
    from Structure.StructureInfo import StructureInfo
    from Structure.StructureTag import StructureTag
    from Tablifier.Tablifier import Tablifier
    from Utilities.Cache import Cache
    from Utilities.DataFile import DataFile
    from Utilities.File import AbstractFile, File
    from Utilities.Log import Log
    from Utilities.Scripts import Script
    from Utilities.TypeUtilities import TypeSet
    from Utilities.TypeVerifier import TypedDictTypeVerifier, TypeVerifier
    from Version.Version import Version
    from Version.VersionFile import VersionFile
    from Version.VersionFileType import VersionFileType
    from Version.VersionRange import VersionRange
    from Version.VersionTag.VersionTag import VersionTag

def message[a](message:a|None, no_message:str="!", yes_message:str=" %s!", stringify_function:Callable[[a],str]|None=None) -> str:
    if stringify_function is None:
        return no_message if message is None else yes_message % (message,)
    else:
        return no_message if message is None else yes_message % (stringify_function(message),)

def message_bool(display_switch:bool, false_message:str|Callable[[],str]="", true_message:str|Callable[[],str]="") -> str:
    if display_switch:
        return false_message() if callable(false_message) else false_message
    else:
        return true_message() if callable(true_message) else true_message

@cache
def get_nearest(_str:str, options:frozenset[str]) -> str|None:
    min_option:str|None = None
    min_distance:float|None = None
    second_min_distance:float|None = None
    for option in options:
        if option == min_option: continue
        distances:list[list[int]] = [[0] * (len(_str) + 1) for y in range(len(option) + 1)]
        path:list[list[int]] = [[0] * (len(_str) + 1) for y in range(len(option) + 1)]
        for x in range(1, len(_str) + 1):
            distances[0][x] = x
        for y in range(1, len(option) + 1):
            path[y][0] = 1
            distances[y][0] = y
        for y in range(len(option)):
            for x in range(len(_str)):
                addition_cost = distances[y+1][x] + 1
                removal_cost = distances[y][x+1] + 1
                substitution_cost = distances[y][x] + int(inequality := (_str[x] != option[y]))
                if addition_cost < removal_cost and addition_cost < substitution_cost:
                    path[y + 1][x + 1] = 0
                    distances[y + 1][x + 1] = addition_cost
                elif removal_cost < substitution_cost:
                    path[y + 1][x + 1] = 1
                    distances[y + 1][x + 1] = removal_cost
                else:
                    path[y + 1][x + 1] = 3 if inequality else 2
                    distances[y + 1][x + 1] = substitution_cost

        # weirdness is a measure of how many "turns" the path hash through the
        # Levenshtein space.
        x, y = len(_str), len(option)
        weirdness = 0
        adjusted_distance = 0
        previous = -1
        while x > 0 or y > 0:
            match (item := path[y][x]):
                case 0:
                    x -= 1
                    adjusted_distance += 1
                case 1:
                    y -= 1
                    adjusted_distance += 1
                case 2 | 3:
                    x -= 1; y -= 1
                    adjusted_distance += item == 3
            if item != previous:
                previous = item
                weirdness += 1

        distance = adjusted_distance * 1 + weirdness * 1
        if min_distance is None or distance < min_distance:
            second_min_distance = min_distance
            min_option = option
            min_distance = distance
    if min_distance is not None and min_distance < 10 and (second_min_distance is None or second_min_distance - min_distance > 0.5):
        return min_option

def nearest_message(value:str, options:list[str]) -> str:
    nearest = get_nearest(value, frozenset(options))
    if nearest is None:
        return ""
    else:
        return f" Did you mean {nearest}?"

# Within this file, an "Exception" is an abstract type and
# an "Error" is a concrete type.
# one-off exceptions related to the domain don't need a custom error type

class AttributeNoneError(Exception):
    "The attribute is None when, at the time of calling, it should not be None."

    def __init__(self, name:str, source:object, message:Optional[str]=None) -> None:
        super().__init__(name, source, message)
        self.name = name
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"Attribute \"{self.name}\" of {self.source} is None and should not be{message(self.message)}"

class EmptyFileError(Exception):
    "The file IO has no bytes."

    def __init__(self, message:Optional[str]=None) -> None:
        '''
        :message: Additional text to place after the main message.
        '''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"A file has no bytes{message(self.message)}"

class ImportOrderError(Exception):
    "A module has been imported at the wrong time."

    def __init__(self, module_name:str, message:Optional[str]=None) -> None:
        '''
        :module_name: The name of the Module that was imported too early.
        :message: Additional text to place after the main message.
        '''
        super().__init__(module_name, message)
        self.module_name = module_name
        self.message = message

    def __str__(self) -> str:
        return f"Module {self.module_name} was imported too early{message(self.message)}"

class InvalidStateError(Exception):
    "The program has reached an assumedly unreachable part of the code."

    def __str__(self) -> str:
        return f"Invalid state{message(self.args, yes_message=": %s!")}"

class CacheException(Exception):
    "Abstract Exception class for errors relating to Caches."

class CacheCannotWriteError(CacheException):
    "Attempted to write to a Cache that cannot be written to."

    def __init__(self, cache:"Cache", message:Optional[str]=None) -> None:
        '''
        :cache: The Cache that cannot be written to.
        :message: Additional text to place after the main message.
        '''
        super().__init__(cache, message)
        self.cache = cache
        self.message = message

    def __str__(self) -> str:
        return f"{self.cache} cannot be written to{message(self.message)}"

class CacheDeserializeError(CacheException):
    "Attempted to write a Cache that has no `deserialize` method defined."

    def __init__(self, cache:"Cache", message:Optional[str]=None) -> None:
        '''
        :cache: The Cache with no `deserialize` method.
        :message: Additional text to place after the main message.
        '''
        super().__init__(cache, message)
        self.cache = cache
        self.message = message

    def __str__(self) -> str:
        return f"{self.cache} has no deserialize method; cannot write{message(self.message)}"

class CacheFileNotFoundError(CacheException):
    "Attempted to open a Cache that has no `get_default_content` method and no existing file."

    def __init__(self, cache:"Cache", message:Optional[str]=None) -> None:
        '''
        :cache: The Cache with no `get_default_content` method.
        :message: Additional text to place after the main message.
        '''
        super().__init__(cache, message)
        self.cache = cache
        self.message = message

    def __str__(self) -> str:
        return f"{self.cache} has no get_default_content method and its file does not exist{message(self.message)}"

class ComponentException(Exception):
    "Abstract Exception class for errors relating to Components."

class ComponentCountError(ComponentException):
    "There is an invalid number of BaseComponents."

    def __init__(self, components:Sequence[Any], object_type:type, message:Optional[str]=None) -> None:
        '''
        :components: The list of Components of duplicate type.
        :object_type: The type of final in `components`.
        :message: Additional text to place after the main message.
        '''
        super().__init__(components, object_type, message)
        self.components = components
        self.object_type = object_type
        self.message = message

    def __str__(self) -> str:
        return f"There is not exactly one Components of type {self.object_type.__name__}{": " if len(self.components) > 0 else ""}{", ".join(component.name for component in self.components)}{message(self.message)}"

class ComponentDuplicateTypeError(ComponentException):
    "A Component has a duplicate type."

    def __init__(self, type_str:str, message:Optional[str]=None) -> None:
        '''
        :type_str: The name of the type that is duplicated.
        :message: Additional text to place after the main message.
        '''
        super().__init__(type_str, message)
        self.type_str = type_str
        self.message = message

    def __str__(self) -> str:
        return f"Type \"{self.type_str}\" is duplicate{message(self.message)}"

class ComponentFileError(ComponentException):
    "Failed to read a Component file."

    def __init__(self, file:Path, contents:bytes, message:Optional[str]=None) -> None:
        '''
        :file: The name of the invalid file.
        :contents: The byte contents of the invalid file.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file, contents, message)
        self.file = file
        self.contents = contents
        self.message = message

    def __str__(self) -> str:
        return f"Cannot read file{self.file}{message(self.message, no_message=": ", yes_message=" %s: ")}{self.contents}"

class ComponentInvalidNameCharacterError(ComponentException):
    "A Component has a name with an illegal character."

    def __init__(self, component:"Component", invalid_characters:list[str], message:Optional[str]=None) -> None:
        '''
        :component: The Component with an invalid character.
        :invalid_characters: A list of characters this Component cannot have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, invalid_characters, message)
        self.component = component
        self.invalid_characters = invalid_characters
        self.message = message

    def __str__(self) -> str:
        return f"The name of {self.component} cannot have any characters within {"".join(self.invalid_characters)}{message(self.message)}"

class ComponentInvalidNameError(ComponentException):
    "A Component has an illegal name."

    def __init__(self, component:"Component", invalid_names:list[str], message:Optional[str]=None) -> None:
        '''
        :component: The Component with an invalid name.
        :invalid_names: A list of names that this Component cannot have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, invalid_names, message)
        self.component = component
        self.invalid_names = invalid_names
        self.message = message

    def __str__(self) -> str:
        return f"The name of {self.component} cannot be one of {self.invalid_names}{message(self.message)}"

class ComponentInvalidVersionRangeException(ComponentException):
    "Abstract exception class for errors relating to invalid VersionRanges."

class ComponentVersionRangeExists(ComponentInvalidVersionRangeException):
    "The new/old Version of the first/last sub-Component is not None."

    def __init__(self, actual_value:"Version", is_first:bool, message:Optional[str]=None) -> None:
        '''
        :actual_value: The value that is present in the new Version instead of None.
        :is_first: Whether this DataminerSettings is the newest one or not.
        :message: Additional text to place after the main message.
        '''
        super().__init__(actual_value, is_first, message)
        self.actual_value = actual_value
        self.is_first = is_first
        self.message = message

    def __str__(self) -> str:
        return f"The {"new" if self.is_first else "old"} Version of the {"first" if self.is_first else "last"} DataminerSettings is not None, but instead {self.actual_value}{message(self.message)}"

class ComponentVersionRangeGap(ComponentInvalidVersionRangeException):
    "There is a gap in a Components's sub-Components' Versions."

    def __init__(self, new_version:"Version", old_version:"Version", message:Optional[str]=None) -> None:
        '''
        :new_version: The Version or the Version's name on the newer side of the gap.
        :old_version: The Version or the Version's name on the older side of the gap.
        :message: Additional text to place after the main message.
        '''
        super().__init__(new_version, old_version, message)
        self.new_version = new_version
        self.old_version = old_version
        self.message = message

    def __str__(self) -> str:
        return f"There is a gap between Versions {self.new_version} and {self.old_version}{message(self.message)}"

class ComponentVersionRangeMissing(ComponentInvalidVersionRangeException):
    "The new or old Version of a non-first DataminerSettings is None."

    def __init__(self, slot:Literal["old", "new"], message:Optional[str]=None) -> None:
        '''
        :index: The index of the DataminerSettings
        :slot: The key ("old" or "new") of the sub-Component.
        :message: Additional text to place after the main message.
        '''
        super().__init__(slot, message)
        self.slot = slot
        self.message = message

    def __str__(self) -> str:
        return f"The {self.slot} Version is None{message(self.message)}"

class ComponentMismatchedTypesError(ComponentException):
    "The types of one Component and the types of another do not match."

    def __init__(self, component1:"Component", component1_types:list[type], component2:"Component", component2_types:list[type], message:Optional[str]=None) -> None:
        '''
        :component1: The first Component or a string representing it.
        :component1_types: The types allowed by the first Component.
        :component2: The second Component or a string representing it.
        :component2_types: The types allowed by the second Component.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component1, component1_types, component2, component2_types, message)
        self.component1 = component1
        self.component1_types = component1_types
        self.component2 = component2
        self.component2_types = component2_types
        self.message = message

    def __str__(self) -> str:
        return f"{self.component1} accepts types [{", ".join(f"\"{type.__name__}\"" for type in self.component1_types)}], but its subcomponent, {self.component2}, accepts types [{", ".join(f"\"{type.__name__}\"" for type in self.component2_types)}]{message(self.message)}"

class ComponentParseError(ComponentException):
    "Multiple Components failed to parse."

    def __init__(self, failed_groups:list[str], exception_count:int, message:Optional[str]=None) -> None:
        '''
        :failed_groups: The Groups that failed to parse.
        :exception_count: The number of total Exceptions.
        :message: Additional text to place after the main message.
        '''
        super().__init__(failed_groups, exception_count, message)
        self.failed_groups = failed_groups
        self.exception_count = exception_count
        self.message = message

    def __str__(self) -> str:
        return f"{self.exception_count} exceptions in {len(self.failed_groups)} Groups: [{", ".join(self.failed_groups)}]{message(self.message)}"

class ComponentScriptUnreferenceableError(ComponentException):
    "The Component corresponding to the object accessed by a ScriptReferenceable does not allow script referencing of its final."

    def __init__(self, path:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :path: The path used to access the Component's final.
        :options: All paths that can be used to access valid script-referenceable objects.
        :message: Additional text to place after the main message.
        '''
        super().__init__(path, options, message)
        self.path = path
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Component at \"{self.path}\" does not allow for its final to be referenced by Scripts{message(self.message)}{nearest_message(self.path, self.options)}"

class ComponentTypeContainmentError(ComponentException):
    "A Component has a type that cannot be contained by its current container type."

    def __init__(self, container_type:type, containee_type:type, message:Optional[str]=None) -> None:
        '''
        :container_type: The type of the container.
        :containee_type: The type contained by the container type.
        :message: Additional text to place after the main message.
        '''
        super().__init__(container_type, containee_type, message)
        self.container_type = container_type
        self.containee_type = containee_type
        self.message = message

    def __str__(self) -> str:
        return f"Type \"{self.containee_type}\" cannot be contained by type \"{self.container_type}\"{message(self.message)}"

class ComponentTypeInvalidTypeError(ComponentException):
    "A Component has a value in a TypeField that is not allowed."

    def __init__(self, observed_type:type, allowed_types:"TypeSet", message:Optional[str]=None) -> None:
        '''
        :observed_type: The type that is not allowed.
        :allowed_types: The set of types that this TypeField must be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(observed_type, allowed_types, message)
        self.observed_type = observed_type
        self.allowed_types = allowed_types
        self.message = message

    def __str__(self) -> str:
        return f"{self.observed_type} is not one of [{", ".join(type.__name__ for type in sorted(self.allowed_types, key=lambda value: value.__name__))}]{message(self.message)}"

class ComponentTypeMissingError(ComponentException):
    "A Component is missing the type key and there is no type assumption."

    def __init__(self, component_name:str, group:"Group", message:Optional[str]=None) -> None:
        '''
        :component_name: The name of the Component with the missing type key.
        :group: The Group the Component is found in.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component_name, group, message)
        self.component_name = component_name
        self.group = group
        self.message = message

    def __str__(self) -> str:
        return f"Component \"{self.component_name}\" in {self.group} is missing its type key{message(self.message)}"

class ComponentTypeRequiresComponentError(ComponentException):
    "A Component has a type that requires a Component but has no Component."

    def __init__(self, component:"Component|str", accepted_type:type, message:Optional[str]=None) -> None:
        '''
        :component: The Component referencing the type or a string representing it.
        :accepted_type: The type requiring a Component.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, accepted_type, message)
        self.component = component
        self.accepted_type = accepted_type
        self.message = message

    def __str__(self) -> str:
        return f"{self.component} accepts type \"{self.accepted_type.__name__}\", which requires a Component, but has no sub-Component{message(self.message)}"

class ComponentUnrecognizedTypeError(ComponentException):
    "This Component references an unrecognized default type."

    def __init__(self, type_str:str, message:Optional[str]=None) -> None:
        '''
        :type_str: The name of the unrecognized type.
        :message: Additional text to place after the main message.
        '''
        super().__init__(type_str, message)
        self.type_str = type_str
        self.message = message

    def __str__(self) -> str:
        return f"Type \"{self.type_str}\" is unrecognized{message(self.message)}"

class GroupAliasDomainError(ComponentException):
    "Attempted to create a Group alias with a target in another Domain."

    def __init__(self, alias:str, target:str, message:Optional[str]=None) -> None:
        '''
        :alias: The alias name.
        :target: The invalid target name.
        :message: Additional text to place after the main message.
        '''
        super().__init__(alias, target, message)
        self.alias = alias
        self.target = target
        self.message = message

    def __str__(self) -> str:
        return f"Cannot create Group alias \"{self.alias}\": \"{self.target}\" to another Domain{message(self.message)}"

class InlineComponentError(ComponentException):
    "An inline Component exists where it is not allowed."

    def __init__(self, component:"Component", field:"Field", subcomponent_data:Optional["ComponentTypedDicts"]=None, message:Optional[str]=None) -> None:
        '''
        :component: The Component with the disallowed inline subcomponent.
        :field: The Field with the disallowed inline subcomponent.
        :subcomponent_data: The data used to specify the subcomponent.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, field, subcomponent_data, message)
        self.component = component
        self.field = field
        self.subcomponent_data = subcomponent_data
        self.message = message

    def __str__(self) -> str:
        return f"{self.component}, {self.field} attempted to create a disallowed inline Component{message(self.message, yes_message=" %s")}{message(self.subcomponent_data, yes_message=": %s")}"

class InvalidComponentError(ComponentException):
    "The referenced Component has the wrong properties."

    def __init__(self, component:"Component", key:str|None, required_properties:"Pattern", actual_capabilities:"Capabilities", options:list[str]|None, message:Optional[str]=None) -> None:
        '''
        :component: The Component that is being referenced.
        :key: The key used to reference the Component.
        :required_properties: The Pattern that the Component is expected to have.
        :actual_capabilities: The Capabilities that the Component actually has.
        :options: Values the Component reference could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, key, required_properties, actual_capabilities, options, message)
        self.component = component
        self.key = key
        self.required_properties = required_properties
        self.actual_capabilities = actual_capabilities
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"{self.component} is expected to have {self.required_properties}, but only has {self.actual_capabilities}{message(self.message)}{nearest_message(self.key, self.options) if self.key is not None and self.options is not None else None}"

class InvalidComponentFinalTypeError(ComponentException):
    "The referenced Component's final is the wrong type."
    # used exclusively by ScriptReferenceable

    def __init__(self, path:str, object:Any, required_type:type, actual_type:type, options:list[str], message:Optional[str]=None) -> None:
        '''
        :path: The key used to reference the Component.
        :object: The Component's final.
        :required_type: The type that the Component's final should be.
        :actual_type: The type that the Component's final is.
        :options: Values the path could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(path, object, required_type, actual_type, options, message)
        self.path = path
        self.object = object
        self.required_type = required_type
        self.actual_type = actual_type
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"{self.object:r} at \"{self.path}\" should be type {self.required_type.__name__}, but is actually {self.actual_type.__name__}{message(self.message)}{nearest_message(self.path, self.options)}"

class LinkedComponentExtraError(ComponentException):
    "An extra linked Component is present."

    def __init__(self, key:str, linked_object:Any, options:list[str], message:Optional[str]=None) -> None:
        '''
        :key: The key of the extra linked Component.
        :linked_object: The object of the linked Component.
        :options: Values that `key` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, linked_object, options, message)
        self.key = key
        self.linked_object = linked_object
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"There is an extra linked Component \"{self.key}\": {self.linked_object}{message(self.message)}{nearest_message(self.key, self.options)}"

class LinkedComponentMissingError(ComponentException):
    "A linked Component is missing."

    def __init__(self, key:str, linked_type:type, message:Optional[str]=None) -> None:
        '''
        :key: The key of the missing Component.
        :linked_type: The type of the linked object.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, linked_type, message)
        self.key = key
        self.linked_type = linked_type
        self.message = message

    def __str__(self) -> str:
        return f"Missing linked Component \"{self.key}\" of type \"{self.linked_type.__name__}\"{message(self.message)}"

class LinkedComponentTypeError(ComponentException):
    "A linked Component's object is the wrong type."

    def __init__(self, key:str, required_type:type, observed_object:Any, message:Optional[str]=None) -> None:
        '''
        :key: The key of the linked Component.
        :required_type: The type the linked object should have.
        :observed_object: The linked object.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, required_type, observed_object, message)
        self.key = key
        self.required_type = required_type
        self.observed_object = observed_object
        self.message = message

    def __str__(self) -> str:
        return f"Linked object \"{self.key}\": {self.observed_object} should be type \"{self.required_type.__name__}\"{message(self.message)}"

class MalformedComponentReferenceError(ComponentException):
    "A reference Component is invalid."

    def __init__(self, key:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :key: The key used to reference the Component
        :options: Values that `key` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, options, message)
        self.key = key
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Component reference \"{self.key}\" is malformed{message(self.message)}{nearest_message(self.key, self.options)}"

class ReferenceComponentError(ComponentException):
    "A reference Component exists where it is not allowed."

    def __init__(self, component:"Component", field:"Field", subcomponent_name:Optional[str]=None, message:Optional[str]=None) -> None:
        '''
        :component: The Component with the disallowed inline subcomponent.
        :field: The Field with the disallowed inline subcomponent.
        :subcomponent_name: The name of the subcomponent.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, field, subcomponent_name, message)
        self.component = component
        self.field = field
        self.subcomponent_name = subcomponent_name
        self.message = message

    def __str__(self) -> str:
        return f"{self.component}, {self.field} attempted to reference a disallowed reference Component{message(self.subcomponent_name, "", " \"%s\"")}{message(self.message)}"

class UnrecognizedCapabilityError(ComponentException):
    "A capability is unrecognized."

    def __init__(self, property:str, message:Optional[str]=None) -> None:
        '''
        :property: The name of the unrecognized capability property.
        :message: Additional text to place after the main message.
        '''
        super().__init__(property, message)
        self.property = property
        self.message = message

    def __str__(self) -> str:
        return f"Key \"{self.property}\" is not a recognized property{message(self.message)}"

class UnrecognizedComponentError(ComponentException):
    "A Component is unrecognized."

    def __init__(self, component_str:str, key:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :component_str: The name of the unrecognized Component.
        :key: The key used to reference the Component.
        :source: The object that refers to this Component.
        :options: Values the Component key could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component_str, key, options, message)
        self.component_str = component_str
        self.key = key
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Component \"{self.component_str}\" is unrecognized{message(self.message)}{nearest_message(self.key, self.options)}"

class UnrecognizedComponentDomainError(ComponentException):
    "A Domain referenced by a Component is unrecognized."

    def __init__(self, domain:str, key:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :domain: The name of the unrecognized Domain.
        :key: The key used to reference the Component.
        :options: Values that `key` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(domain, key, options, message)
        self.domain = domain
        self.key = key
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Domain \"{self.domain}\" is unrecognized{message(self.message)}{nearest_message(self.key, self.options)}"

class UnrecognizedGroupError(ComponentException):
    "A Group is unrecognized"

    def __init__(self, group_name:str, key:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :group_name: The name of the unrecognized Group.
        :key: The key used to reference the Component.
        :options: Values that `key` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(group_name, key, options, message)
        self.group_name = group_name
        self.key = key
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Group \"{self.group_name}\" is unrecognized{message(self.message)}{nearest_message(self.key, self.options)}"

class UnrecognizedComponentTypeError(ComponentException):
    "A Component type is unrecognized."

    def __init__(self, component_type:str, source:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :component_type: The name of the unrecognized Component type.
        :source: The object that refers to this Component type.
        :options: Values that the Component type could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component_type, source, options, message)
        self.component_type = component_type
        self.source = source
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Component type \"{self.component_type}\", as referenced by {self.source}, is unrecognized{message(self.message)}{nearest_message(self.component_type, self.options)}"

class CustomJsonException(Exception):
    "Abstract Exception class for errors relating to custom JSON encoders and decoders."

class CannotEncodeToJsonError(CustomJsonException):
    "The object cannot be encoded to JSON."

    def __init__(self, source:object, message:Optional[str]=None) -> None:
        '''
        :source: The object that cannot be encoded to JSON.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, message)
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"Object {self.source} of type {self.source.__class__.__name__} cannot be encoded to JSON{message(self.message)}"

class InvalidSpecialTypeError(CustomJsonException):
    "The $special_type key has a value that is not recognized."

    def __init__(self, special_type:str, message:Optional[str]=None) -> None:
        '''
        :special_type: The value of $special_type.
        :message: Additional text to place after the main message.
        '''
        super().__init__(special_type, message)
        self.special_type = special_type
        self.message = message

    def __str__(self) -> str:
        return f"Invalid $special_type of \"{self.special_type}\" received{message(self.message)}"

class DataFileException(Exception):
    "Exception relating to DataFiles"

class DataFileNothingToWriteError(DataFileException):
    "Called `write` on a DataFile without any content."

    def __init__(self, source:"DataFile", message:Optional[str]=None) -> None:
        '''
        :source: The DataFile that has nothing to write.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, message)
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"{self.source} cannot be written if not yet read{message(self.message)}"

class DataminerException(Exception):
    "Abstract Exception class for errors relating to Dataminers."

class DataminerAccessorWrongTypeError(DataminerException):
    "The assumed type of an Accessor is not its actual type."

    def __init__(self, dataminer:"Dataminer", file_type:str, accessor_type:type["Accessor"], options:list[str], message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that attempted to access its Accessor.
        :file_type: The name of the VersionFile that has the wrong Accessor type.
        :accessor_type: The type that the Accessor should be.
        :options: Values that `file_type` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, file_type, accessor_type, options, message)
        self.dataminer = dataminer
        self.file_type = file_type
        self.accessor_type = accessor_type
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"VersionFile \"{self.file_type}\" from {self.dataminer} should have Accessor with type \"{self.accessor_type.__name__}\"{message(self.message)}"

class DataminerCannotKnowFileTypeError(DataminerException):
    "Attempted to access a Dataminer's VersionFileTypes with no key, but there are too many VersionFileTypes."

    def __init__(self, dataminer:"Dataminer", count:int, message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer with too many VersionFileTypes.
        :count: The number of VersionFileTypes.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, count, message)
        self.dataminer = dataminer
        self.count = count
        self.message = message

    def __str__(self) -> str:
        return f"Cannot know which VersionFileType {self.dataminer}.get_accessor is referring to, since there are more than 1 ({self.count}) VersionFileTypes{message(self.message)}"

class DataminerCollectionFileError(DataminerException):
    "The \"files\" key in a DataminerCollection is improperly specified."

    def __init__(self, exists:bool, message:Optional[str]=None) -> None:
        '''
        :exists: Whether or not the "files" key actually exists.
        :message: Additional text to place after the main message.
        '''
        super().__init__(exists, message)
        self.exists = exists
        self.message = message

    def __str__(self) -> str:
        return f"Key \"files\" {"cannot" if self.exists else "must"} exist{message(self.message)}"

class DataminerDependencyOverwriteError(DataminerException):
    "Attempted to set an item of a DataminerDependencies object that already exists."

    def __init__(self, dataminer_dependencies:"DataminerDependencies", dependency_name:str, message:Optional[str]=None) -> None:
        '''
        :dataminer_dependencies: The DataminerDependencies that had an item overwritten.
        :dependency_name: The dependency that was overwritten.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_dependencies, dependency_name, message)
        self.dataminer_dependencies = dataminer_dependencies
        self.dependency_name = dependency_name
        self.message = message

    def __str__(self) -> str:
        return f"Attempted to overwrite dependency \"{self.dependency_name}\" of {self.dataminer_dependencies}{message(self.message)}"

class DataminerDuplicateFileNameError(DataminerException):
    "Two DataminerCollections have the same file name."

    def __init__(self, file_name:str, dataminers:list["AbstractDataminerCollection"], message:Optional[str]=None) -> None:
        '''
        :file_name: The file name shared by all of the DataminerCollections.
        :dataminers: The DataminerCollections that share the same file name.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_name, dataminers, message)
        self.file_name = file_name
        self.dataminers = dataminers
        self.message = message

    def __str__(self) -> str:
        return f"DataminerCollection [{", ".join(dataminer.name for dataminer in self.dataminers)}] all have the same file name \"{self.file_name}\"{message(self.message)}"

class DataminerFileTypePermissionError(DataminerException):
    "A Dataminer attempted to access a VersionFileType it has no permissions to use."

    def __init__(self, dataminer:"Dataminer", file_type_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that attempted to access a VersionFileType without permission.
        :file_type_name: The name of the VersionFileType it attempted to access.
        :options: Values that `file_type_name` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, file_type_name, options, message)
        self.dataminer = dataminer
        self.file_type_name = file_type_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} attempted to access VersionFileType {self.file_type_name}; permissions are lacking or it does not exist{message(self.message, "", " %s")}{nearest_message(self.file_type_name, self.options)}"

class DataminerLacksActivateError(DataminerException):
    "A Dataminer did not override the activate function."

    def __init__(self, dataminer:"Dataminer", message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that is missing the activate function.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} is missing its activate function{message(self.message)}"

class DataminerNoFileTypeError(DataminerException):
    "A Dataminer has no linked VersionFileTypes and should."

    def __init__(self, dataminer:"Dataminer", message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer with no VersionFileTypes specified.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} has no VersionFileTypes; cannot access one{message(self.message)}"

class DataminerNothingFoundError(DataminerException):
    "This Dataminer found nothing."

    def __init__(self, dataminer:"Dataminer", message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that failed to find anything.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} failed to find anything{message(self.message)}"

class DataminerNullReturnError(DataminerException):
    "The Dataminer's activate method has returned None."

    def __init__(self, dataminer:"AbstractDataminerCollection", message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer whose activate method returned None.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} returned None upon being activated{message(self.message)}"

class DataminerSettingsImporterLoopError(DataminerException):
    "A DataminerSettings has an import loop."

    def __init__(self, dataminer_settings:"DataminerSettings", loop_items:Sequence[str], message:Optional[str]=None) -> None:
        '''
        :dataminer_settings: The initial DataminerSettings containing the loop.
        :loop_items: A list of DataminerCollection names contained in the loop.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_settings, loop_items, message)
        self.dataminer_settings = dataminer_settings
        self.loop_items = loop_items
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer_settings} has an import loop involving {self.loop_items}{message(self.message)}"

class DataminersFailureError(DataminerException):
    "Multiple Dataminers failed to activate."

    def __init__(self, version:"Version", dataminer_collections:list["AbstractDataminerCollection"], message:Optional[str]=None) -> None:
        '''
        :version: The Version for which datamining failed.
        :dataminer_collections: The DataminerCollections that failed to activate on this Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, dataminer_collections, message)
        self.version = version
        self.dataminer_collections = dataminer_collections
        self.message = message

    def __str__(self) -> str:
        return f"Failed to datamine {self.version} on {len(self.dataminer_collections)} Dataminers: [{", ".join(dataminer_collection.name for dataminer_collection in self.dataminer_collections)}]{message(self.message)}"

class DataminerUnrecognizedDependencyError(DataminerException):
    "A dependency does not exist."

    def __init__(self, dataminer:"Dataminer", dependency_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer attempting to access the dependency.
        :dependency_name: The name of the DataminerCollection that does not exist.
        :options: Values that `dependency_name` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, dependency_name, options, message)
        self.dataminer = dataminer
        self.dependency_name = dependency_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} references dependency \"{self.dependency_name}\" that is non-existent for this Version{message(self.message)}{nearest_message(self.dependency_name, self.options)}"

class DataminerUnrecognizedSuffixError(DataminerException):
    "A file suffix is unrecognized."

    def __init__(self, dataminer:"Dataminer", path:str, recognized_suffixes:list[str], message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that found the unrecognized suffix.
        :path: The path containing the unrecognized suffix.
        :recognized_suffixes: A list of suffixes that are recognized.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, path, recognized_suffixes, message)
        self.dataminer = dataminer
        self.path = path
        self.recognized_suffixes = recognized_suffixes
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} found unrecognized suffix on path \"{self.path}\"; it is not in {self.recognized_suffixes}{message(self.message, yes_message="; %s!")}"

class DataminerUnregisteredDependencyError(DataminerException):
    "The dependency exists, but is not listed as a dependency by this Dataminer."

    def __init__(self, dataminer:"Dataminer", dependency_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer attempting to access the dependency.
        :dependency_name: The name of the DataminerCollection that is unregistered.
        :options: Values that `dependency_name` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, dependency_name, options, message)
        self.dataminer = dataminer
        self.dependency_name = dependency_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} references unlisted dependency \"{self.dependency_name}\"{message(self.message)}{nearest_message(self.dependency_name, self.options)}"

class MissingDataFileError(DataminerException):
    "The data file for this DataminerCollection is missing."

    def __init__(self, dataminer:"Dataminer|DataminerSettings|AbstractDataminerCollection", file_name:str, version:Optional["Version"], message:Optional[str]=None) -> None:
        '''
        :dataminer_collection: The Dataminer, DataminerSettings, or DataminerCollection that is missing its file.
        :file_name: The name of the file that's missing.
        :version: The Version for which this Dataminer is missing its file.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, version, file_name, message)
        self.dataminer = dataminer
        self.version = version
        self.file_name = file_name
        self.message = message

    def __str__(self) -> str:
        return f"File {self.file_name} of {self.dataminer}{message(self.version, "", " of Version \"%s\"", lambda version: version.name)} is missing{message(self.message)}"

class NullDataminerMethodError(DataminerException):
    "An invalid exception has been called on a NullDataminer."

    def __init__(self, dataminer:"NullDataminer", method:Callable, message:Optional[str]=None) -> None:
        '''
        :dataminer: The NullDataminer that an invalid method was called on.
        :method: The method that was called on the NullDataminer.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, method, message)
        self.dataminer = dataminer
        self.method = method
        self.message = message

    def __str__(self) -> str:
        return f"Attemtped to call method \"{self.method.__name__}\" on {self.dataminer}{message(self.message)}"

class TagSearcherDependencyError(DataminerException):
    "A tag exists in a Dataminer that is not a dependency of this one."

    def __init__(self, dataminer:"Dataminer", tag:"StructureTag", dataminer_collection:"AbstractDataminerCollection", message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that attempted to access the tag.
        :tag: The tag that was found in an inaccessible DataminerCollection.
        :dataminer_collection: The DataminerCollection the tag was found in.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, tag, dataminer_collection, message)
        self.dataminer = dataminer
        self.tag = tag
        self.dataminer_collection = dataminer_collection
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} could find {self.tag} in {self.dataminer_collection}, but it is not a dependency{message(self.message)}"

class TagSearcherParseError(DataminerException):
    "Failed to parse a TagSearcher expression."

    def __init__(self, data_reader:"DataReader", reason:str, message:Optional[str]=None) -> None:
        '''
        :data_reader: The DataReader object used to read the expression.
        :reason: The reason for the error.
        :message: Additional text to place after the main message.
        '''
        super().__init__(data_reader, reason, message)
        self.data_reader = data_reader
        self.reason = reason
        self.message = message

    def __str__(self) -> str:
        return f"{self.reason} at position {self.data_reader.position} of expression \"{self.data_reader.data}\"{message(self.message)}"

class DelegateException(Exception):
    "Abstract Exception class for errors relating to Delegates."

class InapplicableDelegateError(DelegateException):
    "The Structure or StructureBase a Delegate is applied to does not suit the Delegate."

    def __init__(
        self,
        delegate_type:type["Delegate"],
        structure:"Structure",
        allowed_types:tuple[type["Structure|None"], ...],
        message:Optional[str]=None,
    ) -> None:
        '''
        :delegate_type: The type of Delegate that is applied to the wrong type of Structure or StructureBase.
        :structure_type: The Structure or StructureBase that has the inapplicable Delegate applied to it.
        :allowed_types: The types of Structure or StructureBase that the Delegate is allowed to be applied to.
        :message: Additional text to place after the main message.
        '''
        super().__init__(delegate_type, structure, allowed_types, message)
        self.delegate_type = delegate_type
        self.structure = structure
        self.allowed_types = allowed_types
        self.message = message

    def __str__(self) -> str:
        return f"Delegate type \"{self.delegate_type.__name__}\" can only be applied to types [{", ".join(f"\"{allowed_type.__name__}\"" for allowed_type in self.allowed_types)}], not {self.structure}{message(self.message)}"

class LogException(Exception):
    "Abstract Exception class for errors relating to Logs."

class LogInvalidFileError(LogException):
    "Attempted to create a Log with an invalid file path."

    def __init__(self, log:"Log", path:Path, message:Optional[str]=None) -> None:
        '''
        :log: The Log with the invalid file path.
        :path: The invalid path.
        :message: Additional text to place after the main message.
        '''
        super().__init__(log, path, message)
        self.log = log
        self.path = path
        self.message = message

    def __str__(self) -> str:
        return f"The path of {self.log}, \"{self.path.as_posix()}\", is invalid{message(self.message)}"

class LogWriteTypeError(LogException):
    "Attempted to write to a Log with an invalid type for the Log's LogType."

    def __init__(self, log:"Log", write_type:type, allowed_types:tuple[type,...], message:Optional[str]=None) -> None:
        '''
        :log: The Log that attempted to write to.
        :write_type: The type that was given to `Log.write`.
        :allowed_types: The types that can be given to `Log.write`.
        :message: Additional text to place after the main message.
        '''
        super().__init__(log, write_type, allowed_types, message)
        self.log = log
        self.write_type = write_type
        self.allowed_types = allowed_types
        self.message = message

    def __str__(self) -> str:
        return f"Attempted to write to {self.log} using type \"{self.write_type.__name__}\" instead of types [{", ".join(f"\"{allowed_type.__name__}\"" for allowed_type in self.allowed_types)}]{message(self.message)}"

class DomainException(Exception):
    "Abstract Exception class for errors relating to Domains."

class LibFileNotFoundError(DomainException):
    "A lib file does not exist."

    def __init__(self, name:str, path:Path, options:list[str], message:Optional[str]=None) -> None:
        '''
        :name: The file name used to access the LibFiles.
        :path: The Path that was found using `name`.
        :options: Options that `name` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(name, path, options, message)
        self.name = name
        self.path = path
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Path \"{self.path.as_posix()}\", derived from \"{self.name}\", does not exist{message(self.message)}{nearest_message(self.name, self.options)}"

class LibFileWrongDirectoryError(DomainException):
    "Attempted to access a lib file that is not in the correct directory."

    def __init__(self, name:str, path:Path, correct_directory:Path, options:list[str], message:Optional[str]=None) -> None:
        '''
        :name: The file name used to access the LibFiles.
        :path: The Path that was found using `name`.
        :correct_directory: The Path that `path` should be a descendent of.
        :options: Options that `name` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(name, path, correct_directory, options, message)
        self.name = name
        self.path = path
        self.correct_directory = correct_directory
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Path derived from {self.name} should be a descendent of {self.correct_directory.as_posix()}, not {self.path.as_posix()}{message(self.message)}{nearest_message(self.name, self.options)}"

class ScriptException(Exception):
    "Abstract Exception class for errors relating to Scripts."

class ScriptNameCollideError(ScriptException):
    "A Script has the same stem as another Script in the same folder."

    def __init__(self, script_path1:Path, script_path2:Path, message:Optional[str]=None) -> None:
        '''
        :script_path1: The Path of the first Script.
        :script_path2: The Path of the second Script.
        :message: Additional text to place after the main message.
        '''
        super().__init__(script_path1, script_path2, message)
        self.script_path1 = script_path1
        self.script_path2 = script_path2
        self.message = message

    def __str__(self) -> str:
        return f"Scripts on paths \"{self.script_path1}\" and \"{self.script_path2}\" have the same stem{message(self.message)}"

class ScriptGeneralityError(ScriptException):
    "Cannot use a Script key because it could refer to multiple objects"

    def __init__(self, script_name:str, potential_meanings:list["Script"], options:list[str], message:Optional[str]=None) -> None:
        '''
        :script_name: The key used to access the ScriptSet.
        :potential_meanings: The Scripts that `script_name` could refer to.
        :options: Values this Script could have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(script_name, potential_meanings, options, message)
        self.script_name = script_name
        self.potential_meanings = potential_meanings
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Script name \"{self.script_name}\" could be referring to {self.potential_meanings}{message(self.message)}{nearest_message(self.script_name, self.options)}"

class UnrecognizedScriptDomainError(ScriptException):
    "An unrecognized Domain is referenced by a Script."

    def __init__(self, domain_name:str, key:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :domain_name: The name of the unrecognized Domain.
        :key: The key used to access the Script.
        :options: Values this Script could have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(domain_name, key, options, message)
        self.domain_name = domain_name
        self.key = key
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Domain \"{self.domain_name}\" in key \"{self.key}\" is unrecognized{message(self.message)}{nearest_message(self.key, self.options)}"

class UnrecognizedScriptError(ScriptException):
    "An unrecognized Script was referenced."

    def __init__(self, script_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :script_name: The name of the unrecognized script.
        :options: Values this Script could have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(script_name, options, message)
        self.script_name = script_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Unrecognized Script \"{self.script_name}\"{message(self.message)}{nearest_message(self.script_name, self.options)}"

class UnrecognizedScriptFileNameError(ScriptException):
    "A Script references a file that does not exist."

    def __init__(self, key:str, file_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :key: The key used to access the Script.
        :file_name: The unrecognized file name.
        :options: Values this Script could have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, file_name, options, message)
        self.key = key
        self.file_name = file_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Script file name \"{self.file_name}\"{f" from key \"{self.key}\"" if self.key != self.file_name else ""} is unrecognized{message(self.message)}{nearest_message(self.key, self.options)}"

class UnrecognizedScriptObjectNameError(ScriptException):
    "A Script references an object that does not exist in a file that does exist."

    def __init__(self, key:str, file_name:str, object_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :key: The key used to access the Script.
        :file_name: The recognized file name.
        :object_name: The unrecognized object name.
        :options: Values this Script could have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, file_name, object_name, options, message)
        self.key = key
        self.file_name = file_name
        self.object_name = object_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Scripted object \"{self.object_name}\" is unrecognized in recognized file \"{self.file_name}\"{message(self.message)}{nearest_message(self.key, self.options)}"

class WrongScriptError(ScriptException):
    "Attempted to import a Script that exists, but cannot be used in this situation."

    def __init__(self, key:str, script:"Script", type_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :key: The key used to access the Script.
        :script: The Script that cannot be used in this situation.
        :type_name: A string representing the type the ScriptSet should be referencing.
        :options: Values this Script could have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, script, options, message)
        self.key = key
        self.script = script
        self.type_name = type_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Cannot load {self.script} from \"{self.key}\" in this situation; should be {self.type_name}{message(self.message)}{nearest_message(self.key, self.options)}"

class WrongScriptFileError(ScriptException):
    "Attempted to import a Script file that exists, but cannot be used in this situation."

    def __init__(self, key:str, file_name:str, type_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :key: The key used to access the Script.
        :file_name: The file name of the Script that cannot be used in this situation.
        :type_name: A string representing the type the ScriptSet should be referencing.
        :options: Values this Script could have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, file_name, options, message)
        self.key = key
        self.file_name = file_name
        self.type_name = type_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Cannot load any Script in \"{self.file_name}\" from \"{self.key}\" in this situation; should be {self.type_name}{message(self.message)}{nearest_message(self.key, self.options)}"

class SerializerException(Exception):
    "Abstract Exception class for errors relating to Serializers"

class FileWrongSerializerError(SerializerException):
    "A File cannot be read with the given Serializer."

    def __init__(self, file:"AbstractFile", serializers:list["Serializer|None"], serializer:"Serializer|None", message:Optional[str]=None) -> None:
        '''
        :file: The File without the correct Serializer.
        :serializers: The Serializers that the File does have.
        :serializer: The Serializer used to access the File.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file, serializers, serializer, message)
        self.file = file
        self.serializers = serializers
        self.serializer = serializer
        self.message = message

    def __str__(self) -> str:
        return f"{self.file} cannot be read with {self.serializer} because {"it has not been read yet" if len(self.serializers) == 0 else f"it can only be read by [{", ".join(repr(serializer) for serializer in self.serializers)}]"}{message(self.message)}"

class SerializerEllipsisError(SerializerException):
    "A Serializer returned an Ellipsis object."

    def __init__(self, file:"AbstractFile", serializer:"Serializer|None", message:Optional[str]=None) -> None:
        '''
        :file: The File that was read using the Serializer.
        :serializer: The Serializer that returned an Ellipsis object.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file, serializer, message)
        self.file = file
        self.serializer = serializer
        self.message = message

    def __str__(self) -> str:
        if self.serializer is None:
            return f"Attempted to set a the data of {self.file} to an Ellipsis{message(self.message)}"
        else:
            return f"{self.serializer} returned an Ellipsis while deserializing {self.file}{message(self.message)}"

class SerializationFailureError(SerializerException):
    "A Serializer failed to serialize."

    def __init__(self, serializer:"Serializer", file_name:str, message:Optional[str]=None) -> None:
        '''
        :serializer: The Serializer that failed to serialize.
        :file_name: The name of the File that failed to be serialized.
        :message: Additional text to place after the main message.
        '''
        super().__init__(serializer, file_name, message)
        self.serializer = serializer
        self.file_name = file_name
        self.message = message

    def __str__(self) -> str:
        return f"{self.serializer} failed to serialize file \"{self.file_name}\"{message(self.message)}"

class SerializerMethodNonexistentError(SerializerException):
    "A Serializer's method does not exist and was called."

    def __init__(self, serializer:"Serializer", method:Callable, message:Optional[str]=None) -> None:
        '''
        :serializer: The Serializer missing a method.
        :method: The method that was called and is missing.
        :message: Additional text to place after the main message.
        '''
        super().__init__(serializer, method, message)
        self.serializer = serializer
        self.method = method
        self.message = message

    def __str__(self) -> str:
        return f"{self.serializer} is missing method {self.method.__name__}{message(self.message)}"

class SerializerNoneError(SerializerException):
    "Attempted to read a File without using a Serializer."

    def __init__(self, file:"File", message:Optional[str]=None) -> None:
        '''
        :file: The File that was read without a Serializer.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file, message)
        self.file = file
        self.message = message

    def __str__(self) -> str:
        return f"Attempted to read non-fake File {self.file} without a Serializer{message(self.message)}"

class StructureException(Exception):
    "Abstract Exception class for errors relating to Structures"

class ConditionStructureFilterError(StructureException):
    "A ConditionStructure encountered StructureInfo that fits none of its filters."

    def __init__(self, structure:"Structure", structure_info:"StructureInfo", message:Optional[str]=None) -> None:
        '''
        :structure: The Structure that encountered StructureInfo that fits none of its filters.
        :structure_info: The StructureInfo that fits no filter.
        :message: Additional text to place after the main message.
        '''
        self.structure = structure
        self.structure_info = structure_info
        self.message = message

    def __str__(self) -> str:
        return f"{self.structure} encountered {self.structure_info}, which passes no filter{message(self.message)}"

class DataPathEmbeddedDataError(StructureException):
    "A DataPath has no embedded data but should."

    def __init__(self, data_path:"DataPath", message:Optional[str]=None) -> None:
        '''
        :data_path: The DataPath without embedded data.
        :message: Additional text to place after the main message.
        '''
        super().__init__(data_path, message)
        self.data_path = data_path
        self.message = message

    def __str__(self) -> str:
        return f"{self.data_path} has no embedded data{message(self.message)}"

class SwitchStructureError(StructureException):
    "A SwitchStructure's switch function returned a value that is not in its switches."

    def __init__(self, return_value:str, options:list[str], switch_structure:"Structure", message:Optional[str]=None) -> None:
        '''
        :return_value: The value that the SwitchStructure's switch function returned.
        :options: The values that the SwitchStructure expects the return value to be.
        :switch_structure: The SwitchStructure.
        :message: Additional text to place after the main message.
        '''
        super().__init__(return_value, options, switch_structure, message)
        self.return_value = return_value
        self.options = options
        self.switch_structure = switch_structure
        self.message = message

    def __str__(self) -> str:
        return f"{self.switch_structure}'s switch function returned \"{self.return_value}\", which is not in [{", ".join(f"\"{value}\"" for value in self.options)}]{message(self.message)}{nearest_message(self.return_value, self.options)}"

class InvalidFileHashType(StructureException):
    "An is_file StructureTag references data that cannot be interpreted as a file hash."

    def __init__(self, version:"Version", structure_tag:"StructureTag", data_path:"DataPath", message:Optional[str]=None) -> None:
        '''
        :version: The Version that has the invalid file hash.
        :structure_tag: The StructureTag that has the invalid file hash.
        :data_path: The DataPath whose embedded data is an invalid file hash.
        '''
        super().__init__(version, structure_tag, data_path, message)
        self.version = version
        self.structure_tag = structure_tag
        self.data_path = data_path
        self.message = message

    def __str__(self) -> str:
        return f"Data {self.data_path.embedded_data} at path {self.data_path} of {self.structure_tag} of {self.version} is not a valid file hash{message(self.message)}"

class NormalizerEllipsisError(StructureException):
    "A Normalizer returned Ellipsis."

    def __init__(self, normalizer:"Normalizer", message:Optional[str]=None) -> None:
        super().__init__(normalizer, message)
        self.normalizer = normalizer
        self.message = message

    def __str__(self) -> str:
        return f"{self.normalizer} returned Ellipsis{message(self.message)}"

class SequenceTooLongError(StructureException):
    "A StringStructure or SequenceStructure cannot compare or get similarity of data because it is too long."

    def __init__(self, structure:"Structure", len1:int, len2:int, message:Optional[str]=None) -> None:
        '''
        :structure: The StringStructure or SequenceStructure with the too-long data.
        :len1: The length of the first data.
        :len2: The length of the second data.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure, len1, len2, message)
        self.structure = structure
        self.len1 = len1
        self.len2 = len2
        self.message = message

    def __str__(self) -> str:
        return f"{self.structure} attempted to compare/get similarity of data too long: first is {self.len1} long; second is {self.len2} long{message(self.message)}"

class StructuresCompareFailureError(StructureException):
    "Multiple Structures failed to compare."

    def __init__(self, structure_names:list[str], message:Optional[str]=None) -> None:
        '''
        :structure_names: The names of the Structures that failed to compare.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure_names, message)
        self.structure_names = structure_names
        self.message = message

    def __str__(self) -> str:
        return f"Failed to compare on DataminerCollections [{", ".join(self.structure_names)}] (len {len(self.structure_names)}){message(self.message)}"

class StructureCannotPrintFlatError(StructureException):
    "Some data cannot be printed on a single line."

    def __init__(self, message:Optional[str]=None) -> None:
        '''
        :message: Additional text to place after the main message.
        '''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Data cannot be printed flat{message(self.message)}"

class StructureError(StructureException):
    "A StructureBase has failed."

    def __init__(self, structure_base:"Structure", message:Optional[str]=None) -> None:
        '''
        :structure_base: The StructureBase that failed.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure_base, message)
        self.structure_base = structure_base
        self.message = message

    def __str__(self) -> str:
        return f"{self.structure_base} has failed{message(self.message)}"

class StructureNoManipulationFunctionError(StructureException):
    "In order to normalize a type a certain way, it must have a certain TypeStuff function, but does not."

    def __init__(self, function_name:str, data_type:type, message:Optional[str]=None) -> None:
        '''
        :function_name: The name of the function the TypeStuff should have, such as "setitem" or "popitem".
        :data_type: The type that the TypeStuff does not know about.
        :message: Additional text to place after the main message.
        '''
        super().__init__(function_name, data_type, message)
        self.function_name = function_name
        self.data_type = data_type
        self.message = message

    def __str__(self) -> str:
        return f"Type {self.data_type} does not have a {self.function_name} method{message(self.message)}"

class StructureRequiredKeyMissingError(StructureException):
    "A required key is missing."

    def __init__(self, structure:"Structure", key:Any, message:Optional[str]=None) -> None:
        '''
        :structure: The Structure that should have the key.
        :key: The required key that is missing from the data.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure, key, message)
        self.structure = structure
        self.key = key
        self.message = message

    def __str__(self) -> str:
        return f"Required key \"{self.key}\" from {self.structure} is missing{message(self.message)}"

class StructureTypeError(StructureException):
    "Data given to a Structure has the wrong type."

    def __init__(self, required_types:tuple[type,...], actual_type:type, label:str, message:Optional[str]=None) -> None:
        '''
        :required_types: The types that the value should be.
        :actual_type: The actual type of the data tested.
        :label: The uppercase text to label the value with.
        :message: Additional text to place after the main message.
        '''
        super().__init__(required_types, actual_type, label, message)
        self.required_types = required_types
        self.actual_type = actual_type
        self.label = label
        self.message = message

    def __str__(self) -> str:
        return f"{self.label} must have a type of one of [{", ".join(f"\"{required_type.__name__}\"" for required_type in self.required_types)}], not \"{self.actual_type.__name__}\"{message(self.message)}"

class StructureUnrecognizedKeyError(StructureException):
    "A key in some data is not a recognized key."

    def __init__(self, unrecognized_key:Any, label:str="Key", message:Optional[str]=None) -> None:
        '''
        :unrecognized_key: The key that is unrecognized.
        :label: The uppercase text to label the key with.
        :message: Additional text to place after the main message.
        '''
        super().__init__(unrecognized_key, label, message)
        self.unrecognized_key = unrecognized_key
        self.label = label
        self.message = message

    def __str__(self) -> str:
        return f"{self.label} \"{self.unrecognized_key}\" is not recognized{message(self.message)}"

class UnrecognizedStructureTagError(StructureException):
    "A StructureTag referenced in a tag expression does not exist."

    def __init__(self, expression:str, tag_name:str, options:list[str], message:Optional[str]=None) -> None:
        '''
        :expression: The tag expression containing the unrecognized StructureTag.
        :tag_name: The name of the unrecognized StructureTag.
        :options: Values that `tag_name` could be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(expression, tag_name, options, message)
        self.expression = expression
        self.tag_name = tag_name
        self.options = options
        self.message = message

    def __str__(self) -> str:
        return f"Unrecognized tag \"{self.tag_name}\" referenced in expression \"{self.expression}{message(self.message)}{nearest_message(self.tag_name, self.options)}"

class ZeroWeightError(StructureException):
    "The sum of the key weight and value weight for a Structure may be 0!"

    def __init__(self, key_weight_path:str, value_weight_path:str, message:Optional[str]=None) -> None:
        '''
        :key_weight_path: A string representing the key path from the Structure to the key weight.
        :value_weight_path: A string representing the key path from the Structure to the value weight.
        :message: Additional text to place after the main message
        '''
        self.key_weight_path = key_weight_path
        self.value_weight_path = value_weight_path
        self.message = message
        super().__init__(key_weight_path, value_weight_path, message)

    def __str__(self) -> str:
        return f"The sum of {self.key_weight_path} and {self.value_weight_path} is 0{message(self.message)}"

class TablifierException(Exception):
    "Abstract Exception class for errors relating to Tablifiers."

class TablifierError(StructureException):
    "A Tablifier has failed."

    def __init__(self, tablifier:"Tablifier", message:Optional[str]=None) -> None:
        '''
        :tablifier: The Tablifier that failed.
        :message: Additional text to place after the main message.
        '''
        super().__init__(tablifier, message)
        self.tablifier = tablifier
        self.message = message

    def __str__(self) -> str:
        return f"{self.tablifier} has failed{message(self.message)}"

class TypeVerifierException(Exception):
    "Abstract Exception class for errors relating to TypeVerifiers."

class TypedDictTypeVerifierKeysOverlapError(TypeVerifierException):
    "Attempted to extend a TypedDictTypeVerifier with another TypedDictTypeVerifier that shares its same keys!"

    def __init__(self, type_verifier:"TypedDictTypeVerifier", other:"TypedDictTypeVerifier", keys_overlap:list[str]) -> None:
        super().__init__(type_verifier, other, keys_overlap)
        self.type_verifier = type_verifier
        self.other = other
        self.keys_overlap = keys_overlap

    def __str__(self) -> str:
        return f"Cannot combine {self.other} into {self.type_verifier} because they share these keys: {self.keys_overlap}!"

class TypeVerificationFailedError(TypeVerifierException):
    "Type verification failed."

    def __init__(self, type_verifier:"TypeVerifier", message:Optional[str]=None) -> None:
        '''
        :type_verifier: The base TypeVerifier on which base_verify was called.
        :message: Additional text to place after the main message.
        '''
        super().__init__(type_verifier, message)
        self.type_verifier = type_verifier
        self.message = message

    def __str__(self) -> str:
        return f"{self.type_verifier} failed verification{message(self.message)}"

class TypeVerificationTypeException(TypeVerifierException):
    "Abstract Exception class for errors that are passed around by TypeVerifiers."
    ...

class TypeVerificationEnumError(TypeVerificationTypeException):

    def __init__(self, options:Container, value:Any) -> None:
        super().__init__(options, value)
        self.options = options
        self.value = value

    def __str__(self) -> str:
        return f"The data is not one of {self.options}, but instead {self.value}"

class TypeVerificationFunctionError(TypeVerificationTypeException):

    def __init__(self, message:str|None) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"The data failed verification{message(self.message, yes_message=" due to \"%s\"!")}"

class TypeVerificationMissingKeyError(TypeVerificationTypeException):

    def __init__(self, key:str) -> None:
        super().__init__(key)
        self.key = key

    def __str__(self) -> str:
        return f"Required key \"{self.key}\" is missing!"

class TypeVerificationTypeError(TypeVerificationTypeException):

    def __init__(self, expected_type:str, observed_type:type) -> None:
        super().__init__(expected_type, observed_type)
        self.expected_type = expected_type
        self.observed_type = observed_type

    def __str__(self) -> str:
        return f"The data is not {self.expected_type}, but instead {self.observed_type.__name__}!"

class TypeVerificationUnionError(TypeVerificationTypeException):

    def __init__(self, expected_type:str, observed_type:type, count:int) -> None:
        super().__init__(expected_type, observed_type)
        self.expected_type = expected_type
        self.observed_type = observed_type
        self.count = count

    def __str__(self) -> str:
        return f"The data is not {self.expected_type}, but instead {self.observed_type.__name__} due to {self.count} above exception(s)!"

class TypeVerificationUnrecognizedKeyError(TypeVerificationTypeException):

    def __init__(self, key:str, options:list[str]) -> None:
        super().__init__(key, options)
        self.key = key
        self.options = options

    def __str__(self) -> str:
        return f"\"{self.key}\" is an unrecognized key!{nearest_message(self.key, self.options)}"

class VersionException(Exception):
    "Abstract Exception class for errors relating to Versions."

class DuplicateVersionTagOrderError(VersionException):
    "There are two VersionTags with the same name in VersionTagOrder"

    def __init__(self, tag:"VersionTag", key:str|tuple[str,...], message:Optional[str]=None) -> None:
        '''
        :tag: The VersionTag that is dulicated.
        :key: The key(s) in version_tags_order.json that has the duplicate VersionTag.
        :message: Additional text to place after the main message.
        '''
        super().__init__(tag, key, message)
        self.tag = tag
        self.key = key
        self.message = message

    def __str__(self) -> str:
        return f"{self.tag} is duplicated in {f"keys [{", ".join(f"\"{key}\"" for key in self.key)}]" if isinstance(self.key, tuple) else f"key \"{self.key}\""} of VersionTagOrder{message(self.message)}"

class InvalidParentVersionError(VersionException):
    "A Version has an invalid parent Version."

    def __init__(self, version:"Version", parent:"Version", message:Optional[str]=None) -> None:
        '''
        :version: The Version with an invalid parent Version.
        :parent: The parent of this Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, parent, message)
        self.version = version
        self.parent = parent
        self.message = message

    def __str__(self) -> str:
        return f"{self.version} has an invalid parent {self.parent}{message(self.message)}"

class InvalidVersionTimeError(VersionException):
    "A Version has an invalid time."

    def __init__(self, version:"Version", time:date|datetime, reason:str, message:Optional[str]=None) -> None:
        '''
        :version: The Version with an invalid time.
        :time: The time that is invalid.
        :reason: Why the time is invalid.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, time, reason, message)
        self.version = version
        self.time = time
        self.reason = reason
        self.message = message

    def __str__(self) -> str:
        return f"{self.version} has an invalid time {self.time} because {self.reason}{message(self.message)}"

class NoOrderVersionTagsFoundError(VersionException):
    "No ordering VersionTags were found."

    def __init__(self, version:"Version", version_tags:Sequence["VersionTag"], message:Optional[str]=None) -> None:
        '''
        :version: The Version with no ordering tags.
        :version_tags: The list of VersionTags containing no ordering tags.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, version_tags, message)
        self.version = version
        self.version_tags = version_tags
        self.message = message

    def __str__(self) -> str:
        return f"No ordering tags found with {self.version}'s tags: {self.version_tags}{message(self.message)}"

class NotAllOrderTagsUsedError(VersionException):
    "Not all ordering VersionTags were used."

    def __init__(self, tag:"VersionTag", key:str|tuple[str,...], message:Optional[str]=None) -> None:
        '''
        :tag: The VersionTag that is missing.
        :key: Which key(s) in version_tags_order.json has a missing VersionTag.
        :message: Additional text to place after the main message.
        '''
        super().__init__(tag, key, message)
        self.tag = tag
        self.key = key
        self.message = message

    def __str__(self) -> str:
        return f"{self.tag} was not used in {f"keys [{", ".join(f"\"key\"" for key in self.key)}]" if isinstance(self.key, tuple) else f"key \"{self.key}\""} of VersionTagOrder{message(self.message)}"

class NotAnOrderTagError(VersionException):
    "The VersionTag is not an ordering tag."

    def __init__(self, tag:"VersionTag", message:Optional[str]=None) -> None:
        '''
        :tag: The VersionTag that is not an ordering tag.
        :message: Additional text to place after the main message.
        '''
        super().__init__(tag, message)
        self.tag = tag
        self.message = message

    def __str__(self) -> str:
        return f"{self.tag} is not an ordering tag{message(self.message)}"

class UnreleasedDownloadableVersionError(VersionException):
    "A Version has the unreleased tag and has a method for downloading."

    def __init__(self, version:"Version", version_file:"VersionFile", message:Optional[str]=None) -> None:
        '''
        :version: The Version with an unreleased tag and a method for downloading.
        :version_file: The VersionFile that cannot exist when the Version is unreleased.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, message)
        self.version = version
        self.version_file = version_file
        self.message = message

    def __str__(self) -> str:
        return f"{self.version_file} cannot exist when {self.version} is unreleased{message(self.message)}"

class VersionChildError(VersionException):
    "The parent Version's ordering tag and child Version's ordering tag cannot go together."

    def __init__(self, parent_version:"Version", parent_tag:"VersionTag", child_version:"Version", child_tag:"VersionTag", message:Optional[str]=None) -> None:
        '''
        :parent_version: The parent Version.
        :parent_tag: The ordering VersionTag of the parent Version.
        :child_version: The child Version.
        :child_tag: The ordering VersionTag of the child Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(parent_version, parent_tag, child_version, child_tag, message)
        self.parent_version = parent_version
        self.parent_tag = parent_tag
        self.child_version = child_version
        self.child_tag = child_tag
        self.message = message

    def __str__(self) -> str:
        return f"{self.child_version} (tag {self.child_tag}), child of {self.parent_version} (tag {self.parent_tag}) is not a valid child type of a {self.parent_tag}{message(self.message)}"

class VersionChildOfMultipleTopLevelVersionsError(VersionException):
    "The Version is a child of multiple top-level Versions."

    def __init__(self, version:"Version", message:Optional[str]=None) -> None:
        '''
        :version: The Version that is a child of multiple top-level Versions.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, message)
        self.version = version
        self.message = message

    def __str__(self) -> str:
        return f"{self.version} is a child of multiple top-level Versions{message(self.message)}"

class VersionChildOrderError(VersionException):
    "The Version's children are in an invalid order."

    def __init__(self, version:"Version", child_tags:list["VersionTag"], error_child:"Version", message:Optional[str]=None) -> None:
        '''
        :version: The Version with children in an invalid order.
        :child_tags: The ordering VersionTags of each of the Version's children.
        :error_child: The Version child at which the order is invalid.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, child_tags, error_child, message)
        self.version = version
        self.child_tags = child_tags
        self.error_child = error_child
        self.message = message

    def __str__(self) -> str:
        return f"The children of {self.version}, [{", ".join(child_tag.name for child_tag in self.child_tags)}], are in an invalid order at child {self.error_child}{message(self.message)}"

class VersionOrderingTagsError(VersionException):
    "The Version has none or too many ordering VersionTags."

    def __init__(self, version:"Version", count:int, tags:Sequence["VersionTag"], message:Optional[str]=None) -> None:
        '''
        :version: The Version that has an invalid number of ordering VersionTags.
        :count: The number of ordering VersionTags this Version has.
        :tags: The list of VersionTags that this Version does have.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, count, tags, message)
        self.version = version
        self.count = count
        self.tags = tags
        self.message = message

    def __str__(self) -> str:
        return f"{self.version} {"lacks" if self.count == 0 else "has too many"} ordering VersionTags; has [{", ".join(tag.name for tag in self.tags)}]{message(self.message)}"

class VersionOrderSequenceError(VersionException):
    "A Version is before or after a tag that it shouldn't be."

    def __init__(self, parent_version:"Version", parent_tag:"VersionTag", child_version:"Version", child_tag:"VersionTag", time_text:Literal["before", "after"], message:Optional[str]=None) -> None:
        '''
        :parent_version: The parent Version.
        :parent_tag: The ordering VersionTag of the parent Version.
        :child_version: The child Version.
        :child_tag: The ordering VersionTag of the child Version.
        :time_text: The actual relationship the child has to its parent.
        :message: Additional text to place after the main message.
        '''
        super().__init__(parent_version, parent_tag, child_version, child_tag, time_text, message)
        self.parent_version = parent_version
        self.parent_tag = parent_tag
        self.child_version = child_version
        self.child_tag = child_tag
        self.time_text = time_text
        self.message = message

    def __str__(self) -> str:
        return f"Child {self.child_version} (tag {self.child_tag}) of {self.parent_version} (tag {self.parent_tag}) comes {self.time_text} the latter{message(self.message)}"

class VersionOutOfRangeError(VersionException):
    "The Version is not in a VersionRange."

    def __init__(self, version:"Version", version_range:Optional["VersionRange"]=None, message:Optional[str]=None) -> None:
        '''
        :version: The Version that is not within the VersionRange.
        :version_range: The VersionRange that the Version does not fall within.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, version_range, message)
        self.version = version
        self.version_range = version_range
        self.message = message

    def __str__(self) -> str:
        return f"Version {self.version} is not within the VersionRange{message(self.version_range, "", "%r")}{message(self.message)}"

class VersionRangeOrderError(VersionException):
    "The old and new Versions of a VersionRange are switched."

    def __init__(
        self,
        version_range:"VersionRange",
        start_version:"Version|VersionComponent",
        stop_version:"Version|VersionComponent",
        message:Optional[str]=None
    ) -> None:
        '''
        :version_range: The VersionRange with switched Versions.
        :start_version: The start Version that is newer than the stop Version.
        :stop_version: The stop Version that is older than the start Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_range, start_version, stop_version, message)
        self.version_range = version_range
        self.start_version = start_version
        self.stop_version = stop_version
        self.message = message

    def __str__(self) -> str:
        return f"The Versions of {self.version_range}, {self.start_version} (start) and {self.stop_version} (stop), are switched{message(self.message)}"

class VersionTagExclusivePropertyError(VersionException):
    "A VersionTag has properties that are mutually exclusive."

    def __init__(self, property1:str, property2:str, message:Optional[str]=None) -> None:
        '''
        :property1: The name of the first mutually exclusive property.
        :property2: The name of the second mutually exclusive property.
        :message: Additional text to place after the main message.
        '''
        super().__init__(property1, property2, message)
        self.property1 = property1
        self.property2 = property2
        self.message = message

    def __str__(self) -> str:
        return f"Cannot have both {self.property1} and {self.property2}{message(self.message)}"

class VersionTimeTravelError(VersionException):
    "A Version's children are not in order chronologically."

    def __init__(self, previous_child:"Version", previous_time:datetime, current_child:"Version", current_time:datetime, parent:"Version", message:Optional[str]=None) -> None:
        '''
        :previous_child: The child earlier in the children but chronologically after the current child.
        :previous_time: The time of the previous child.
        :current_child: The child after in the children but chronologically before the previous child.
        :current_time: The time of the current child.
        :parent: The parent Version of the previous and current children.
        :message: Additional text to place after the main message.
        '''
        super().__init__(previous_child, previous_time, current_child, current_time, parent, message)
        self.previous_child = previous_child
        self.previous_time = previous_time
        self.current_child = current_child
        self.current_time = current_time
        self.parent = parent
        self.message = message

    def __str__(self) -> str:
        return f"Date of child {self.previous_child} ({self.previous_time}) comes after date of child {self.current_child} ({self.current_time}) despite being before it in the children of {self.parent}{message(self.message)}"

class VersionTimezoneError(VersionException):
    "A Version has no timezone in its time but should."

    def __init__(self, version:"Version", time:datetime, version_with_timezone:"Version", timezone_time:datetime, message:Optional[str]=None) -> None:
        '''
        :version: The Version without timezone info.
        :time: The time of the Version.
        :version_with_timezone: The Version with a timezone
        :timezone_time: The time with a timezone.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, time, version_with_timezone, timezone_time, message)
        self.version = version
        self.time = time
        self.version_with_timezone = version_with_timezone
        self.timezone_time = timezone_time
        self.message = message

    def __str__(self) -> str:
        return f"{self.version}'s time, {self.time.isoformat()} does not have a timezone but should because {self.version_with_timezone}'s time, {self.timezone_time.isoformat()}, does have a timezone{message(self.message)}"

class VersionTopLevelError(VersionException):
    "A Version is a top-level Version but has no top-level VersionTag."

    def __init__(self, version:"Version", top_level_tag:"VersionTag", message:Optional[str]=None) -> None:
        '''
        :version: The top-level Version missing the top-level VersionTag.
        :top_level_tag: The top-level VersionTag.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, top_level_tag, message)
        self.version = version
        self.top_level_tag = top_level_tag
        self.message = message

    def __str__(self) -> str:
        return f"{self.version} is a top-level Version, but does not have the top-level {self.top_level_tag}{message(self.message)}"

class VersionFileException(Exception):
    "Abstract Exception class for errors relating to VersionFiles or VersionFileTypes."

class RequiredVersionFileTypeMissingError(VersionFileException):
    "A requied VersionFileType is not present."

    def __init__(self, file_type:"VersionFileType", version:"Version", message:Optional[str]=None) -> None:
        '''
        :file_type: The VersionFileType that is required but missing.
        :version: The Version that is missing the VersionFileType.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_type, version, message)
        self.file_type = file_type
        self.version = version
        self.message = message

    def __str__(self) -> str:
        return f"Required {self.file_type} is missing in {self.version}{message(self.message)}"

class VersionFileInvalidAccessorError(VersionFileException):
    "The VersionFile has an invalid Accessor."

    def __init__(self, version_file:"VersionFile", accessor_str:str, message:Optional[str]=None) -> None:
        '''
        :version_file: The VersionFile with an invalid Accessor.
        :accessor_str: The name of the Accessor.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_file, accessor_str, message)
        self.version_file = version_file
        self.accessor_str = accessor_str
        self.message = message

    def __str__(self) -> str:
        return f"{self.version_file} does not recognize Accessor \"{self.accessor_str}\"{message(self.message)}"

class VersionFileNoAccessorsError(VersionFileException):
    "The VersionFile has no Accessors."

    def __init__(self, version_file:"VersionFile", message:Optional[str]=None) -> None:
        '''
        :version_file: The VersionFile with no available Accessors.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_file, message)
        self.version_file = version_file
        self.message = message

    def __str__(self) -> str:
        return f"{self.version_file} has no available Accessors{message_bool(self.version_file.has_accessors(), "", lambda: f" from [{", ".join(repr(accessor) for accessor in self.version_file.accessors)}]")}{message(self.message)}"
