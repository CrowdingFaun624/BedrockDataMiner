import datetime
from typing import (TYPE_CHECKING, Any, Callable, Container, Literal, Optional,
                    TypeVar, Union)

from pathlib2 import Path

if TYPE_CHECKING:
    import Component.Capabilities as Capabilities
    import Component.Component as Component
    import Component.ComponentTyping as ComponentTyping
    import Component.Field.Field as Field
    import Component.ImporterEnvironment as ImporterEnvironment
    import Component.Pattern as Pattern
    import Component.Version.Field.VersionRangeField as VersionRangeField
    import Component.Version.VersionComponent as VersionComponent
    import DataMiner.BuiltIns.TagSearcherDataMiner as TagSearcherDataMiner
    import DataMiner.DataMiner as DataMiner
    import DataMiner.DataMinerCollection as DataMinerCollection
    import DataMiner.DataMinerEnvironment as DataMinerEnvironment
    import DataMiner.DataMinerSettings as DataMinerSettings
    import Downloader.Accessor as Accessor
    import Downloader.Manager as Manager
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
    import Utilities.CustomJson as CustomJson
    import Utilities.DataFile as DataFile
    import Utilities.FileManager as FileManager
    import Utilities.Nbt.SnbtParser as SnbtParser
    import Utilities.Scripts as Scripts
    import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
    import Utilities.TypeVerifier.TypeVerifierImporter as TypeVerifierImporter
    import Version.Version as Version
    import Version.VersionFile as VersionFile
    import Version.VersionFileType as VersionFileType
    import Version.VersionRange as VersionRange
    import Version.VersionTag.VersionTag as VersionTag

a = TypeVar("a")

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
        output = "Attribute \"%s\" of %r is None and should not be" % (self.name, self.source)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Attempted to stringify an object of type \"%s\"" % (self.object_type,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class EmptyFileError(Exception):
    "The file IO has no bytes."

    def __init__(self, message:Optional[str]=None) -> None:
        '''
        :message: Additional text to place after the main message.
        '''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        output = "A file has no bytes"
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class FileHashNotFound(Exception):
    "A file cannot be found because its hash is missing in an archive."

    def __init__(self, unknown_hash:str, message:Optional[str]=None) -> None:
        '''
        :unknown_hash: The hash of the file that is unrecognized.
        :message: Additional text to place after the main message.
        '''
        super().__init__(unknown_hash, message)
        self.unknown_hash = unknown_hash
        self.message = message

    def __str__(self) -> str:
        output = "File with hash \"%s\" does not exist" % (self.unknown_hash,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class FileNotFoundInVersionArchive(Exception):
    "A file cannot be found in an archive."

    def __init__(self, file_name:str, version_name:str, message:Optional[str]=None) -> None:
        '''
        :file_name: The name of the unrecognized file.
        :version: The name of the version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_name, version_name, message)
        self.file_name = file_name
        self.version_name = version_name
        self.message = message

    def __str__(self) -> str:
        output = "File \"%s\" does not exist in version \"%s\" of the archive" % (self.file_name, self.version_name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class InvalidFileFormatError(Exception):
    "A file has an invalid file format."

    def __init__(self, file_name:str, message:Optional[str]=None) -> None:
        '''
        :file_name: The file with the invalid file format.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_name, message)
        self.file_name = file_name
        self.message = message

    def __str__(self) -> str:
        output = "File \"%s\" has an invalid file format" % (self.file_name,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class InvalidFileNameError(Exception):
    "A string cannot be used as a file name due to invalid characters."

    def __init__(self, file_name:str, file_label:str="File", message:Optional[str]=None) -> None:
        '''
        :file_name: The name of the file that is invalid.
        :file_label: A string to label the file type/location with.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_name, file_label, message)
        self.file_name = file_name
        self.file_label = file_label
        self.message = message

    def __str__(self) -> str:
        output = "%s \"%s\" cannot be created due to invalid characters" % (self.file_label, self.file_name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class InvalidStateError(Exception):
    "The program has reached an assumedly unreachable part of the code."

    def __str__(self) -> str:
        if len(self.args) == 0:
            return "Invalid state!"
        else:
            return "Invalid state: %s" % (self.args,)

class AccessorException(Exception):
    "Abstract Exception class for errors relating to Accessors."

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
        output = "Accessor class \"%s\"" % (self.accessor_class_str)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        elif self.source_str is not None:
            output += ", as referenced by %s," % (self.source_str)
        if self.message is None:
            output += " does not exist!"
        else:
            output += " does not exist %s!" % (self.message,)
        return output

class ComponentException(Exception):
    "Abstract Exception class for errors relating to Components."

class BaseComponentCountError(ComponentException):
    "There is an invalid number of BaseComponents."

    def __init__(self, structure_name:str, count:int, message:Optional[str]=None) -> None:
        '''
        :structure_name: The name of the Structure with an invalid count of BaseComponents.
        :count: How many BaseComponents are in this Structure file.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure_name, count, message)
        self.structure_name = structure_name
        self.count = count
        self.message = message

    def __str__(self) -> str:
        output = "Structure file \"%s\" has %i BaseComponents, while it should have 1" % (self.structure_name, self.count)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Type \"%s\", as referenced by %r, is duplicate!" % (self.type_str, self.source)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Required parameter \"%s\" is missing from %r" % (self.parameter, self.source)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Parameter \"%s\" with value %s of %r is of type \"%s\" instead of types [%s]" % (self.parameter, self.argument, self.source, self.argument_type, ", ".join("\"%s\"" % (item,) for item in self.allowed_types))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has an additional parameter \"%s\" with value %s" % (self.source, self.parameter, self.argument)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Circular import: %s" % (self.structure_names,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ComponentInvalidNameError(ComponentException):
    "A Component's name is invalid."

    def __init__(self, component:"Component.Component", invalid_names:list[str], message:Optional[str]=None) -> None:
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
        output = "The name of %r cannot be one of %s" % (self.component, self.invalid_names)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ComponentInvalidVersionRangeException(ComponentException):
    "Abstract exception class for errors relating to the Version ranges in a DataMinerSettings being invalid."

class ComponentVersionRangeExists(ComponentInvalidVersionRangeException):
    "The new/old Version of the first/last sub-Component is not None."

    def __init__(self, source:"Component.Component", actual_value:"Version.Version", is_first:bool, message:Optional[str]=None) -> None:
        '''
        :source: The Component with an invalid VersionRange.
        :actual_value: The value that is present in the new Version instead of None.
        :is_first: Whether this DataMinerSettings is the newest one or not.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, actual_value, is_first, message)
        self.source = source
        self.actual_value = actual_value
        self.is_first = is_first
        self.message = message

    def __str__(self) -> str:
        first_last_text = ("new", "first") if self.is_first else ("old", "last")
        output = "The %s Version of the %s sub-Component of %r is not None, but instead %r" % (first_last_text[0], first_last_text[1], self.source, self.actual_value)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ComponentVersionRangeGap(ComponentInvalidVersionRangeException):
    "There is a gap in a Components's sub-Components' Versions."

    def __init__(self, source:"Component.Component", new_version:Union["Version.Version",str], old_version:Union["Version.Version",str], message:Optional[str]=None) -> None:
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
        output = "%r has a gap between Versions %s and %s" % (self.source, self.new_version, self.old_version)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ComponentVersionRangeMissing(ComponentInvalidVersionRangeException):
    "The new or old Version of a non-first DataMinerSettings is None."

    def __init__(self, source:"Component.Component", index:int, slot:Literal["old", "new"], message:Optional[str]=None) -> None:
        '''
        :source: The Comopnent with an invalid VersionRange.
        :index: The index of the DataMinerSettings
        :slot: The key ("old" or "new") of the sub-Component.
        :message: Additional text to place after the main message.
        '''
        super().__init__(source, index, slot, message)
        self.dataminer_collection_component = source
        self.index = index
        self.slot = slot
        self.message = message

    def __str__(self) -> str:
        output = "The %s Version of sub-Component %i of %r is None" % (self.slot, self.index, self.dataminer_collection_component)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ComponentMismatchedTypesError(ComponentException):
    "The types of one Component and the types of another do not match."

    def __init__(self, component1:Union["Component.Component",str], component1_types:list[type], component2:Union["Component.Component",str], component2_types:list[type], message:Optional[str]=None) -> None:
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
        component1_str = self.component1 if isinstance(self.component1, str) else repr(self.component1)
        component2_str = self.component2 if isinstance(self.component2, str) else repr(self.component2)
        output = "%s accepts types [%s], but its subcomponent, %s, accepts types [%s]" % (component1_str, ", ".join("\"%s\"" % type.__name__ for type in self.component1_types), component2_str, ", ".join("\"%s\"" % type.__name__ for type in self.component2_types))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ComponentParseError(ComponentException):
    "Multiple Components failed to parse."

    def __init__(self, message:Optional[str]=None) -> None:
        '''
        :message: Additional text to place after the main message.
        '''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        output = "Failed to parse Component group(s)"
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Type \"%s\" of %r cannot be contained by type \"%s\"" % (self.containee_type, self.source_component, self.container_type)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ComponentTypeInvalidTypeError(ComponentException):
    "A Component has a value in a TypeField that is not allowed."

    def __init__(self, source_component:"Component.Component", observed_type:type, allowed_types:set[type], message:Optional[str]=None) -> None:
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
        type_list = ", ".join(type.__name__ for type in sorted(self.allowed_types, key=lambda value: value.__name__))
        output = "%r has field with type %s, which is not one of [%s]" % (self.type_field, self.observed_type, type_list)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Component \"%s\" in %s is missing its type key" % (self.component_name, self.component_group)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ComponentTypeRequiresComponentError(ComponentException):
    "A Component has a type that requires a Component but has no Component."

    def __init__(self, component:Union["Component.Component",str], accepted_type:type, message:Optional[str]=None) -> None:
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
        component_str = self.component if isinstance(self.component, str) else repr(self.component)
        output = "%s accepts type \"%s\", which requires a Component, but has no subcomponent" % (component_str, self.accepted_type.__name__)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        source_str = self.source if isinstance(self.source, str) else repr(self.source)
        output = "Function \"%s\", as referenced by %s, is unrecognized" % (self.function_name, source_str)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Type \"%s\", as referenced by %r, is unrecognized" % (self.type_str, self.source)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r is empty" % (self.capabilities,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Cannot call \"%s\" before \"%s\" on %r" % (self.second_method.__name__, self.first_method.__name__, self.source)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "ImporterEnvironments %r and %r both attempted to create a Component group with the name \"%s\"" % (self.importer_environment1, self.importer_environment2, self.name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "ImporterEnvironments %r and %r both attempted to create a Component group from the same file \"%s\"" % (self.importer_environment1, self.importer_environment2, self.path)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r, %r attempted to create a disallowed inline Component" % (self.component, self.field)
        if self.message is not None: output += " %s" % (self.message,)
        output += ": %s" % (self.subcomponent_data,) if self.subcomponent_data is not None else "!"
        return output

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
        source_str = self.source if isinstance(self.source, str) else repr(self.source)
        output = "%r, as referenced by %s, is expected to have %r, but only has %r" % (self.component, source_str, self.required_properties, self.actual_capabilities)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Cannot find any Components with %r" % (self.pattern,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r, %r attempted to reference a disallowed reference Component" % (self.component, self.field)
        if self.subcomponent_name is not None: output += " \"%s\"" % (self.subcomponent_name,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Key \"%s\" is not a recognized property" % (self.property,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Component at \"%s\", as referenced by %s, is unrecognized" % (self.component_type_str, self.source_str)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Component group \"%s\", as referenced by %s, is unrecognized" % (self.component_group_str, self.source_str)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Component type \"%s\", as referenced by %s, is unrecognized" % (self.component_type_str, self.source_str)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Object %r of type %s cannot be encoded to JSON" % (self.source, self.source.__class__.__name__)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class CustomJsonTestFailError(CustomJsonException):
    "A test of CustomJsonException has failed."

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
        output = "Invalid $special_type of \"%s\" received" % (self.special_type)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r cannot be written if not yet read" % (self.source,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerException(Exception):
    "Abstract Exception class for errors relating to DataMiners."

class DataMinerAccessorWrongTypeError(DataMinerException):
    "The assumed type of an Accessor is not its actual type."

    def __init__(self, dataminer:"DataMiner.DataMiner", file_type:str, accessor_type:type["Accessor.Accessor"], message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner that attempted to access its Accessor.
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
        output = "VersionFile \"%s\" from %r should have accessor with type \"%s\"" % (self.file_type, self.dataminer, self.accessor_type.__name__)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerAdditionalSerializerError(DataMinerException):
    "This DataMiner has been provided with an additional, unnecessary Serializer."

    def __init__(self, dataminer_settings:"DataMinerSettings.DataMinerSettings", dataminer_class:type["DataMiner.DataMiner"], key:str, serializer:"Serializer.Serializer", allowed_keys:set[str], message:Optional[str]=None) -> None:
        '''
        :dataminer_settings: The DataMinerSettings that provided the additional Serializer.
        :dataminer_class: The class of DataMiner that the DataMinerSettings has that does not support the key.
        :key: The key of the additional Serializer.
        :serializer: The additional Serializer.
        :allowed_keys: The set of Serializer keys that are allowed in this DataMiner.
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
        output = "%r provided additional Serializer key \"%s\": %r to DataMiner class \"%s\", which only supports keys [%s]" % (self.dataminer_settings, self.key, self.serializer, self.dataminer_class, ", ".join(sorted(self.allowed_keys)))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerCollectionFileError(DataMinerException):
    "The \"files\" key in a DataMinerCollection is improperly specified."

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
        if self.exists:
            output = "Key \"files\" of %r cannot exist" % (self.source,)
        else:
            output = "Key \"files\" of %r must exist" % (self.source,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerDependencyOverwriteError(DataMinerException):
    "Attempted to set an item of a DataMinerDependencies object that already exists."

    def __init__(self, dataminer_dependencies:"DataMinerEnvironment.DataMinerDependencies", dependency_name:str, message:Optional[str]=None) -> None:
        '''
        :dataminer_dependencies: The DataMinerDependencies that had an item overwritten.
        :dependency_name: The dependency that was overwritten.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_dependencies, dependency_name, message)
        self.dataminer_dependencies = dataminer_dependencies
        self.dependency_name = dependency_name
        self.message = message

    def __str__(self) -> str:
        output = "Attempted to overwrite dependency \"%s\" of %r" % (self.dependency_name, self.dataminer_dependencies)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerDuplicateFileNameError(DataMinerException):
    "Two DataMinerCollections have the same file name."

    def __init__(self, file_name:str, dataminers:list["DataMinerCollection.DataMinerCollection"], message:Optional[str]=None) -> None:
        '''
        :file_name: The file name shared by all of the DataMinerCollections.
        :dataminers: The DataMinerCollections that share the same file name.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_name, dataminers, message)
        self.file_name = file_name
        self.dataminers = dataminers
        self.message = message

    def __str__(self) -> str:
        output = "DataMinerCollections [%s] all have the same file name \"%s\"" % (", ".join(dataminer.name for dataminer in self.dataminers), self.file_name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerFileTypePermissionError(DataMinerException):
    "A DataMiner attempted to access an VersionFileType it has no permissions to use."

    def __init__(self, dataminer:"DataMiner.DataMiner", file_type_name:str, allowed_file_types:Optional[list[str]]=None, message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner that attempted to access a VersionFileType without permission.
        :file_type_name: The name of the VersionFileType it attempted to access.
        :allowed_file_types: A list of all VersionFileType names this DataMiner is allowed to access.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, file_type_name, allowed_file_types, message)
        self.dataminer = dataminer
        self.file_type_name = file_type_name
        self.allowed_file_types = allowed_file_types
        self.message = message

    def __str__(self) -> str:
        output = "%r attempted to access VersionFileType %s; permissions are lacking or it does not exist" % (self.dataminer, self.file_type_name)
        if self.message is not None:
            output += " %s" % (self.message,)
        if self.allowed_file_types is None:
            output += "!"
        else:
            output += ". It may only access %s!" % (self.allowed_file_types,)
        return output

class DataMinerLacksActivateError(DataMinerException):
    "A DataMiner did not override the activate function."

    def __init__(self, dataminer:"DataMiner.DataMiner", message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner that is missing the activate function.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        output = "%r is missing its activate function" % (self.dataminer,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerNothingFoundError(DataMinerException):
    "This DataMiner found nothing."

    def __init__(self, dataminer:"DataMiner.DataMiner", message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner that failed to find anything.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        output = "%r failed to find anything" % (self.dataminer,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerNullReturnError(DataMinerException):
    "The DataMiner's activate method has returned None."

    def __init__(self, dataminer:"DataMiner.DataMiner", message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner whose activate method returned None.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        output = "%r returned None upon being activated" % (self.dataminer)
        if self.message is None:
            output += "!"
        else:
            output += " %s" % (self.message,)
        return output

class DataMinerReadFilesError(DataMinerException):
    "The DataMiner failed to read files."

    def __init__(self, dataminer:"DataMiner.DataMiner", message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner that failed to read files.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, message)
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        output = "%r failed to read files" % (self.dataminer,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerSerializerMissingError(DataMinerException):
    "A DataMiner class requires a Serializer and does not have one."

    def __init__(self, dataminer_settings:"DataMinerSettings.DataMinerSettings", dataminer_type:type["DataMiner.DataMiner"], serializer_key:str, message:Optional[str]=None) -> None:
        '''
        :dataminer_settings: The DataMinerSettings whose DataMiner type requires a Serializer.
        :dataminer_type: The DataMinerSettings' DataMiner type.
        :serializer_key: The key of the missing Serializer.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_settings, dataminer_type, serializer_key, message)
        self.dataminer_settings = dataminer_settings
        self.dataminer_type = dataminer_type
        self.serializer_key = serializer_key
        self.message = message

    def __str__(self) -> str:
        output = "DataMiner type \"%s\" from %r requires is missing Serializer \"%s\"" % (self.dataminer_type.__name__, self.dataminer_settings, self.serializer_key)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerSettingsImporterLoopError(DataMinerException):
    "A DataMinerSettings has an import loop."

    def __init__(self, dataminer_settings:"DataMinerSettings.DataMinerSettings", loop_items:list[str], message:Optional[str]=None) -> None:
        '''
        :dataminer_settings: The initial DataMinerSettings containing the loop.
        :loop_items: A list of DataMinerCollection names contained in the loop.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_settings, loop_items, message)
        self.dataminer_settings = dataminer_settings
        self.loop_items = loop_items
        self.message = message

    def __str__(self) -> str:
        output = "%r has an import loop involving %s" % (self.dataminer_settings, self.loop_items)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinersFailureError(DataMinerException):
    "Multiple DataMiners failed to activate."

    def __init__(self, version:"Version.Version", dataminer_collections:list["DataMinerCollection.DataMinerCollection"], message:Optional[str]=None) -> None:
        '''
        :version: The Version for which datamining failed.
        :dataminer_collections: The DataMinerCollections that failed to activate on this Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, dataminer_collections, message)
        self.version = version
        self.dataminer_collections = dataminer_collections
        self.message = message

    def __str__(self) -> str:
        output = "Failed to datamine %r on DataMiners [%s]" % (self.version, ", ".join(dataminer_collection.name for dataminer_collection in self.dataminer_collections))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerUnrecognizedSerializerError(DataMinerException):
    "Called `export_file` on a DataMiner with no Serializer"

    def __init__(self, dataminer:"DataMiner.DataMiner", key:str, message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner missing a Serializer.
        :key: The key that attempted to access the Serializer.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, key, message)
        self.dataminer = dataminer
        self.key = key
        self.message = message

    def __str__(self) -> str:
        output = "Attempted to call `export_file` on %r using non-existent Serializer key \"%s\"" % (self.dataminer, self.key)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerUnrecognizedDependencyError(DataMinerException):
    "A dependency does not exist."

    def __init__(self, dataminer:"DataMiner.DataMiner", dependency_name:str, message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner attempting to access the dependency.
        :dependency_name: The name of the DataMinerCollection that does not exist.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, dependency_name, message)
        self.dataminer = dataminer
        self.dependency_name = dependency_name
        self.message = message

    def __str__(self) -> str:
        output = "%r references dependency \"%s\" that is non-existent for this Version" % (self.dataminer, self.dependency_name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerUnrecognizedSuffixError(DataMinerException):
    "A file suffix is unrecognized."

    def __init__(self, dataminer:"DataMiner.DataMiner", path:str, recognized_suffixes:list[str], message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner that found the unrecognized suffix.
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
        output = "%r found unrecognized suffix on path \"%s\"; it is not in %s" % (self.dataminer, self.path, self.recognized_suffixes)
        if self.message is None:
            output += "!"
        else:
            output += "; %s!" % (self.message,)
        return output

class DataMinerUnregisteredDependencyError(DataMinerException):
    "The dependency exists, but is not listed as a dependency by this DataMiner."

    def __init__(self, dataminer:"DataMiner.DataMiner", dependency_name:str, message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner attempting to access the dependency.
        :dependency_name: The name of the DataMinerCollection that is unregistered.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, dependency_name, message)
        self.dataminer = dataminer
        self.dependency_name = dependency_name
        self.message = message

    def __str__(self) -> str:
        output = "%r references unlisted dependency \"%s\"" % (self.dataminer, self.dependency_name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class MissingDataFileError(DataMinerException):
    "The data file for this DataMinerCollection is missing."

    def __init__(self, dataminer:Union["DataMiner.DataMiner", "DataMinerSettings.DataMinerSettings", "DataMinerCollection.DataMinerCollection"], file_name:str, version:Optional["Version.Version"], message:Optional[str]=None) -> None:
        '''
        :dataminer_collection: The DataMiner, DataMinerSettings, or DataMinerCollection that is missing its file.
        :file_name: The name of the file that's missing.
        :version: The Version for which this DataMiner is missing its file.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, version, file_name, message)
        self.dataminer = dataminer
        self.version = version
        self.file_name = file_name
        self.message = message

    def __str__(self) -> str:
        output = "File %s of %s" % (self.file_name, self.dataminer)
        if self.version is not None:
            output += " of Version \"%s\"" % (self.version.name,)
        if self.message is None:
            output += " is missing!"
        else:
            output += " is missing %s!" % (self.message,)
        return output

class NullDataMinerMethodError(DataMinerException):
    "An invalid exception has been called on a NullDataMiner."

    def __init__(self, dataminer:"DataMiner.NullDataMiner", method:Callable, message:Optional[str]=None) -> None:
        '''
        :dataminer: The NullDataMiner that an invalid method was called on.
        :method: The method that was called on the NullDataMiner.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, method, message)
        self.dataminer = dataminer
        self.method = method
        self.message = message

    def __str__(self) -> str:
        output = "Attempted to call method \"%s\" on %r" % (self.method.__name__, self.dataminer)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class SoundFilesExtractionError(DataMinerException):
    "Failure to extract from an FSB file."

    def __init__(self, exit_code:int, message:Optional[str]=None) -> None:
        '''
        :exit_code: The exit code that the extraction executable returned.
        :message: Additional text to place after the main message.
        '''
        super().__init__(exit_code, message)
        self.exit_code = exit_code
        self.message = message

    def __str__(self) -> str:
        output = "Failed to extract FSB file; returned exit code %i" % (self.exit_code,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class SoundFilesMetadataError(DataMinerException):
    "audio_metadata failed to extract the sound file."

    def __init__(self, message:Optional[str]=None) -> None:
        '''
        :message: Additional text to place after the main message.'''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        output = "audio_metadata failed to extract a file"
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class TagSearcherDependencyError(DataMinerException):
    "A tag exists in a DataMiner that is not a dependency of this one."

    def __init__(self, dataminer:"DataMiner.DataMiner", tag:"StructureTag.StructureTag", dataminer_collection:"DataMinerCollection.DataMinerCollection", message:Optional[str]=None) -> None:
        '''
        :dataminer: The DataMiner that attempted to access the tag.
        :tag: The tag that was found in an inaccessible DataMinerCollection.
        :dataminer_collection: The DataMinerCollection the tag was found in.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer, tag, dataminer_collection, message)
        self.dataminer = dataminer
        self.tag = tag
        self.dataminer_collection = dataminer_collection
        self.message = message

    def __str__(self) -> str:
        output = "%r could find %r in %r, but it is not a dependency" % (self.dataminer, self.tag, self.dataminer_collection)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class TagSearcherParseError(DataMinerException):
    "Failed to parse a TagSearcher expression."

    def __init__(self, data_reader:"TagSearcherDataMiner.DataReader", reason:str, message:Optional[str]=None) -> None:
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
        output = "%s at position %i of expression \"%s\"" % (self.reason, self.data_reader.position, self.data_reader.data)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class UnrecognizedPackError(DataMinerException):
    "The behavior pack/resource pack is not recognized."

    def __init__(self, pack:str|list[str], pack_type:Literal["behavior", "resource", "skin", "emote", "piece", "pack"], source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :pack: The name(s) of the behavior pack/resource pack(s).
        :pack_type: The type of pack ("behavior", "resource", "skin", "emote", "piece", or "pack").
        :source: The object that found the behavior pack/resource pack.
        :message: Additional text to place after the main message.
        '''
        super().__init__(pack, pack_type, source, message)
        self.pack = pack
        self.pack_type = pack_type
        self.source = source
        self.message = message

    def __str__(self) -> str:
        match self.pack_type:
            case "behavior":
                pack_string = "Behavior pack"
            case "resource":
                pack_string = "Resource pack"
            case "skin":
                pack_string = "Skin pack"
            case "emote":
                pack_string = "Emote directory"
            case "piece":
                pack_string = "Piece directory"
            case _:
                pack_string = "Pack"
        output = "%s " % (pack_string,)
        output = "\"%s\"" % (self.pack,) if isinstance(self.pack, str) else "[%s]" % (", ".join("\"%s\"" % pack for pack in self.pack))
        if self.source is not None:
            output += ", found by %r," % (self.source,)
        output += " is not recognized"
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DelegateException(Exception):
    "Abstract Exception class for errors relating to Delegates."

class InapplicableDelegateError(DelegateException):
    "The Structure or StructureBase a Delegate is applied to does not suit the Delegate."

    def __init__(
        self,
        delegate_type:type["Delegate.Delegate"],
        structure:Union["Structure.Structure", "StructureBase.StructureBase"],
        allowed_types:tuple[type[Union["Structure.Structure", "StructureBase.StructureBase", None]], ...],
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
        output = "Delegate type \"%s\" can only be applied to types [%s], not %r" % (self.delegate_type.__name__, ", ".join("\"%s\"" % allowed_type.__name__ for allowed_type in self.allowed_types), self.structure)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class UnrecognizedDelegateError(DelegateException):
    "A Delegate type is unrecognized."

    def __init__(self, delegate_type_str:str, source_str:str, message:Optional[str]=None) -> None:
        '''
        :delegate_type_str: The name of the unrecognized Delegate type.
        :source_str: The object that refers to this Delegate type.
        :message: Additional text to place after the main message.
        '''
        super().__init__(delegate_type_str, source_str, message)
        self.delegate_type_str = delegate_type_str
        self.source_str = source_str
        self.message = message

    def __str__(self) -> str:
        output = "Delegate type \"%s\" is not recognized by %s" % (self.delegate_type_str, self.source_str)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ManagerException(Exception):
    "Abstract Exception class for errors relating to Managers."

class DownloadManagerFailError(ManagerException):
    "A DownloadManager failed to download a file."

    def __init__(self, manager:"Manager.Manager", url:str, file:Optional[str]=None, message:Optional[str]=None) -> None:
        '''
        :manager: The Manager that failed to download a file.
        :url: The url from which the file comes from.
        :file: The name of the file that could not be downloaded.
        :message: Additional text to place after the main message.
        '''
        super().__init__(manager, url, file, message)
        self.manager = manager
        self.url = url
        self.file = file
        self.message = message

    def __str__(self) -> str:
        output = "%r failed to download file" % (self.manager,)
        if self.file is not None:
            output += " \"%s\"" % (self.file,)
        output += " from \"%s\"" % (self.url)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ManagerUndefinedMethodError(ManagerException):
    "A Manager has a method that is not overridden by a subclass."

    def __init__(self, manager:"Manager.Manager", function:Callable, message:Optional[str]=None) -> None:
        '''
        :manager: The Manager that has a method that is not overridden.
        :function: The function that was not overridden.
        :message: Additional text to place after the main message.
        '''
        super().__init__(manager, function, message)
        self.manager = manager
        self.function = function
        self.message = message

    def __str__(self) -> str:
        output = "Method %s of %r was not overridden" % (self.function.__name__, self.manager)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class UnrecognizedManagerError(DataMinerException):
    "The Manager string is not recognized."

    def __init__(self, manager_str:str, source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :manager_str: The Manager string that does not correspond to any Manager.
        :source: The object attempting to reference this Manager.
        :message: Additional text to place after the main message.
        '''
        super().__init__(manager_str, source, message)
        self.source = source
        self.manager_str = manager_str
        self.message = message

    def __str__(self) -> str:
        output = "Manager \"%s\"" % (self.manager_str)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        if self.message is None:
            output += " does not exist!"
        else:
            output += " does not exist %s!" % (self.message,)
        return output

class NbtException(Exception):
    "Abstract Exception class for errors relating to NBT."

class NbtParseException(NbtException):
    "Abstract Exception class for errors relating to the parsing of NBT from bytes."

class CompoundDuplicateKeyError(NbtParseException):
    "A TAG_Compound has a duplicate key."

    def __init__(self, key:str, message:Optional[str]=None) -> None:
        '''
        :key: The key that was duplicated.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, message)
        self.key = key
        self.message = message

    def __str__(self) -> str:
        output = "A TAG_Compound has a duplicate key \"%s\"" % (self.key,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class InvalidNbtContentType(NbtParseException):
    "An NBT tag has an invalid content type."

    def __init__(self, content_type:int, message:Optional[str]=None) -> None:
        '''
        :content_type: The content type ID.
        :message: Additional text to place after the main message.
        '''
        super().__init__(content_type, message)
        self.content_type = content_type
        self.message = message

    def __str__(self) -> str:
        output = "Invalid NBT content type %i" % (self.content_type,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class NbtTestFailureError(NbtException):
    "An NBT test has failed."

class SnbtParseError(Exception):
    def __init__(self, message:str, reader:"SnbtParser.Reader", other_exceptions:list["SnbtParseError"]|None=None) -> None:
        super().__init__(message, reader.position, reader.stack, other_exceptions)

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
        output = "Invalid file suffix \"%s\" on file \"%s\"" % (self.suffix, self.name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r in %r should be one of types [%s] instead of type \"%s\"" % (self.object, self.script, ", ".join("\"%s\"" % (allowed_type.__name__) for allowed_type in self.allowed_types), type(self.object))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class ScriptedClassMissingInheritError(ScriptException):
    "A scripted type failed to correctly inherit."

    def __init__(self, class_name:str, message:Optional[str]=None) -> None:
        '''
        :class_name: The name of the type class that failed to inherit.
        :message: Additional text to place after the main message.
        '''
        super().__init__(class_name, message)
        self.class_name = class_name
        self.message = message

    def __str__(self) -> str:
        output = "Scripted class \"%s\" is missing the \"inherit\" key" % (self.class_name,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r failed to load" % (self.script,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Scripts on paths \"%s\" and \"%s\" have the same stem" % (self.script_path1, self.script_path2)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Unrecognized Script \"%s\"" % (self.script_name,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class WrongScriptError(ScriptException):
    "Attempted to import a Script that exists, but cannot be used in this situation."
    
    def __init__(self, script:"Scripts.Script", message:Optional[str]=None) -> None:
        '''
        :script: The Script that cannot be used in this situation:
        :message: Additional text to place after the main message.
        '''
        super().__init__(script, message)
        self.script = script
        self.message = message
    
    def __str__(self) -> str:
        output = "Cannot load %r in this situation" % (self.script,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class SerializerException(Exception):
    "Abstract Exception class for errors relating to Serializers"

class MediaSerializerFailedError(SerializerException):
    "MediaSerializer has \"Error\" in its output."

    def __init__(self, serializer:"Serializer.Serializer", error_message:str, message:Optional[str]=None) -> None:
        '''
        :serializer: The MediaSerializer that failed.
        :error_message: The content of the "Error" key.
        :message: Additional text to place after the main message.
        '''
        super().__init__(serializer, error_message, message)
        self.serializer = serializer
        self.error_message = error_message
        self.message = message

    def __str__(self) -> str:
        output = "%r gave error \"%s\"" % (self.serializer, self.error_message)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r failed to serialize file \"%s\"" % (self.serializer, self.file_name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r is missing method %s" % (self.serializer, self.method.__name__)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class UnrecognizedSerializerInFileError(SerializerException):
    "A Serializer's name in a stored File does not exist."

    def __init__(self, file_data:"CustomJson.FileTypedDict", message:Optional[str]=None) -> None:
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
        output = "Attempted to create File with name \"%s\" and hash \"%s\" using non-existent Serializer \"%s\"" % (self.name, self.hash, self.serializer)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class StructureException(Exception):
    "Abstract Exception class for errors relating to Structures"

class CacheStructureHashError(StructureException):
    "A CacheStructure failed to hash an unknown type."

    def __init__(self, unhashable_type:type, message:Optional[str]=None) -> None:
        '''
        :unhashable_type: The type that could not be hashed.
        :message: Additional text to place after the main message.
        '''
        super().__init__(unhashable_type, message)
        self.unhashable_type = unhashable_type
        self.message = message

    def __str__(self) -> str:
        output = "Failed to hash %r" % (self.unhashable_type,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class CompareWithNoneError(StructureException):
    "A StructureSet attempted to compare data using None instead of a Structure."

    def __init__(self, structure:Union["Structure.Structure", "StructureSet.StructureSet"], key:Union[int, None]=None, message:Optional[str]=None) -> None:
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
        if self.key is None:
            output = "Attempted to compare with %r using a NoneType object" % (self.structure,)
        else:
            output = "Attempted to compare with key %s on %r using a NoneType object" % (self.key, self.structure)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has no non-None versions" % (self.environment,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Attempted to create a Diff with branch %i overlapping with one of [%s]" % (self.overlapping_branches, ", ".join(str(branch) for branch in self.all_branches))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has no items besides NoExist" % (self.diff,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DiffKeyError(StructureException):
    "The Diff object does not have anything at the position indexed."

    def __init__(self, index:int|tuple[int,...], diff:"D.Diff[a]", message:Optional[str]=None) -> None:
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
        output = "%r does not have an item at index %s" % (self.diff, self.index)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DiffLengthError(StructureException):
    "Attempted to create a multi-Diff with a length that does not match the correct length"

    def __init__(self, current_length:int, desired_length:int, message:Optional[str]=None) -> None:
        '''
        :current_length: The number of items attempting to be made into a diff.
        :desired_length: The length that the items should be.
        :message: Additional text to place after the main message.
        '''
        super().__init__(current_length, desired_length, message)
        self.current_length = current_length
        self.desired_length = desired_length
        self.message = message

    def __str__(self) -> str:
        output = "Attempted to create a diff with with a length of %i instead of %i" % (self.current_length, self.desired_length)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DiffsLengthError(StructureException):
    "Two Diffs cannot be zipped because of different lengths."

    def __init__(self, diff1:"D.Diff", diff2:"D.Diff", message:Optional[str]=None) -> None:
        '''
        :diff1: The first Diff attempted to be zipped.
        :diff2: The second Diff attempted to be zipped.
        :message: Additional text to place after the main message.
        '''
        super().__init__(diff1, diff2, message)
        self.diff1 = diff1
        self.diff2 = diff2
        self.message = message

    def __str__(self) -> str:
        output = "Cannot zip %r is [0, %i) and %r is [0, %i)" % (self.diff1, len(self.diff1), self.diff2, len(self.diff2))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Data %s at path %s of %r of %r is not a valid file hash" % (self.data_path.embedded_data, self.data_path, self.structure_tag, self.version)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has a similarity of %.4f" % (self.structure, self.similarity)
        output += ": " if self.message is None else " %s: " % (self.message,)
        output += "on data %s and %s" % (self.data1, self.data2)
        return output

class NormalizerNoneError(StructureException):
    "A Normalizer has returned None where it should return something."

    def __init__(self, normalizer:"Normalizer.Normalizer", source:object, message:Optional[str]=None) -> None:
        super().__init__(normalizer, source, message)
        self.normalizer = normalizer
        self.source = source
        self.message = message

    def __str__(self) -> str:
        output = "%r, as referenced by %r, returned None when it shouldn't have" % (self.normalizer, self.source)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r attempted to compare/get similarity of data too long: first is %i long; second is %i long" % (self.structure, self.len1, self.len2)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Failed to compare on Structures [%s]" % (", ".join(self.structure_names))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class StructureCannotPrintFlatError(StructureException):
    "Some data cannot be printed on a single line."

    def __init__(self, message:Optional[str]=None) -> None:
        '''
        :message: Additional text to place after the main message.
        '''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        output = "Data cannot be printed flat"
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has failed" % (self.structure_base,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has errors in function \"%s\" where it should not" % (self.structure, self.function.__name__)
        output += ": " if self.message is None else " %s: " % (self.message,)
        output += "[%s]" % (", ".join(exception.finalize().stringify() for exception in self.exceptions))
        return output

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
        output = "Required key \"%s\" from %r is missing" % (self.key, self.structure)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%s must have a type of one of [%s], not \"%s\"" % (self.label, ", ".join("\"%s\"" % required_type.__name__ for required_type in self.required_types), self.actual_type.__name__)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%s \"%s\" is not recognized" % (self.label, self.unrecognized_key)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Cannot perform function \"%s\" on %r due to it being " % (self.function.__name__, self.trace)
        if self.is_finalized:
            output += "finalized"
        else:
            output += "not finalized"
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Unrecognized tag \"%s\" referenced in expression \"%s\"" % (self.tag_name, self.expression)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class VolumeStructureAdditionalDataError(StructureException):
    "The VolumeStructure cannot print a layer because unexpected additional data exists."

    def __init__(self, structure:"Structure.Structure", message:Optional[str]=None) -> None:
        '''
        :structure: The VolumeStructure.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure, message)
        self.structure = structure
        self.message = message

    def __str__(self) -> str:
        output = "%r does not expect additional data" % (self.structure,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class VolumeStructureMissingKeyError(StructureException):
    "The VolumeStructure is missing its position or state key."

    def __init__(self, key_type:Literal["Position", "State"], key:str, block:int, message:Optional[str]=None) -> None:
        '''
        :key_type: If the key is a position key or a state key.
        :key: The key that is missing.
        :block: The index of the block with the missing key.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key_type, key, block, message)
        self.key_type = key_type
        self.key = key
        self.block = block
        self.message = message

    def __str__(self) -> str:
        output = "%s key \"%s\" is missing in block %i" % (self.key_type, self.key, self.block)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class VolumeStructureInvalidKeyError(StructureException):
    "The position or state of a VolumeStructure is invalid."

    def __init__(self, key_type:Literal["Position", "State"], value:Any, block:int, message:str="is invalid") -> None:
        '''
        :key_type: If the key is a position key or a state key.
        :value: The value of the key for this block.
        :block: The index of the block.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key_type, value, block, message)
        self.key_type = key_type
        self.value = value
        self.block = block
        self.message = message

    def __str__(self) -> str:
        return "%s \"%s\" in block %i %s!" % (self.key_type, self.value, self.block, self.message)

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
        output = "%r failed verification" % (self.type_verifier,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class TypeVerifierDisallowedError(TypeVerifierException):
    "A TypeVerifier appears in an invalid spot in a JSON TypeVerifier."

    def __init__(self, data:"TypeVerifierImporter.TypedVerifierTypedDicts", message:Optional[str]=None) -> None:
        '''
        :data: The type field that contains a disallowed TypeVerifier.
        :message: Additional text to place after the main message.
        '''
        super().__init__(data, message)
        self.data = data
        self.message = message

    def __str__(self) -> str:
        output = "Type field %s contains a TypeVerifier and should not" % (self.data,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        return "%s is not one of %s, but instead %s!" % (self.trace.to_str(), self.options, self.value)

class TypeVerificationFunctionError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace", message:str|None, data:Any|None=None) -> None:
        super().__init__(trace, message, data)
        self.message = message
        self.data = data

    def __str__(self) -> str:
        if self.message is None:
            if self.data is None:
                return "%s failed verification!" % (self.trace.to_str())
            else:
                return "%s (data %s) failed verification!" % (self.trace.to_str(), self.data)
        else:
            if self.data is None:
                return "%s failed verification due to \"%s\"!" % (self.trace.to_str(), self.message)
            else:
                return "%s (data %s) failed verification due to \"%s\"!" % (self.trace.to_str(), self.data, self.message)

class TypeVerificationMissingKeyError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace") -> None:
        super().__init__(trace)

    def __str__(self) -> str:
        return "Required %s is missing!" % (self.trace.to_str(capitalize=False))

class TypeVerificationTypeError(TypeVerificationTypeException):

    def __init__(self, trace: "TypeVerifier.Trace", expected_type:str, observed_type:type) -> None:
        super().__init__(trace, expected_type, observed_type)
        self.expected_type = expected_type
        self.observed_type = observed_type

    def __str__(self) -> str:
        return "%s is not %s, but instead %s!" % (self.trace.to_str(), self.expected_type, self.observed_type.__name__)

class TypeVerificationUnionError(TypeVerificationTypeException):

    def __init__(self, trace: "TypeVerifier.Trace", expected_type:str, observed_type:type, causes:list[list[TypeVerificationTypeException]]) -> None:
        super().__init__(trace, expected_type, observed_type, causes)
        self.expected_type = expected_type
        self.observed_type = observed_type
        self.causes = causes

    def __str__(self) -> str:
        return "%s is not %s, but instead %s due to %s!" % (self.trace.to_str(), self.expected_type, self.observed_type.__name__, [[str(exception) for exception in exception_list] for exception_list in self.causes])

class TypeVerificationUnrecognizedKeyError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace") -> None:
        super().__init__(trace)

    def __str__(self) -> str:
        return "%s is an unrecognized key!" % (self.trace.to_str())

class TypeVerificationWrongLengthError(TypeVerificationTypeException):

    def __init__(self, trace:"TypeVerifier.Trace", expected_length:int, observed_length:int) -> None:
        super().__init__(trace, expected_length, observed_length)
        self.expected_length = expected_length
        self.observed_length = observed_length

    def __str__(self) -> str:
        return "%s is not length %i, but instead length %i!" % (self.trace.to_str(), self.expected_length, self.observed_length)

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
        output = "%r is duplicated in " % (self.tag,)
        if isinstance(self.key, tuple):
            output += "keys [%s] of VersionTagOrder" % (", ".join("\"%s\"" % key for key in self.key),)
        else:
            output += "key \"%s\" of VersionTagOrder" % (self.key,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has an invalid parent %r" % (self.version, self.parent)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has an invalid time %s because %s" % (self.version, self.time, self.reason)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "No ordering tags found within %r's tags: %s" % (self.version, self.version_tags)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r was not used in " % (self.tag,)
        if isinstance(self.key, tuple):
            output += "keys [%s] of VersionTagOrder" % (", ".join("\"%s\"" % key for key in self.key))
        else:
            output += "key \"%s\" of VersionTagOrder" % (self.key,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r is not an ordering tag" % (self.tag,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r cannot exist when %r is unreleased" % (self.version_file, self.version)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r (tag %r), child of %r (tag %r) is not a valid child type of a %r"% (self.child_version, self.child_tag, self.parent_version, self.parent_tag, self.parent_tag)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r is a child of multiple top-level Versions" % (self.version,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "The children of %r, [%s], are in an invalid order at child %r" % (self.version, (child_tag.name for child_tag in self.child_tags), self.error_child)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r lacks ordering VersionTags, only has [%s]" % (self.version)
        if self.count == 0:
            output += "lacks ordering VersionTags, only has [%s]" % (", ".join(tag.name for tag in self.tags))
        else:
            output += "has too many ordering VersionTags, has [%s]" % (", ".join(tag.name for tag in self.tags))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Child %r (tag %r) of %r (tag %r) comes %s the latter" % (self.child_version, self.child_tag, self.parent_version, self.parent_tag, self.time_text)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Version \"%s\" is not within the VersionRange " % (self.version,)
        if self.version_range is not None:
            output += "%r" % (self.version_range,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class VersionRangeOrderError(VersionException):
    "The old and new Versions of a VersionRange are switched."

    def __init__(
        self,
        version_range:Union["VersionRange.VersionRange", "VersionRangeField.VersionRangeField"],
        start_version:Union["Version.Version", "VersionComponent.VersionComponent"],
        stop_version:Union["Version.Version", "VersionComponent.VersionComponent"],
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
        output = "The Versions of %r, %r (start) and %r (stop), are switched" % (self.version_range, self.start_version, self.stop_version)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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

class VersionTimeTravelError(VersionException):
    "A Version's children are not in order chronologically."

    def __init__(self, previous_child:"Version.Version", previous_time:datetime.date|datetime.datetime, current_child:"Version.Version", current_time:datetime.date|datetime.datetime, parent:"Version.Version", message:Optional[str]=None) -> None:
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
        output = "Date of child %r (%s) comes after date of child %r (%s) despite being before it in the children of %r" % (self.previous_child, self.previous_time, self.current_child, self.current_time, self.parent)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r is a top-level Version, but does not have the top-level %r" % (self.version, self.top_level_tag)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "Required %r is missing in %r" % (self.file_type, self.version)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r does not recognize accessor \"%s\"" % (self.version_file, self.accessor_str)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r has no available Accessors" % (self.version_file,)
        if self.version_file.has_accessors():
            output += " from [%s]" % (repr(accessor) for accessor in self.version_file.get_accessors())
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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
        output = "%r is not an auto-assigning VersionFileType" % (self.version_file_type,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output
