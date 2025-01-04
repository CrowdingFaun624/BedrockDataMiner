import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Container, Literal, Optional

if TYPE_CHECKING:
    import Component.Capabilities as Capabilities
    import Component.Component as Component
    import Component.ComponentTyping as ComponentTyping
    import Component.Field.Field as Field
    import Component.ImporterEnvironment as ImporterEnvironment
    import Component.Pattern as Pattern
    import Component.Structure.BaseComponent as BaseComponent
    import Component.Version.Field.VersionRangeField as VersionRangeField
    import Component.Version.VersionComponent as VersionComponent
    import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
    import Dataminer.BuiltIns.TagSearcherDataminer as TagSearcherDataminer
    import Dataminer.Dataminer as Dataminer
    import Dataminer.DataminerEnvironment as DataminerEnvironment
    import Dataminer.DataminerSettings as DataminerSettings
    import Downloader.Accessor as Accessor
    import Serializer.Serializer as Serializer
    import Structure.DataPath as DataPath
    import Structure.Delegate.Delegate as Delegate
    import Structure.Difference as D
    import Structure.Normalizer as Normalizer
    import Structure.Structure as Structure
    import Structure.StructureBase as StructureBase
    import Structure.StructureEnvironment as StructureEnvironment
    import Structure.StructureSet as StructureSet
    import Structure.StructureTag as StructureTag
    import Structure.Trace as Trace
    import Utilities.Cache as Cache
    import Utilities.DataFile as DataFile
    import Utilities.File as File
    import Utilities.Log as Log
    import Utilities.Scripts as Scripts
    import Utilities.TypeUtilities as TypeUtilities
    import Utilities.TypeVerifier as TypeVerifier
    import Version.Version as Version
    import Version.VersionFile as VersionFile
    import Version.VersionFileType as VersionFileType
    import Version.VersionRange as VersionRange
    import Version.VersionTag.VersionTag as VersionTag

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

class CannotStringifyError(Exception):
    "Attempted to stringify an invalid object."

    def __init__(self, object_type:type, message:Optional[str]=None) -> None:
        '''
        :object_type: The type of the object that cannot be stringified.
        :message: Additional text to place after the main message.
        '''
        super().__init__(object_type, message)
        self.object_type = object_type
        self.message = message

    def __str__(self) -> str:
        return f"Attempted to stringify an object of type \"{self.object_type}\"{message(self.message)}"

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

class InvalidFileLocationError(Exception):
    "A file is not in the correct directory."

    def __init__(self, file_location:Path, required_directory:Path, message:Optional[str]=None) -> None:
        '''
        :file_location: The Path that is not in the correct directory.
        :required_directory: The directory `file_location` must be a descendent of.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_location, required_directory, message)
        self.file_location = file_location
        self.required_directory = required_directory
        self.message = message

    def __str__(self) -> str:
        return f"Path \"{self.file_location.as_posix()}\" is not in directory \"{self.required_directory}\"{message(self.message)}"

class InvalidStateError(Exception):
    "The program has reached an assumedly unreachable part of the code."

    def __str__(self) -> str:
        return f"Invalid state{message(self.args, yes_message=": %s!")}"

class AccessorException(Exception):
    "Abstract Exception class for errors relating to Accessors."

class DownloadAccessorFailError(AccessorException):
    "A DownloadAccessor failed to download a file."

    def __init__(self, accessor:"Accessor.Accessor", url:str, file:Optional[str]=None, message:Optional[str]=None) -> None:
        '''
        :accessor: The Accessor that failed to download a file.
        :url: The url from which the file comes from.
        :file: The name of the file that could not be downloaded.
        :message: Additional text to place after the main message.
        '''
        super().__init__(accessor, url, file, message)
        self.accessor = accessor
        self.url = url
        self.file = file
        self.message = message

    def __str__(self) -> str:
        return f"{self.accessor} failed to download file{message(self.file, "", " \"%s\"")} from \"{self.url}\"{message(self.message)}"

class UnrecognizedAccessorClassError(AccessorException):
    "An AccessorType is not recognized."

    def __init__(self, accessor_class_str:str, source:Optional[object]=None, source_str:Optional[str]=None, message:Optional[str]=None) -> None:
        '''
        :accessor_class_str: The name of the unrecognized Accessor class.
        :source: The object that attempts to reference the unrecognized AccessorType; may be empty.
        :source_str: A string describing the object that attempts to reference the unrecognized AccessorType; may be empty.
        :message: Additional text to place after the main message.
        '''
        super().__init__(accessor_class_str, source, source_str, message)
        self.accessor_class_str = accessor_class_str
        self.source = source
        self.source_str = source_str
        self.message = message

    def __str__(self) -> str:
        return f"Accessor class \"{self.accessor_class_str}\"{f", as referenced by {self.source if self.source_str is None else self.source_str}," if not (self.source is None and self.source_str is None) else ""} does not exist{message(self.message)}"

class UnrecognizedAccessorError(AccessorException):
    "The Accessor string is not recognized."

    def __init__(self, accessor_str:str, source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :accessor_str: The Accessor string that does not correspond to any Accessor.
        :source: The object attempting to reference this Accessor.
        :message: Additional text to place after the main message.
        '''
        super().__init__(accessor_str, source, message)
        self.source = source
        self.accessor_str = accessor_str
        self.message = message

    def __str__(self) -> str:
        return f"Accessor \"{self.accessor_str}\"{message(self.source, "", ", as referenced by %s,")} does note exist{message(self.message)}"

class CacheException(Exception):
    "Abstract Exception class for errors relating to Caches."

class CacheCannotWriteError(CacheException):
    "Attempted to write to a Cache that cannot be written to."

    def __init__(self, cache:"Cache.Cache", message:Optional[str]=None) -> None:
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

    def __init__(self, cache:"Cache.Cache", message:Optional[str]=None) -> None:
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

    def __init__(self, cache:"Cache.Cache", message:Optional[str]=None) -> None:
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

class BaseComponentCountError(ComponentException):
    "There is an invalid number of BaseComponents."

    def __init__(self, structure_name:str, base_components:list["BaseComponent.BaseComponent"], message:Optional[str]=None) -> None:
        '''
        :structure_name: The name of the Structure with an invalid count of BaseComponents.
        :base_components: The list of BaseComponents.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure_name, base_components, message)
        self.structure_name = structure_name
        self.base_components = base_components
        self.message = message

    def __str__(self) -> str:
        return f"Structure file \"{self.structure_name}\" has more than one BaseComponent: {", ".join(component.name for component in self.base_components)}{message(self.message)}"

class ComponentDuplicateTypeError(ComponentException):
    "A Component has a duplicate type."

    def __init__(self, type_str:str, source:object, message:Optional[str]=None) -> None:
        '''
        :type_str: The name of the type that is duplicated.
        :source: The object that references the duplicated types.
        :message: Additional text to place after the main message.
        '''
        super().__init__(type_str, source, message)
        self.type_str = type_str
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"Type \"{self.type_str}\", as referenced by {self.source}, is duplicate{message(self.message)}"

class ComponentFunctionException(ComponentException):
    "Abstract class for exceptions relating to Functions of Components"

class ComponentFunctionMissingArgumentError(ComponentFunctionException):
    "A required argument is missing."

    def __init__(self, source:object, parameter:str, message:Optional[str]=None) -> None:
        '''
        :source: The object that has a missing argument.
        :parameter: The parameter corresponding to the missing argument.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, parameter, message)
        self.source = source
        self.parameter = parameter
        self.message = message

    def __str__(self) -> str:
        return f"Required parameter \"{self.parameter}\" is missing from {self.source}{message(self.message)}"

class ComponentFunctionArgumentTypeError(ComponentException):
    "An argument has the wrong type."

    def __init__(self, source:object, parameter:str, argument:Any, argument_type:type, allowed_types:tuple[Any,...], message:Optional[str]=None) -> None:
        '''
        :source: The object that has an argument of the wrong type.
        :parameter: The name of the argument with the wrong type.
        :argument: The value of the argument with the wrong type.
        :argument_type: The type of the value of the argument with the wrong type.
        :allowed_types: The types and type-like objects that the
        '''
        super().__init__(source, parameter, argument, argument_type, allowed_types, message)
        self.source = source
        self.parameter = parameter
        self.argument = argument
        self.argument_type = argument_type
        self.allowed_types = allowed_types
        self.message = message

    def __str__(self) -> str:
        return f"Parameter \"{self.parameter}\" with value {self.argument} of {self.source} is of type \"{self.argument_type}\" instead of types [{", ".join(f"\"{item}\"" for item in self.allowed_types)}]{message(self.message)}"

class ComponentFunctionUnrecognizedArgumentError(ComponentFunctionException):
    "An argument exists that the function does not accept."

    def __init__(self, source:object, parameter:str, argument:Any, message:Optional[str]=None) -> None:
        '''
        :source: The object that has an additional argument.
        :parameter: The name of the additional argument.
        :argument: The value of the additional argument.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, parameter, argument, message)
        self.source = source
        self.parameter = parameter
        self.argument = argument
        self.message = message

    def __str__(self) -> str:
        return f"{self.source} has an additional parameter \"{self.parameter}\" with value {self.argument}{message(self.message)}"

class ComponentImporterCircularImportError(ComponentException):
    "Components attempt to make a circular import."

    def __init__(self, structure_names:list[str], message:Optional[str]=None) -> None:
        '''
        :structure_names: Names of Structures involved in the import loop.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure_names, message)
        self.structure_names = structure_names
        self.message = message

    def __str__(self) -> str:
        return f"Circular import: {self.structure_names}{message(self.message)}"

class ComponentInvalidNameError(ComponentException):
    "A Component's name is invalid."

    def __init__(self, component:"Component.Component", invalid_names:Optional[list[str]]=None, message:Optional[str]=None) -> None:
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
        return f"The name of {self.component} {f"cannot be one of {self.invalid_names}" if self.invalid_names is not None else "is invalid"}{message(self.message)}"

class ComponentInvalidVersionRangeException(ComponentException):
    "Abstract exception class for errors relating to the Version ranges in a DataminerSettings being invalid."

class ComponentVersionRangeExists(ComponentInvalidVersionRangeException):
    "The new/old Version of the first/last sub-Component is not None."

    def __init__(self, source:"Component.Component", actual_value:"Version.Version", is_first:bool, message:Optional[str]=None) -> None:
        '''
        :source: The Component with an invalid VersionRange.
        :actual_value: The value that is present in the new Version instead of None.
        :is_first: Whether this DataminerSettings is the newest one or not.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, actual_value, is_first, message)
        self.source = source
        self.actual_value = actual_value
        self.is_first = is_first
        self.message = message

    def __str__(self) -> str:
        return f"The {"new" if self.is_first else "old"} Version of the {"first" if self.is_first else "last"} sub-Component of {self.source} is not None, but instead {self.actual_value}{message(self.message)}"

class ComponentVersionRangeGap(ComponentInvalidVersionRangeException):
    "There is a gap in a Components's sub-Components' Versions."

    def __init__(self, source:"Component.Component", new_version:"Version.Version|str", old_version:"Version.Version|str", message:Optional[str]=None) -> None:
        '''
        :source: The Component with invalid VersionRange.
        :new_version: The Version or the Version's name on the newer side of the gap.
        :old_version: The Version or the Version's name on the older side of the gap.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, new_version, old_version, message)
        self.source = source
        self.new_version = new_version
        self.old_version = old_version
        self.message = message

    def __str__(self) -> str:
        return f"{self.source} has a gap between Versions {self.new_version} and {self.old_version}{message(self.message)}"

class ComponentVersionRangeMissing(ComponentInvalidVersionRangeException):
    "The new or old Version of a non-first DataminerSettings is None."

    def __init__(self, source:"Component.Component", index:int, slot:Literal["old", "new"], message:Optional[str]=None) -> None:
        '''
        :source: The Comopnent with an invalid VersionRange.
        :index: The index of the DataminerSettings
        :slot: The key ("old" or "new") of the sub-Component.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, index, slot, message)
        self.dataminer_collection_component = source
        self.index = index
        self.slot = slot
        self.message = message

    def __str__(self) -> str:
        return f"The {self.slot} Version of sub-Component {self.index} of {self.dataminer_collection_component} is None{message(self.message)}"

class ComponentMismatchedTypesError(ComponentException):
    "The types of one Component and the types of another do not match."

    def __init__(self, component1:"Component.Component", component1_types:list[type], component2:"Component.Component", component2_types:list[type], message:Optional[str]=None) -> None:
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

    def __init__(self, failed_component_groups:list[str], message:Optional[str]=None) -> None:
        '''
        :failed_component_groups: The Component groups that failed to parse.
        :message: Additional text to place after the main message.
        '''
        super().__init__(failed_component_groups, message)
        self.failed_component_groups = failed_component_groups
        self.message = message

    def __str__(self) -> str:
        return f"Failed to parse Component group(s) [{", ".join(self.failed_component_groups)}]{message(self.message)}"

class ComponentTypeContainmentError(ComponentException):
    "A Component has a type that cannot be contained by its current container type."

    def __init__(self, source_component:"Component.Component", container_type:type, containee_type:type, message:Optional[str]=None) -> None:
        '''
        :source_component: The Component with the disallowed type.
        :container_type: The type of the container.
        :containee_type: The type contained by the container type.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source_component, container_type, containee_type, message)
        self.source_component = source_component
        self.container_type = container_type
        self.containee_type = containee_type
        self.message = message

    def __str__(self) -> str:
        return f"Type \"{self.containee_type}\" of {self.source_component} cannot be contained by type \"{self.container_type}\"{message(self.message)}"

class ComponentTypeInvalidTypeError(ComponentException):
    "A Component has a value in a TypeField that is not allowed."

    def __init__(self, source_component:"Component.Component", observed_type:type, allowed_types:"TypeUtilities.TypeSet", message:Optional[str]=None) -> None:
        '''
        :source_component: The Component with the disallowed type.
        :observed_type: The type that is not allowed.
        :allowed_types: The set of types that this TypeField must be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source_component, observed_type, allowed_types, message)
        self.type_field = source_component
        self.observed_type = observed_type
        self.allowed_types = allowed_types
        self.message = message

    def __str__(self) -> str:
        return f"{self.type_field} has field with type {self.observed_type}, which is not one of [{", ".join(type.__name__ for type in sorted(self.allowed_types, key=lambda value: value.__name__))}]{message(self.message)}"

class ComponentTypeMissingError(ComponentException):
    "A Component is missing the type key and there is no type assumption."

    def __init__(self, component_name:str, component_group:str, message:Optional[str]=None) -> None:
        '''
        :component_name: The name of the Component with the missing type key.
        :component_group: The Component group the Component is found in.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component_name, component_group, message)
        self.component_name = component_name
        self.component_group = component_group
        self.message = message

    def __str__(self) -> str:
        return f"Component \"{self.component_name}\" in {self.component_group} is missing its type key{message(self.message)}"

class ComponentTypeRequiresComponentError(ComponentException):
    "A Component has a type that requires a Component but has no Component."

    def __init__(self, component:"Component.Component|str", accepted_type:type, message:Optional[str]=None) -> None:
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

class ComponentUnrecognizedFunctionError(ComponentException):
    "This Component references an unrecognized function."

    def __init__(self, function_name:str, source:object|str, message:Optional[str]=None) -> None:
        '''
        :function_name: The name of the unrecognized function.
        :source: The object or a string representing the object that references the function.
        :message: Additional text to place after the main message.
        '''
        super().__init__(function_name, source, message)
        self.function_name = function_name
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"Function \"{self.function_name}\", as referenced by {self.source}, is unrecognized{message(self.message)}"

class ComponentUnrecognizedTypeError(ComponentException):
    "This Component references an unrecognized default type."

    def __init__(self, type_str:str, source:object, message:Optional[str]=None) -> None:
        '''
        :type_str: The name of the unrecognized type.
        :source: The object that references this type.
        :message: Additional text to place after the main message.
        '''
        super().__init__(type_str, source, message)
        self.type_str = type_str
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"Type \"{self.type_str}\", as referenced by {self.source}, is unrecognized{message(self.message)}"

class EmptyCapabilitiesError(ComponentException):
    "An empty Capabilities object was created."

    def __init__(self, capabilities:"Capabilities.Capabilities", message:Optional[str]=None) -> None:
        '''
        :capabilities: The empty Capabilities object.
        :message: Additional text to place after the main message.
        '''
        super().__init__(capabilities, message)
        self.capabilities = capabilities
        self.message = message

    def __str__(self) -> str:
        return f"{self.capabilities} is empty{message(self.message)}"

class FieldSequenceBreakError(ComponentException):
    "A Field's methods were called in the wrong order."

    def __init__(self, first_method:Callable, second_method:Callable, source:object, message:Optional[str]=None) -> None:
        '''
        :first_method: The method that should be called first.
        :second_method: The method that should be called second.
        :source: The object whose methods were called out of order.
        :message: Additional text to place after the main message.
        '''
        super().__init__(first_method, second_method, source, message)
        self.first_method = first_method
        self.second_method = second_method
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"Cannot call \"{self.second_method.__name__}\" before \"{self.first_method.__name__}\" on {self.source}{message(self.message)}"

class ImporterEnvironmentNameCollisionError(ComponentException):
    "Two Component groups have the same name."

    def __init__(self, name:str, importer_environment1:"ImporterEnvironment.ImporterEnvironment", importer_environment2:"ImporterEnvironment.ImporterEnvironment", message:Optional[str]=None) -> None:
        '''
        :name: The name of the duplicate Component group.
        :importer_environment1: The ImporterEnvironment that produced the first Component group with this name.
        :importer_environment2: The ImporterEnvironment that produced the second Component group with this name.
        :message: Additional text to place after the main message.
        '''
        super().__init__(name, importer_environment1, importer_environment2, message)
        self.name = name
        self.importer_environment1 = importer_environment1
        self.importer_environment2 = importer_environment2
        self.message = message

    def __str__(self) -> str:
        return f"ImporterEnvironments {self.importer_environment1} and {self.importer_environment2} both attempted to create a Component group with the name \"{self.name}\"{message(self.message)}"

class ImporterEnvironmentFileNotFoundError(ComponentException):
    "An ImporterEnvironment refers to a file that does not exist and has no default content"

    def __init__(self, path:Path, importer_environment:"ImporterEnvironment.ImporterEnvironment", message:Optional[str]=None) -> None:
        '''
        :path: The Path the ImporterEnvironment refers to that does not exist.
        :importer_environment: The ImporterEnvironment that refers to the Path.
        :message: Additional text to place after the main message.
        '''
        super().__init__(path, importer_environment, message)
        self.path = path
        self.importer_environment = importer_environment
        self.message = message

class ImporterEnvironmentPathCollisionError(ComponentException):
    "Two Component groups come from the same file."

    def __init__(self, path:Path, importer_environment1:"ImporterEnvironment.ImporterEnvironment", importer_environment2:"ImporterEnvironment.ImporterEnvironment", message:Optional[str]=None) -> None:
        '''
        :path: The path of the duplicate Component group.
        :importer_environment1: The ImporterEnvironment that produced the first Component group with this path.
        :importer_environment2: The ImporterEnvironment that produced the second Component group with this path.
        :message: Additional text to place after the main message.
        '''
        super().__init__(path, importer_environment1, importer_environment2, message)
        self.path = path
        self.importer_environment1 = importer_environment1
        self.importer_environment2 = importer_environment2
        self.message = message

    def __str__(self) -> str:
        return f"ImporterEnvironments {self.importer_environment1} and {self.importer_environment2} both attempted to create a Component group from the same file \"{self.path.as_posix()}\"{message(self.message)}"

class InlineComponentError(ComponentException):
    "An inline Component exists where it is not allowed."

    def __init__(self, component:"Component.Component", field:"Field.Field", subcomponent_data:Optional["ComponentTyping.ComponentTypedDicts"]=None, message:Optional[str]=None) -> None:
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

    def __init__(self, component:"Component.Component", source:object|str, required_properties:"Pattern.Pattern", actual_capabilities:"Capabilities.Capabilities", message:Optional[str]=None) -> None:
        '''
        :component: The Component that is being referenced.
        :source: The object or a string representing the object that is referencing the Component.
        :required_properties: The Pattern that the Component is expected to have.
        :actual_capabilities: The Capabilities that the Component actually has.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, source, required_properties, actual_capabilities, message)
        self.component = component
        self.source = source
        self.required_properties = required_properties
        self.actual_capabilities = actual_capabilities
        self.message = message

    def __str__(self) -> str:
        return f"{self.component}, as referenced by {self.source}, is expected to have {self.required_properties}, but only has {self.actual_capabilities}{message(self.message)}"

class LinkedComponentExtraError(ComponentException):
    "An extra linked Component is present."

    def __init__(self, component:"Component.Component", key:str, linked_object:Any, message:Optional[str]=None) -> None:
        '''
        :component: The Component with an extra linked Component.
        :key: The key of the extra linked Component.
        :linked_object: The object of the linked Component.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, key, linked_object, message)
        self.component = component
        self.key = key
        self.linked_object = linked_object
        self.message = message

    def __str__(self) -> str:
        return f"{self.component} has an extra linked Component \"{self.key}\": {self.linked_object}{message(self.message)}"

class LinkedComponentMissingError(ComponentException):
    "A linked Component is missing."

    def __init__(self, component:"Component.Component", key:str, linked_type:type, message:Optional[str]=None) -> None:
        '''
        :component: The Component missing a linked Component.
        :key: The key of the missing Component.
        :linked_type: The type of the linked object.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, key, linked_type, message)
        self.component = component
        self.key = key
        self.linked_type = linked_type
        self.message = message

    def __str__(self) -> str:
        return f"{self.component} is missing linked Component \"{self.key}\" of type \"{self.linked_type.__name__}\"{message(self.message)}"

class LinkedComponentTypeError(ComponentException):
    "A linked Component's object is the wrong type."

    def __init__(self, component:"Component.Component", key:str, required_type:type, observed_object:Any, message:Optional[str]=None) -> None:
        '''
        :component: The Component with the wrong type of linked object.
        :key: The key of the linked Component.
        :required_type: The type the linked object should have.
        :observed_object: The linked object.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, key, required_type, observed_object, message)
        self.component = component
        self.key = key
        self.required_type = required_type
        self.observed_object = observed_object
        self.message = message

    def __str__(self) -> str:
        return f"{self.component}'s linked object \"{self.key}\": {self.observed_object} should be type \"{self.required_type.__name__}\"{message(self.message)}"

class NoComponentMatchError(ComponentException):
    "No Components match the Pattern."

    def __init__(self, pattern:"Pattern.Pattern", message:Optional[str]=None) -> None:
        '''
        :pattern: The Pattern that does not exist in the Components.
        :message: Additional text to place after the main message.
        '''
        super().__init__(pattern, message)
        self.pattern = pattern
        self.message = message

    def __str__(self) -> str:
        return f"Cannot find Components with {self.pattern}{message(self.message)}"

class ReferenceComponentError(ComponentException):
    "A reference Component exists where it is not allowed."

    def __init__(self, component:"Component.Component", field:"Field.Field", subcomponent_name:Optional[str]=None, message:Optional[str]=None) -> None:
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

    def __init__(self, component_str:str, source_str:str, message:Optional[str]=None) -> None:
        '''
        :component_str: The name of the unrecognized Component.
        :source_str: The object that refers to this Component.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component_str, message)
        self.component_type_str = component_str
        self.source_str = source_str
        self.message = message

    def __str__(self) -> str:
        return f"Component at \"{self.component_type_str}\", as referenced by {self.source_str}, is unrecognized{message(self.message)}"

class UnrecognizedComponentGroupError(ComponentException):
    "A Component group is unrecognized"

    def __init__(self, component_group_str:str, source_str:str, message:Optional[str]=None) -> None:
        '''
        :component_group_str: The name of the unrecognized Component group.
        :source_str: The object that refers to this Component group.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component_group_str, source_str, message)
        self.component_group_str = component_group_str
        self.source_str = source_str
        self.message = message

    def __str__(self) -> str:
        return f"Component group \"{self.component_group_str}\", as referenced by {self.source_str}, is unrecognized{message(self.message)}"

class UnrecognizedComponentTypeError(ComponentException):
    "A Component type is unrecognized."

    def __init__(self, component_type_str:str, source_str:str, message:Optional[str]=None) -> None:
        '''
        :component_type_str: The name of the unrecognized Component type.
        :source_str: The object that refers to this Component type.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component_type_str, message)
        self.component_type_str = component_type_str
        self.source_str = source_str
        self.message = message

    def __str__(self) -> str:
        return f"Component type \"{self.component_type_str}\", as referenced by {self.source_str}, is unrecognized{message(self.message)}"

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

    def __init__(self, source:"DataFile.DataFile", message:Optional[str]=None) -> None:
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

    def __init__(self, dataminer:"Dataminer.Dataminer", file_type:str, accessor_type:type["Accessor.Accessor"], message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that attempted to access its Accessor.
        :file_type: The name of the VersionFile that has the wrong Accessor type.
        :accessor_type: The type that the Accessor should be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, file_type, accessor_type, message)
        self.dataminer = dataminer
        self.file_type = file_type
        self.accessor_type = accessor_type
        self.message = message

    def __str__(self) -> str:
        return f"VersionFile \"{self.file_type}\" from {self.dataminer} should have Accessor with type \"{self.accessor_type.__name__}\"{message(self.message)}"

class DataminerAdditionalSerializerError(DataminerException):
    "This Dataminer has been provided with an additional, unnecessary Serializer."

    def __init__(self, dataminer_settings:"DataminerSettings.DataminerSettings", dataminer_class:type["Dataminer.Dataminer"], key:str, serializer:"Serializer.Serializer", allowed_keys:set[str], message:Optional[str]=None) -> None:
        '''
        :dataminer_settings: The DataminerSettings that provided the additional Serializer.
        :dataminer_class: The class of Dataminer that the DataminerSettings has that does not support the key.
        :key: The key of the additional Serializer.
        :serializer: The additional Serializer.
        :allowed_keys: The set of Serializer keys that are allowed in this Dataminer.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_settings, dataminer_class, key, serializer, allowed_keys, message)
        self.dataminer_settings = dataminer_settings
        self.dataminer_class = dataminer_class
        self.key = key
        self.serializer = serializer
        self.allowed_keys = allowed_keys
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer_settings} provided additional Serializer key \"{self.key}\": {self.serializer} to Dataminer class \"{self.dataminer_class}\", which only supports keys [{", ".join(self.allowed_keys)}]{message(self.message)}"

class DataminerCollectionFileError(DataminerException):
    "The \"files\" key in a DataminerCollection is improperly specified."

    def __init__(self, exists:bool, source:object, message:Optional[str]=None) -> None:
        '''
        :exists: Whether or not the "files" key actually exists.
        :source: The object that has an incorrect "files" key.
        :message: Additional text to place after the main message.
        '''
        super().__init__(exists, source, message)
        self.exists = exists
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"Key \"files\" of {self.source} {"cannot" if self.exists else "must"} exist{message(self.message)}"

class DataminerDependencyOverwriteError(DataminerException):
    "Attempted to set an item of a DataminerDependencies object that already exists."

    def __init__(self, dataminer_dependencies:"DataminerEnvironment.DataminerDependencies", dependency_name:str, message:Optional[str]=None) -> None:
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

    def __init__(self, file_name:str, dataminers:list["AbstractDataminerCollection.AbstractDataminerCollection"], message:Optional[str]=None) -> None:
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
    "A Dataminer attempted to access an VersionFileType it has no permissions to use."

    def __init__(self, dataminer:"Dataminer.Dataminer", file_type_name:str, allowed_file_types:Optional[list[str]]=None, message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that attempted to access a VersionFileType without permission.
        :file_type_name: The name of the VersionFileType it attempted to access.
        :allowed_file_types: A list of all VersionFileType names this Dataminer is allowed to access.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, file_type_name, allowed_file_types, message)
        self.dataminer = dataminer
        self.file_type_name = file_type_name
        self.allowed_file_types = allowed_file_types
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} attempted to access VersionFileType {self.file_type_name}; permissions are lacking or it does not exist{message(self.message, "", " %s")}{message(self.allowed_file_types, yes_message=". It may only access %s!")}"

class DataminerLacksActivateError(DataminerException):
    "A Dataminer did not override the activate function."

    def __init__(self, dataminer:"Dataminer.Dataminer", message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer that is missing the activate function.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} is missing its activate function{message(self.message)}"

class DataminerNothingFoundError(DataminerException):
    "This Dataminer found nothing."

    def __init__(self, dataminer:"Dataminer.Dataminer", message:Optional[str]=None) -> None:
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

    def __init__(self, dataminer:"AbstractDataminerCollection.AbstractDataminerCollection", message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer whose activate method returned None.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} returned None upon being activated{message(self.message)}"

class DataminerSerializerMissingError(DataminerException):
    "A Dataminer class requires a Serializer and does not have one."

    def __init__(self, dataminer_settings:"DataminerSettings.DataminerSettings", dataminer_type:type["Dataminer.Dataminer"], serializer_key:str, message:Optional[str]=None) -> None:
        '''
        :dataminer_settings: The DataminerSettings whose Dataminer type requires a Serializer.
        :dataminer_type: The DataminerSettings' Dataminer type.
        :serializer_key: The key of the missing Serializer.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_settings, dataminer_type, serializer_key, message)
        self.dataminer_settings = dataminer_settings
        self.dataminer_type = dataminer_type
        self.serializer_key = serializer_key
        self.message = message

    def __str__(self) -> str:
        return f"Dataminer type \"{self.dataminer_type.__name__}\" from {self.dataminer_settings} is missing Serializer {self.serializer_key}{message(self.message)}"

class DataminerSettingsImporterLoopError(DataminerException):
    "A DataminerSettings has an import loop."

    def __init__(self, dataminer_settings:"DataminerSettings.DataminerSettings", loop_items:list[str], message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", dataminer_collections:list["AbstractDataminerCollection.AbstractDataminerCollection"], message:Optional[str]=None) -> None:
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
        return f"Failed to datamine {self.version} on Dataminers [{", ".join(dataminer_collection.name for dataminer_collection in self.dataminer_collections)}]{message(self.message)}"

class DataminerUnrecognizedSerializerError(DataminerException):
    "Called `export_file` on a Dataminer with no Serializer"

    def __init__(self, dataminer:"Dataminer.Dataminer", key:str, message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer missing a Serializer.
        :key: The key that attempted to access the Serializer.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, key, message)
        self.dataminer = dataminer
        self.key = key
        self.message = message

    def __str__(self) -> str:
        return f"Attempted to call export_file on {self.dataminer} using non-existent Serializer key \"{self.key}\"{message(self.message)}"

class DataminerUnrecognizedDependencyError(DataminerException):
    "A dependency does not exist."

    def __init__(self, dataminer:"Dataminer.Dataminer", dependency_name:str, message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer attempting to access the dependency.
        :dependency_name: The name of the DataminerCollection that does not exist.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, dependency_name, message)
        self.dataminer = dataminer
        self.dependency_name = dependency_name
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} references dependency \"{self.dependency_name}\" that is non-existent for this Version{message(self.message)}"

class DataminerUnrecognizedSuffixError(DataminerException):
    "A file suffix is unrecognized."

    def __init__(self, dataminer:"Dataminer.Dataminer", path:str, recognized_suffixes:list[str], message:Optional[str]=None) -> None:
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

    def __init__(self, dataminer:"Dataminer.Dataminer", dependency_name:str, message:Optional[str]=None) -> None:
        '''
        :dataminer: The Dataminer attempting to access the dependency.
        :dependency_name: The name of the DataminerCollection that is unregistered.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, dependency_name, message)
        self.dataminer = dataminer
        self.dependency_name = dependency_name
        self.message = message

    def __str__(self) -> str:
        return f"{self.dataminer} references unlisted dependency \"{self.dependency_name}\"{message(self.message)}"

class MissingDataFileError(DataminerException):
    "The data file for this DataminerCollection is missing."

    def __init__(self, dataminer:"Dataminer.Dataminer|DataminerSettings.DataminerSettings|AbstractDataminerCollection.AbstractDataminerCollection", file_name:str, version:Optional["Version.Version"], message:Optional[str]=None) -> None:
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
        return f"File {self.file_name} of {self.dataminer}{message(self.version, "", "of Version \"%s\"", lambda version: version.name)} is missing{message(self.message)}"

class NullDataminerMethodError(DataminerException):
    "An invalid exception has been called on a NullDataminer."

    def __init__(self, dataminer:"Dataminer.NullDataminer", method:Callable, message:Optional[str]=None) -> None:
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

    def __init__(self, dataminer:"Dataminer.Dataminer", tag:"StructureTag.StructureTag", dataminer_collection:"AbstractDataminerCollection.AbstractDataminerCollection", message:Optional[str]=None) -> None:
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

    def __init__(self, data_reader:"TagSearcherDataminer.DataReader", reason:str, message:Optional[str]=None) -> None:
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
        delegate_type:type["Delegate.Delegate"],
        structure:"Structure.Structure|StructureBase.StructureBase",
        allowed_types:tuple[type["Structure.Structure|StructureBase.StructureBase|None"], ...],
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

    def __init__(self, log:"Log.Log", path:Path, message:Optional[str]=None) -> None:
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
        return f"The path of {self.log}, \"{self.path.as_posix()}, is invalid{message(self.message)}"

class LogWriteTypeError(LogException):
    "Attempted to write to a Log with an invalid type for the Log's LogType."

    def __init__(self, log:"Log.Log", write_type:type, allowed_types:tuple[type,...], message:Optional[str]=None) -> None:
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

    def __init__(self, name:str, path:Path, message:Optional[str]=None) -> None:
        '''
        :name: The file name used to access the LibFiles.
        :path: The Path that was found using `name`.
        :message: Additional text to place after the main message.
        '''
        super().__init__(name, path, message)
        self.name = name
        self.path = path
        self.message = message

    def __str__(self) -> str:
        return f"Path \"{self.path.as_posix()}\", derived from \"{self.name}\", does not exist{message(self.message)}"

class LibFileWrongDirectoryError(DomainException):
    "Attempted to access a lib file that is not in the correct directory."

    def __init__(self, name:str, path:Path, correct_directory:Path, message:Optional[str]=None) -> None:
        '''
        :name: The file name used to access the LibFiles.
        :path: The Path that was found using `name`.
        :correct_directory: The Path that `path` should be a descendent of.
        :message: Additional text to place after the main message.
        '''
        super().__init__(name, path, message)
        self.name = name
        self.path = path
        self.correct_directory = correct_directory
        self.message = message

    def __str__(self) -> str:
        return f"Path derived from {self.name} should be a descendent of {self.correct_directory.as_posix()}, not {self.path.as_posix()}{message(self.message)}"

class ScriptException(Exception):
    "Abstract Exception class for errors relating to Scripts."

class InvalidScriptFileSuffix(ScriptException):
    "A Script file has an invalid suffix."

    def __init__(self, suffix:str, name:str, message:Optional[str]=None) -> None:
        '''
        :suffix: The invalid suffix of the file.
        :name: The name of the file.
        :message: Additional text to place after the main message.
        '''
        super().__init__(suffix, name, message)
        self.suffix = suffix
        self.name = name
        self.message = message

    def __str__(self) -> str:
        return f"Invalid file suffix \"{self.suffix}\" on file \"{self.name}\"{message(self.message)}"

class InvalidScriptObjectTypeError(ScriptException):
    "An object in a Script has the wrong type."

    def __init__(self, script:"Scripts.Script", object:Any, allowed_types:list[type], message:Optional[str]=None) -> None:
        '''
        :script: The script with the error.
        :object: The object from the Script with the wrong type.
        :allowed_types: The types this object should be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(object, allowed_types, message)
        self.script = script
        self.object = object
        self.allowed_types = allowed_types
        self.message = message

    def __str__(self) -> str:
        return f"{self.object} in {self.script} should be one of types [{", ".join(f"\"{allowed_type.__name__}\"" for allowed_type in self.allowed_types)}] instead of type \"{self.object.__class__.__name__}\"{message(self.message)}"

class ScriptedClassMissingInheritError(ScriptException):
    "A scripted type failed to correctly inherit."

    def __init__(self, class_name:str, should_inherit_from:type, message:Optional[str]=None) -> None:
        '''
        :class_name: The name of the type class that failed to inherit.
        :should_inherit_from: the type the class should subclass.
        :message: Additional text to place after the main message.
        '''
        super().__init__(class_name, should_inherit_from, message)
        self.class_name = class_name
        self.should_inherit_from = should_inherit_from
        self.message = message

    def __str__(self) -> str:
        return f"Scripted class \"{self.class_name} does not inherit from {self.should_inherit_from.__name__}{message(self.message)}"

class ScriptFailureError(ScriptException):
    "A Script has failed to load."

    def __init__(self, script:"Scripts.Script", message:Optional[str]=None) -> None:
        '''
        :script: The Script that failed to load.
        :message: Additional text to place after the main message.
        '''
        super().__init__(script, message)
        self.script = script
        self.message = message

    def __str__(self) -> str:
        return f"{self.script} failed to load{message(self.message)}"

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

class UnrecognizedScriptError(ScriptException):
    "An unrecognized Script was referenced."

    def __init__(self, script_name:str, message:Optional[str]=None) -> None:
        '''
        :script_name: The name of the unrecognized script.
        :message: Additional text to place after the main message.
        '''
        super().__init__(script_name, message)
        self.script_name = script_name
        self.message = message

    def __str__(self) -> str:
        return f"Unrecognized Script \"{self.script_name}\"{message(self.message)}"

class WrongScriptError(ScriptException):
    "Attempted to import a Script that exists, but cannot be used in this situation."

    def __init__(self, script:"Scripts.Script", message:Optional[str]=None) -> None:
        '''
        :script: The Script that cannot be used in this situation.
        :message: Additional text to place after the main message.
        '''
        super().__init__(script, message)
        self.script = script
        self.message = message

    def __str__(self) -> str:
        return f"Cannot load {self.script} in this situation{message(self.message)}"

class SerializerException(Exception):
    "Abstract Exception class for errors relating to Serializers"

class SerializationFailureError(SerializerException):
    "A Serializer failed to serialize."

    def __init__(self, serializer:"Serializer.Serializer", file_name:str, message:Optional[str]=None) -> None:
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

    def __init__(self, serializer:"Serializer.Serializer", method:Callable, message:Optional[str]=None) -> None:
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

class UnrecognizedSerializerInFileError(SerializerException):
    "A Serializer's name in a stored File does not exist."

    def __init__(self, file_data:"File.FileJsonTypedDict", message:Optional[str]=None) -> None:
        '''
        :file_data: The data used to create the File.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_data, message)
        self.serializer = file_data["serializer"]
        self.name = file_data["name"]
        self.hash = file_data["hash"]
        self.message = message

    def __str__(self) -> str:
        return f"Attempted to create File with name \"{self.name}\" and hash \"{self.hash}\" using non-existent Serializer \"{self.serializer}\"{message(self.message)}"

class StructureException(Exception):
    "Abstract Exception class for errors relating to Structures"

class CompareWithNoneError(StructureException):
    "A StructureSet attempted to compare data using None instead of a Structure."

    def __init__(self, structure:"Structure.Structure|StructureSet.StructureSet", key:int|None=None, message:Optional[str]=None) -> None:
        '''
        :structure_set: The Structure or StructureSet with a None substructure.
        :key: The key used to access the StructureSet if it is a StructureSet.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure, key, message)
        self.structure = structure
        self.key = key
        self.message = message

    def __str__(self) -> str:
        return f"Attempted to compare with {message(self.key, "", "key %s on ")}{self.structure} using a NoneType object{message(self.message)}"

class ComparisonEnvironmentNoVersionError(StructureException):
    "A ComparisonEnvironment has no non-None items in its Version list."

    def __init__(self, environment:"StructureEnvironment.ComparisonEnvironment", message:Optional[str]=None) -> None:
        '''
        :environment: The ComparisonEnvironment with no non-None items in its Versions list.
        :message: Additional text to place after the main message.
        '''
        super().__init__(environment, message)
        self.environment = environment
        self.message = message

    def __str__(self) -> str:
        return f"{self.environment} has non non-None Versions{message(self.message)}"

class DiffContinuityError(StructureException):
    "Attempted to create a Diff with overlapping branches."

    def __init__(self, all_branches:list[int], overlapping_branch:int, message:Optional[str]=None) -> None:
        '''
        :all_branches: All branches that the Diff would have.
        :overlapping_branch: The branch that is already in `all_branches`.
        :message: Additional text to place after the main message.
        '''
        super().__init__(all_branches, overlapping_branch, message)
        self.all_branches = all_branches
        self.overlapping_branches = overlapping_branch
        self.message = message

    def __str__(self) -> str:
        return f"Attempted to create a Diff with branch {self.overlapping_branches} overlapping with one of [{", ".join(str(branch) for branch in self.all_branches)}]{message(self.message)}"

class DiffExistenceError(StructureException):
    "The Diff object has no items except for NoExist."

    def __init__(self, diff:"D.Diff", message:Optional[str]=None) -> None:
        '''
        :diff: The Diff object with no items except for NoExist.
        :message: Additional text to place after the main message.
        '''
        super().__init__(diff, message)
        self.diff = diff
        self.message = message

    def __str__(self) -> str:
        return f"{self.diff} has no items besides NoExist{message(self.message)}"

class DiffKeyError(StructureException):
    "The Diff object does not have anything at the position indexed."

    def __init__(self, index:int|tuple[int,...], diff:"D.Diff", message:Optional[str]=None) -> None:
        '''
        :index: The index used to access the Diff.
        :diff: The Diff that was indexed.
        :message: Additional text to place after the main message.
        '''
        super().__init__(index, diff, message)
        self.index = index
        self.diff = diff
        self.message = message

    def __str__(self) -> str:
        return f"{self.diff} does not have an item at index {self.index}{message(self.message)}"

class InvalidFileHashType(StructureException):
    "An is_file StructureTag references data that cannot be interpreted as a file hash."

    def __init__(self, version:"Version.Version", structure_tag:"StructureTag.StructureTag", data_path:"DataPath.DataPath", message:Optional[str]=None) -> None:
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

class InvalidSimilarityError(StructureException):
    "A calulated similarity is not in [0.0, 1.0]"

    def __init__(self, structure:"Structure.Structure", similarity:float, data1:Any, data2:Any, message:Optional[str]=None) -> None:
        '''
        :structure: The Structure that returned an invalid similarity.
        :similarity: The similarity that is out of range.
        :data1: The older data that caused an invalid similarity
        :data2: The newer data that caused an invalid similarity
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure, similarity, data1, data2, message)
        self.structure = structure
        self.similarity = similarity
        self.data1 = data1
        self.data2 = data2
        self.message = message

    def __str__(self) -> str:
        return f"{self.structure} has a similarity of {self.similarity}{message(self.message, "", " %s")} on data {self.data1} and {self.data2}!"

class NormalizerNoneError(StructureException):
    "A Normalizer has returned None where it should return something."

    def __init__(self, normalizer:"Normalizer.Normalizer", source:object, message:Optional[str]=None) -> None:
        super().__init__(normalizer, source, message)
        self.normalizer = normalizer
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"{self.normalizer}, as referenced by {self.source}, returned None when it shouldn't have{message(self.message)}"

class SequenceTooLongError(StructureException):
    "A StringStructure or SequenceStructure cannot compare or get similarity of data because it is too long."

    def __init__(self, structure:"Structure.Structure", len1:int, len2:int, message:Optional[str]=None) -> None:
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
        return f"Failed to compare on Structures [{", ".join(self.structure_names)}]{message(self.message)}"

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

    def __init__(self, structure_base:"StructureBase.StructureBase", message:Optional[str]=None) -> None:
        '''
        :structure_base: The StructureBase that failed.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure_base, message)
        self.structure_base = structure_base
        self.message = message

    def __str__(self) -> str:
        return f"{self.structure_base} has failed{message(self.message)}"

class StructureExceptionError(StructureException):
    "An error occured where it should not."

    def __init__(self, structure:"Structure.Structure", function:Callable, exceptions:list["Trace.ErrorTrace"], message:Optional[str]=None) -> None:
        '''
        :structure: The Structure with the errors inside its function.
        :function: The function of the Structure where the errors occured.
        :exceptions: The exceptions that should not exist.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure, function, exceptions, message)
        self.structure = structure
        self.function = function
        self.exceptions = exceptions
        self.message = message

    def __str__(self) -> str:
        return f"{self.structure} has errors in function \"{self.function.__name__}\" where it should not{message(self.message, "", " %s")}: [{", ".join(exception.finalize().stringify() for exception in self.exceptions)}]"

class StructureRequiredKeyMissingError(StructureException):
    "A required key is missing."

    def __init__(self, structure:"Structure.Structure", key:str, message:Optional[str]=None) -> None:
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
    "Data given to a Structure has the wrong type. This Error should only be used with ErrorTraces."

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

    def __init__(self, unrecognized_key:str, label:str="Key", message:Optional[str]=None) -> None:
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

class TraceError(StructureException):
    "The operation cannot be performed on this Trace due to its finalization being wrong."

    def __init__(self, trace:"Trace.ErrorTrace", function:Callable, is_finalized:bool, message:Optional[str]=None) -> None:
        '''
        :trace: The Trace with the invalid finalization.
        :function: The function that was called on the Trace.
        :is_finalized: The current, incorrect finalization status of the Trace.
        :message: Additional text to place after the main message.
        '''
        super().__init__(trace, function, is_finalized, message)
        self.trace = trace
        self.function = function
        self.is_finalized = is_finalized
        self.message = message

    def __str__(self) -> str:
        return f"Cannot perform function \"{self.function.__name__}\" on {self.trace} due to it being {"finalized" if self.is_finalized else "not finalized"}{message(self.message)}"

class UnrecognizedStructureTagError(StructureException):
    "A StructureTag referenced in a tag expression does not exist."

    def __init__(self, expression:str, tag_name:str, message:Optional[str]=None) -> None:
        '''
        :expression: The tag expression containing the unrecognized StructureTag.
        :tag_name: The name of the unrecognized StructureTag.
        :message: Additional text to place after the main message.
        '''
        super().__init__(expression, tag_name, message)
        self.expression = expression
        self.tag_name = tag_name
        self.message = message

    def __str__(self) -> str:
        return f"Unrecognized tag \"{self.tag_name}\" referenced in expression \"{self.expression}{message(self.message)}"

class TypeVerifierException(Exception):
    "Abstract Exception class for errors relating to TypeVerifiers."

class TypeVerificationFailedError(TypeVerifierException):
    "Type verification failed."

    def __init__(self, type_verifier:"TypeVerifier.TypeVerifier", message:Optional[str]=None) -> None:
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

    trace: "TypeVerifier.Trace"

    def __init__(self, trace:"TypeVerifier.Trace", *args: object) -> None:
        self.trace = trace
        super().__init__(trace, *args)

class TypeVerificationEnumError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace", options:Container, value:Any) -> None:
        super().__init__(trace, options, value)
        self.options = options
        self.value = value

    def __str__(self) -> str:
        return f"{self.trace.to_str()} is not one of {self.options}, but instead {self.value}"

class TypeVerificationFunctionError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace", message:str|None, data:Any|None=None) -> None:
        super().__init__(trace, message, data)
        self.message = message
        self.data = data

    def __str__(self) -> str:
        return f"{self.trace.to_str()}{message(self.data, "", " (data %s)")} failed verification{message(self.message, yes_message=" due to \"%s\"!")}"

class TypeVerificationMissingKeyError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace") -> None:
        super().__init__(trace)

    def __str__(self) -> str:
        return f"Required {self.trace.to_str(capitalize=False)} is missing!"

class TypeVerificationTypeError(TypeVerificationTypeException):

    def __init__(self, trace: "TypeVerifier.Trace", expected_type:str, observed_type:type) -> None:
        super().__init__(trace, expected_type, observed_type)
        self.expected_type = expected_type
        self.observed_type = observed_type

    def __str__(self) -> str:
        return f"{self.trace.to_str()} is not {self.expected_type}, but instead {self.observed_type.__name__}"

class TypeVerificationUnionError(TypeVerificationTypeException):

    def __init__(self, trace: "TypeVerifier.Trace", expected_type:str, observed_type:type, causes:list[list[TypeVerificationTypeException]]) -> None:
        super().__init__(trace, expected_type, observed_type, causes)
        self.expected_type = expected_type
        self.observed_type = observed_type
        self.causes = causes

    def __str__(self) -> str:
        return f"{self.trace.to_str()} is not {self.expected_type}, but instead {self.observed_type.__name__} due to {[[str(exception) for exception in exception_list] for exception_list in self.causes]}"

class TypeVerificationUnrecognizedKeyError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace") -> None:
        super().__init__(trace)

    def __str__(self) -> str:
        return f"{self.trace.to_str()} is an unrecognized key!"

class TypeVerificationWrongLengthError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace", expected_length:int, observed_length:int) -> None:
        super().__init__(trace, expected_length, observed_length)
        self.expected_length = expected_length
        self.observed_length = observed_length

    def __str__(self) -> str:
        return f"{self.trace.to_str()} is not length {self.expected_length}, but instead length {self.observed_length}!"

class VersionException(Exception):
    "Abstract Exception class for errors relating to Versions."

class DuplicateVersionTagOrderError(VersionException):
    "There are two VersionTags with the same name in VersionTagOrder"

    def __init__(self, tag:"VersionTag.VersionTag", key:str|tuple[str,...], message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", parent:"Version.Version", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", time:datetime.date|datetime.datetime, reason:str, message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", version_tags:list["VersionTag.VersionTag"], message:Optional[str]=None) -> None:
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

    def __init__(self, tag:"VersionTag.VersionTag", key:str|tuple[str,...], message:Optional[str]=None) -> None:
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

    def __init__(self, tag:"VersionTag.VersionTag", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", version_file:"VersionFile.VersionFile", message:Optional[str]=None) -> None:
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

    def __init__(self, parent_version:"Version.Version", parent_tag:"VersionTag.VersionTag", child_version:"Version.Version", child_tag:"VersionTag.VersionTag", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", child_tags:list["VersionTag.VersionTag"], error_child:"Version.Version", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", count:int, tags:list["VersionTag.VersionTag"], message:Optional[str]=None) -> None:
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

    def __init__(self, parent_version:"Version.Version", parent_tag:"VersionTag.VersionTag", child_version:"Version.Version", child_tag:"VersionTag.VersionTag", time_text:Literal["before", "after"], message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", version_range:Optional["VersionRange.VersionRange"]=None, message:Optional[str]=None) -> None:
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
        version_range:"VersionRange.VersionRange|VersionRangeField.VersionRangeField",
        start_version:"Version.Version|VersionComponent.VersionComponent",
        stop_version:"Version.Version|VersionComponent.VersionComponent",
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

    def __init__(self, source:object, property1:str, property2:str, message:Optional[str]=None) -> None:
        '''
        :source: The object that has conflicting properties.
        :property1: The name of the first mutually exclusive property.
        :property2: The name of the second mutually exclusive property.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, property1, property2, message)
        self.source = source
        self.property1 = property1
        self.property2 = property2
        self.message = message

    def __str__(self) -> str:
        return f"{self.source} cannot have both {self.property1} and {self.property2}{message(self.message)}"

class VersionTimeTravelError(VersionException):
    "A Version's children are not in order chronologically."

    def __init__(self, previous_child:"Version.Version", previous_time:datetime.datetime, current_child:"Version.Version", current_time:datetime.datetime, parent:"Version.Version", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", time:datetime.datetime, message:Optional[str]=None) -> None:
        '''
        :version: The Version without timezone info.
        :time: The time of the Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, time, message)
        self.version = version
        self.time = time
        self.message = message

    def __str__(self) -> str:
        return f"{self.version}'s time, {self.time.isoformat()} does not have a timezone but should{message(self.message)}"

class VersionTopLevelError(VersionException):
    "A Version is a top-level Version but has no top-level VersionTag."

    def __init__(self, version:"Version.Version", top_level_tag:"VersionTag.VersionTag", message:Optional[str]=None) -> None:
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

    def __init__(self, file_type:"VersionFileType.VersionFileType", version:"Version.Version", message:Optional[str]=None) -> None:
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

    def __init__(self, version_file:"VersionFile.VersionFile", accessor_str:str, message:Optional[str]=None) -> None:
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

    def __init__(self, version_file:"VersionFile.VersionFile", message:Optional[str]=None) -> None:
        '''
        :version_file: The VersionFile with no available Accessors.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_file, message)
        self.version_file = version_file
        self.message = message

    def __str__(self) -> str:
        return f"{self.version_file} has no available Accessors{message_bool(self.version_file.has_accessors(), "", lambda: f" from [{", ".join(repr(accessor) for accessor in self.version_file.get_accessors())}]")}{message(self.message)}"

class VersionFileTypeNotAutoAssigning(VersionFileException):
    "The VersionFileType does not auto assign."

    def __init__(self, version_file_type:"VersionFileType.VersionFileType", message:Optional[str]=None) -> None:
        '''
        :version_file_type: The VersionFileType that does not have auto assign.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_file_type, message)
        self.version_file_type = version_file_type
        self.message = message

    def __str__(self) -> str:
        return f"{self.version_file_type} is not an auto-assigning VersionFileType{message(self.message)}"
