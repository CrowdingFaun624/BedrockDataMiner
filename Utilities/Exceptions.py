import datetime
from typing import (TYPE_CHECKING, Any, Callable, Container, Literal, Optional,
                    Union)

if TYPE_CHECKING:
    import DataMiners.DataMiner as DataMiner
    import DataMiners.DataMinerCollectionImporter as DataMinerCollectionImporter
    import DataMiners.TagSearcher.TagSearcherDataMiner as TagSearcherDataMiner
    import Downloader.Manager as Manager
    import Structure.Difference as D
    import Structure.Importer.Capabilities as Capabilities
    import Structure.Importer.Component as Component
    import Structure.Importer.Pattern as Pattern
    import Structure.Normalizer as Normalizer
    import Structure.Structure as Structure
    import Structure.StructureBase as StructureBase
    import Structure.StructureSet as StructureSet
    import Structure.Trace as Trace
    import Utilities.FileManager as FileManager
    import Utilities.Nbt.NbtReader as NbtReader
    import Utilities.Nbt.SnbtParser as SnbtParser
    import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
    import Utilities.TypeVerifier.TypeVerifierImporter as TypeVerifierImporter
    import Version.Version as Version
    import Version.VersionFile as VersionFile
    import Version.VersionFileType as VersionFileType
    import Version.VersionRange as VersionRange
    import Version.VersionTags as VersionTags

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

    def __init__(self, file:"FileManager.FilePromise", message:Optional[str]=None) -> None:
        '''
        :file: The FilePromise that was opened to reveal no bytes.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file, message)
        self.file = file
        self.message = message

    def __str__(self) -> str:
        output = "File %r has no bytes"
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
        output = "File with hash \"%s\" does not exist!" % (self.unknown_hash,)
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

class OpenAllDoneFilePromiseError(Exception):
    "Attempted to open a FilePromise for which all_done has already been called."

    def __init__(self, file_promise:"FileManager.FilePromise", message:Optional[str]=None) -> None:
        '''
        :file_promise: The FilePromise that was already marked as all done.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_promise, message)
        self.file_promise = file_promise
        self.message = message

    def __str__(self) -> str:
        output = "Cannot open %r due to it already being marked as all done" % (self.file_promise,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class AccessorException(Exception):
    "Abstract Exception class for errors relating to Accessors."

class AccessorTypeInheritUnrecognizedAccessorTypeError(AccessorException):
    "A scripted AccessorType attempts to subclass an unknown built-in AccessorType"

    def __init__(self, class_name:str, superclass_name:str, message:Optional[str]=None) -> None:
        '''
        :class_name: The name of the AccessorType that attempts to inherit from an unknown AccessorType.
        :superclass_name: The name of the unrecognized AccessorType.
        :message: Additional text to place after the main message.
        '''
        super().__init__(class_name, superclass_name, message)
        self.class_name = class_name
        self.superclass_name = superclass_name
        self.message = message

    def __str__(self) -> str:
        output = "AccessorType \"%s\" attempts to subclass unrecognized built-in AccessorType \"%s\"" % (self.class_name, self.superclass_name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class AccessorTypeMissingInheritError(AccessorException):
    "A scripted AccessorType is missing the inherit key."

    def __init__(self, accessor_type_name:str, message:Optional[str]=None) -> None:
        '''
        :accessor_type_name: The name of the AccessorType missing the inherit key.
        :message: Additional text to place after the main message.
        '''
        super().__init__(accessor_type_name, message)
        self.accessor_type_name = accessor_type_name
        self.message = message

    def __str__(self) -> str:
        output = "Scripted AccessorType \"%s\" is missing the \"inherit\" key" % (self.accessor_type_name,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class UnrecognizedAccessorTypeError(AccessorException):
    "An AccessorType is not recognized."

    def __init__(self, accessor_type_str:str, source:Optional[object]=None, source_str:Optional[str]=None, message:Optional[str]=None) -> None:
        '''
        :accessor_type_str: The name of the unrecognized AccessorType.
        :source: The object that attempts to reference the unrecognized AccessorType; may be empty.
        :source_str: A string describing the object that attempts to reference the unrecognized AccessorType; may be empty.
        :message: Additional text to place after the main message.
        '''
        super().__init__(accessor_type_str, source, source_str, message)
        self.accessor_type_str = accessor_type_str
        self.source = source
        self.source_str = source_str
        self.message = message

    def __str__(self) -> str:
        output = "DataMiner \"%s\"" % (self.accessor_type_str)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        elif self.source_str is not None:
            output += ", as referenced by %s," % (self.source_str)
        if self.message is None:
            output += " does note exist!"
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
        output = "Type \"%s\", as referenced by %r, is duplicated!" % (self.type_str, self.source)
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

class ComponentImportNameClashError(ComponentException):
    "One Component and an imported Component's names are the same."

    def __init__(self, name:str, message:Optional[str]=None) -> None:
        '''
        :name: The name of the Components.
        :message: Additional text to place after the main message.
        '''
        super().__init__(name, message)
        self.name = name
        self.message = message

    def __str__(self) -> str:
        output = "Cannot import components with the same name, \"%s\"" % (self.name,)
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
        output = "Failed to parse Structure"
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

    def __init__(self, function_name:str, source_str:str, message:Optional[str]=None) -> None:
        '''
        :function_name: The name of the unrecognized function.
        :source_str: A string representing the object that references the function.
        :message: Additional text to place after the main message.
        '''
        super().__init__(function_name, source_str, message)
        self.function_name = function_name
        self.source_str = source_str
        self.message = message

    def __str__(self) -> str:
        output = "Function \"%s\", as referenced by %s, is unrecognized" % (self.function_name, self.source_str)
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

class GroupContainsNullSubcomponentsError(ComponentException):
    "An AbstractGroup contains null subcomponents in a situation where it is not allowed."

    def __init__(self, null_types:list[type], source:object, message:Optional[str]=None) -> None:
        '''
        :null_types: The types of the Group that have null subcomponents.
        :source: The object that references the Group.
        :message: Additional text to place after the main message.
        '''
        super().__init__(null_types, source, message)
        self.null_types = null_types
        self.source = source
        self.message = message

    def __str__(self) -> str:
        output = "%r cannot except Groups with subcomponent(s) of null; offenders are [%s]" % (self.source, ", ".join(null_type.__name__ for null_type in self.null_types))
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class InvalidComponentError(ComponentException):
    "The referenced Component has the wrong properties."

    def __init__(self, component:"Component.Component", source_str:str, required_properties:"Pattern.Pattern", actual_capabilities:"Capabilities.Capabilities", message:Optional[str]=None) -> None:
        '''
        :component: The Component that is being referenced.
        :source_str: A string representing the object that is referencing the Component.
        :required_properties: The Pattern that the Component is expected to have.
        :actual_capabilities: The Capabilities that the Component actually has.
        :message: Additional text to place after the main message.
        '''
        super().__init__(component, source_str, required_properties, actual_capabilities, message)
        self.component = component
        self.source_str = source_str
        self.required_properties = required_properties
        self.actual_capabilities = actual_capabilities
        self.message = message

    def __str__(self) -> str:
        output = "%r, as referenced by %s, is expected to have %r, but only has %r" % (self.component, self.source_str, self.required_properties, self.actual_capabilities)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class InvalidComponentTypeError(ComponentException):
    "The referenced Component has the wrong type."

    def __init__(self, component:"Component.Component", required_types:tuple[type,...], actual_type:type, message:Optional[str]=None) -> None:
        '''
        :component: The Component that has the wrong type.
        :required_types: The types that the Component is expected to have.
        :actual_type: The type that the Component actually has.
        :message: Additional text to place after hte main message.
        '''
        super().__init__(component, required_types, actual_type, message)
        self.component = component
        self.required_types = required_types
        self.actual_type = actual_type
        self.message = message

    def __str__(self) -> str:
        output = "%r is expected to have types [%s], but only has \"%s\"" % (self.component, ", ".join("\"%s\"" % required_type.__name__ for required_type in self.required_types), self.actual_type.__name__)
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
        output = "Component \"%s\", as referenced by %s, is unrecognized" % (self.component_type_str, self.source_str)
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
        output = "Invalid $special_type of \"%s\" received!" % (self.special_type)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerException(Exception):
    "Abstract Exception class for errors relating to DataMiners."

class DataMinerCollectionInvalidArgumentsError(DataMinerException):
    "The DataMinerCollection has invalid arguments in dataminer_collections.json."

    def __init__(self, dataminer_collection_intermediate:"DataMinerCollectionImporter.DataMinerCollectionIntermediate", message:Optional[str]=None) -> None:
        '''
        :dataminer_collection_intermediate: The DataMinerCollectionIntermediate that has invalid arguments.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_collection_intermediate, message)
        self.dataminer_collection_intermediate = dataminer_collection_intermediate
        self.message = message

    def __str__(self) -> str:
        output = "%s has invalid arguments" % (self.dataminer_collection_intermediate,)
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

class DataMinerFailureError(DataMinerException):
    "A DataMiner has failed for some reason."

    def __init__(self, dataminer:"DataMiner.DataMiner", *args: object) -> None:
        '''
        :dataminer: The DataMiner that failed.
        '''
        super().__init__(*args)
        self.dataminer = dataminer

    def __str__(self) -> str:
        return "%r failed: %s" % (self.dataminer, self.args)

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

class DataMinerKeywordArgumentsExistError(DataMinerException):
    "A DataMiner was supplied with keyword arguments, but `initialize` was not overridden."

    def __init__(self, kwargs:dict[str,Any], dataminer:"DataMiner.DataMiner", message:Optional[str]=None) -> None:
        '''
        :kwargs: The keyword arguments supplied to the DataMiner.
        :dataminer: The DataMiner the keyword arguments were supplied to.
        :message: Additional text to place after the main message.
        '''
        super().__init__(kwargs, dataminer, message)
        self.kwargs = kwargs
        self.dataminer = dataminer
        self.message = message

    def __str__(self) -> str:
        output = "DataMiner %r was supplied with non-empty kwargs" % (self.dataminer,)
        if self.message is None:
            output += ": "
        else:
            output += " %s:" % (self.message,)
        output += "\"%s\"" % self.kwargs
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

class DataMinerSettingsImporterLoopError(DataMinerException):
    "A DataMinerSettings has an import loop."

    def __init__(self, dataminer_settings:"DataMiner.DataMinerSettings", loop_items:list[str], message:Optional[str]=None) -> None:
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

class DataMinerSettingsInvalidVersionRangeException(DataMinerException):
    "Abstract exception class for errors relating to the Version ranges in a DataMinerSettings being invalid."

class DataMinerSettingsVersionRangeExists(DataMinerSettingsInvalidVersionRangeException):
    "The new/old Version of the first/last DataMinerSettings is not None."

    def __init__(self, dataminer_collection_intermediate:"DataMinerCollectionImporter.DataMinerCollectionIntermediate", actual_value:str, is_first:bool, message:Optional[str]=None) -> None:
        '''
        :dataminer_collection_intermediate: The DataMinerCollectionIntermediate with an invalid DataMinerSettings.
        :actual_value: The value that is present in the new Version instead of None.
        :is_first: Whether this DataMinerSettings is the newest one or not.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_collection_intermediate, actual_value, is_first, message)
        self.dataminer_collection_intermediate = dataminer_collection_intermediate
        self.actual_value = actual_value
        self.is_first = is_first
        self.message = message

    def __str__(self) -> str:
        first_last_text = ("new", "first") if self.is_first else ("old", "last")
        output = "The %s Version of the %s DataMinerSettings of %r is not None, but instead \"%s\"" % (first_last_text[0], first_last_text[1], self.dataminer_collection_intermediate, self.actual_value)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerSettingsVersionRangeGap(DataMinerSettingsInvalidVersionRangeException):
    "There is a gap in a DataMinerCollection's DataMinerSettings' Versions."

    def __init__(self, dataminer_collection_intermediate:"DataMinerCollectionImporter.DataMinerCollectionIntermediate", new_version:"Version.Version", old_version:"Version.Version", message:Optional[str]=None) -> None:
        '''
        :dataminer_collection_intermediate: The DataMinerCollectionIntermediate with invalid DataMinerSettings.
        :new_version: The Version on the newer side of the gap.
        :old_version: The Version on the older side of the gap.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_collection_intermediate, new_version, old_version, message)
        self.dataminer_collection_intermediate = dataminer_collection_intermediate
        self.new_version = new_version
        self.old_version = old_version
        self.message = message

    def __str__(self) -> str:
        output = "%r has a gap between Versions %s and %s" % (self.dataminer_collection_intermediate, self.new_version, self.old_version)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinerSettingsVersionRangeMissing(DataMinerSettingsInvalidVersionRangeException):
    "The new or old Version of a non-first DataMinerSettings is None."

    def __init__(self, dataminer_collection_intermediate:"DataMinerCollectionImporter.DataMinerCollectionIntermediate", index:int, slot:Literal["old", "new"], message:Optional[str]=None) -> None:
        '''
        :dataminer_collection_intermediate: The DataMinerCollectionIntermediate with an invalid DataMinerSettings.
        :index: The index of the DataMinerSettings
        :slot: The key ("old" or "new") of the DataMinerSettings.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_collection_intermediate, index, slot, message)
        self.dataminer_collection_intermediate = dataminer_collection_intermediate
        self.index = index
        self.slot = slot
        self.message = message

    def __str__(self) -> str:
        output = "The %s Version of DataMinerSettings %i of %r is None" % (self.slot, self.index, self.dataminer_collection_intermediate)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DataMinersFailureError(DataMinerException):
    "Multiple DataMiners failed to activate."

    def __init__(self, version:"Version.Version", dataminer_collections:list["DataMiner.DataMinerCollection"], message:Optional[str]=None) -> None:
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

    def __init__(self, dataminer:Union["DataMiner.DataMiner", "DataMiner.DataMinerSettings", "DataMiner.DataMinerCollection"], file_name:str, version:Optional["Version.Version"], message:Optional[str]=None) -> None:
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

    def __init__(self, file:"FileManager.FilePromise", exit_code:int, message:Optional[str]=None) -> None:
        '''
        :file: The FilePromise of an FSB file that failed to extract.
        :exit_code: The exit code that the extraction executable returned.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file, exit_code, message)
        self.file = file
        self.exit_code = exit_code
        self.message = message

    def __str__(self) -> str:
        output = "Failed to extract file %r; returned exit code %i" % (self.file, self.exit_code)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class SoundFilesMetadataError(DataMinerException):
    "audio_metadata failed to extract the sound file."

    def __init__(self, file:"FileManager.FilePromise", message:Optional[str]=None) -> None:
        '''
        :file: The FilePromise that audio_metadata failed to extract.
        :message: Additional text to place after the main message.'''
        super().__init__(file, message)
        self.file = file
        self.message = message

    def __str__(self) -> str:
        output = "audio_metadata failed to extract %r" % (self.file,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class TagSearcherDependencyError(DataMinerException):
    "A tag exists in a DataMiner that is not a dependency of this one."

    def __init__(self, dataminer:"DataMiner.DataMiner", tag:str, dataminer_collection:"DataMiner.DataMinerCollection", message:Optional[str]=None) -> None:
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
        output = "%r could find tag \"%s\" in %r, but it is not a dependency" % (self.dataminer, self.tag, self.dataminer_collection)
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

class UnrecognizedDataMinerCollectionError(DataMinerException):
    "The DataMinerCollection string is not recognized."

    def __init__(self, dataminer_collection_str:str, source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :dataminer_collection_str: The DataMiner string that does not correspond to any DataMiner.
        :source: The object attempting to reference this DataMiner.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_collection_str, source, message)
        self.source = source
        self.dataminer_collection_str = dataminer_collection_str
        self.message = message

    def __str__(self) -> str:
        output = "DataMinerCollection \"%s\"" % (self.dataminer_collection_str)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        if self.message is None:
            output += " does note exist!"
        else:
            output += " does not exist %s!" % (self.message,)
        return output

class UnrecognizedDataMinerError(DataMinerException):
    "The DataMiner string is not recognized."

    def __init__(self, dataminer_str:str, source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :dataminer_str: The DataMiner string that does not correspond to any DataMiner.
        :source: The object attempting to reference this DataMiner.
        :message: Additional text to place after the main message.
        '''
        super().__init__(dataminer_str, source, message)
        self.source = source
        self.dataminer_str = dataminer_str
        self.message = message

    def __str__(self) -> str:
        output = "DataMiner \"%s\"" % (self.dataminer_str)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        if self.message is None:
            output += " does note exist!"
        else:
            output += " does not exist %s!" % (self.message,)
        return output

class UnrecognizedPackError(DataMinerException):
    "The behavior pack/resource pack is not recognized."

    def __init__(self, pack:str, pack_type:Literal["behavior", "resource", "pack"], source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :pack: The name of the behavior pack/resource pack.
        :pack_type: The type of pack ("behavior" or "resource").
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
            case _:
                pack_string = "Pack"
        output = "%s \"%s\"" % (pack_string, self.pack,)
        if self.source is not None:
            output += ", found by %r," % (self.source,)
        output += " is not recognized"
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

class ManagerFailureError(ManagerException):
    "A Manager has failed for some reason."

    def __init__(self, manager:"Manager.Manager", *args: object) -> None:
        '''
        :manager: The Manager that failed.
        '''
        super().__init__(*args)
        self.manager = manager

    def __str__(self) -> str:
        return "%r failed: %s" % (self.manager, self.args)

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

class NbtException(Exception):
    "Abstract Exception class for errors relating to NBT."

class NbtBytesInvalidArgumentsError(NbtException):
    "Attempted to create an NbtBytes object with neither data nor hash."

    def __init__(self, nbt_bytes:"NbtReader.NbtBytes", message:Optional[str]=None) -> None:
        '''
        :nbt_bytes: The NbtBytes object with invalid arguments.
        :message: Additional text to place after the main message.
        '''
        super().__init__(nbt_bytes, message)
        self.nbt_bytes = nbt_bytes
        self.message = message

    def __str__(self) -> str:
        output = "%r must be specified with data_hash and/or value arguments" % (self.nbt_bytes,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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

    def __init__(self, structure_set:"StructureSet.StructureSet", key:Union["D.DiffType", int], message:Optional[str]=None) -> None:
        super().__init__(structure_set, key, message)
        self.structure_set = structure_set
        self.key = key
        self.message = message

    def __str__(self) -> str:
        output = "Attempted to compare with key %s on %r using a NoneType object" % (self.key, self.structure_set)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class DiffKeyError(StructureException):
    "The Diff object does not have anything at the position indexed."

    def __init__(self, side:"D.DiffType", diff:"D.Diff", message:Optional[str]=None) -> None:
        '''
        :side: The DiffType that was used to index.
        :diff: The Diff that was indexed.
        :message: Additional text to place after the main message.
        '''
        super().__init__(side, diff)
        self.side = side
        self.diff = diff
        self.message = message

    def __str__(self) -> str:
        output = "%r does not have" % (self.diff,)
        if self.side.name == "old":
            output += " an old object"
        elif self.side.name == "new":
            output += " a new object"
        else:
            output += " a not_diff object"
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class NormalizerError(StructureException):
    "A Normalizer's function has failed."

    def __init__(self, normalizer:"Normalizer.Normalizer", data:Any, message:Optional[str]=None) -> None:
        '''
        :normalizer: The Normalizer whose function failed.
        :data: The data the Normalizer failed on.
        :message: Additional text to place after the main message.
        '''
        super().__init__(normalizer, data, message)
        self.normalizer = normalizer
        self.data = data
        self.message = message

    def __str__(self) -> str:
        output = "The function of %r failed" % (self.normalizer,)
        data_string = str(self.data)
        if len(data_string) <= 500:
            output += " on data \"%s\"" % (data_string)
        output += "!" if self.message is None else " %s!" % (self.message,)
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

class NullNormalizerDependenciesAccessorError(StructureException):
    "Attempted to access data from a NullNormalizerDependencies"

    def __init__(self, normalizer_dependencies:"Normalizer.NullNormalizerDependencies", version:"Version.Version", dataminer_name:str, message:Optional[str]=None) -> None:
        '''
        :normalizer_dependencies: The NullNormalizerDependencies that was accessed.
        :version: The Version that was used to attempt to access.
        :dataminer_name: The name of the DataMinerCollection that was used to attempt to access.
        :message: Additional text to place after the main message.
        '''
        super().__init__(normalizer_dependencies, version, dataminer_name, message)
        self.normalizer_dependencies = normalizer_dependencies
        self.version = version
        self.dataminer_name = dataminer_name
        self.message = message

    def __str__(self) -> str:
        output = "%r cannot be accessed with %r or DataMinerCollection \"%s\"" % (self.normalizer_dependencies, self.version, self.dataminer_name)
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

class StructureSetKeyError(StructureException):
    "A StructureSet does not have the DiffType used to access it."

    def __init__(self, key:"D.DiffType", source:"StructureSet.StructureSet", message:Optional[str]=None) -> None:
        '''
        :key: The key used to access the StructureSet.
        :source: The StructureSet that could not be accessed.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, source, message)
        self.key = key
        self.source = source
        self.message = message

    def __str__(self) -> str:
        output = "%r cannot be accessed with key %s" % (self.source, self.key.name)
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

class UnrecognizedStructureError(StructureException):
    "The Structure string is not recognized."

    def __init__(self, structure_str:str, source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :structure_str: The Structure string that does not correspond to any Structure.
        :source: The object attempting to reference this Structure.
        :message: Additional text to place after the main message.
        '''
        super().__init__(structure_str, source, message)
        self.structure_str = structure_str
        self.source = source
        self.message = message

    def __str__(self) -> str:
        output = "Structure \"%s\"" % (self.structure_str,)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        if self.message is None:
            output += " does not exist!"
        else:
            output += " does not exist %s!" % (self.message,)
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

class VolumeStructureUnrecognizedKeysError(StructureException):
    "The VolumeStructure has additional data but not Structure."

    def __init__(self, additional_keys:list[str], message:Optional[str]=None) -> None:
        '''
        :additional_keys: The keys that are unrecognized.
        :message: Additional text to place after the main message.
        '''
        super().__init__(additional_keys, message)
        self.additional_keys = additional_keys
        self.message = message

    def __str__(self) -> str:
        output = "Cannot deal with keys %s due to having no substructure" % (self.additional_keys,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

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

class DuplicateVersionError(VersionException):
    "There are two Versions with the same name."

    def __init__(self, version_name:str, message:Optional[str]=None) -> None:
        '''
        :version_name: The name of the duplicated Versions.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_name, message)
        self.version_name = version_name
        self.message = message

    def __str__(self) -> str:
        output = "A duplicated Version with the name \"%s\" exists!" % (self.version_name,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class InvalidParentVersionError(VersionException):
    "A Version has an invalid parent Version."

    def __init__(self, version:"Version.Version", parent_name:str, message:Optional[str]=None) -> None:
        '''
        :version: The Version with an invalid parent Version.
        :parent_name: The name of the parent Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, parent_name, message)
        self.version = version
        self.parent_name = parent_name
        self.message = message

    def __str__(self) -> str:
        output = "%r has an invalid parent \"%s\"" % (self.version, self.parent_name)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class InvalidVersionNameError(VersionException):
    "A Version has an invalid name."

    def __init__(self, version:"Version.Version", message:Optional[str]=None) -> None:
        '''
        :version: The Version with an invalid name.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, message)
        self.version = version
        self.message = message

    def __str__(self) -> str:
        output = "%r has an invalid name" % (self.version,)
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

    def __init__(self, version_tags:list["VersionTags.VersionTag"], message:Optional[str]=None) -> None:
        '''
        :version_tags: The list of VersionTags containing no ordering tags.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_tags, message)
        self.version_tags = version_tags
        self.message = message

    def __str__(self) -> str:
        output = "No ordering tags found within %s" % (self.version_tags,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class NotAllOrderTagsUsedError(VersionException):
    "Not all ordering VersionTags were used."

    def __init__(self, message:Optional[str]=None) -> None:
        '''
        :message: Additional text to place after the main message.
        '''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        output = "Not all order tags were used"
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class NotAnOrderTagError(VersionException):
    "The VersionTag is not an ordering tag."

    def __init__(self, tag:"VersionTags.VersionTag", message:Optional[str]=None) -> None:
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

class UnrecognizedLatestSlotError(VersionException):
    "The latest slot is not recognized."

    def __init__(self, latest_slot:str, source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :latest_slot: The latest slot that is unrecognized.
        :source: The object attempting to reference this latest slot.
        :message: Additional text to place after the main message.
        '''
        super().__init__(latest_slot, source, message)
        self.latest_slot = latest_slot
        self.source = source
        self.message = message

    def __str__(self) -> str:
        output = "Latest slot \"%s\"" % (self.latest_slot,)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        if self.message is None:
            output += " does not exist!"
        else:
            output += " does not exist %s!" % (self.message,)
        return output

class UnrecognizedVersionError(VersionException):
    "The Version string is not recognized."

    def __init__(self, version_str:str, source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :version_str: The Version string that does not correspond to any Version.
        :source: The object attempting to reference this Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_str, source, message)
        self.version_str = version_str
        self.source = source
        self.message = message

    def __str__(self) -> str:
        output = "Version \"%s\"" % (self.version_str,)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        if self.message is None:
            output += " does not exist!"
        else:
            output += " does not exist %s!" % (self.message,)
        return output

class UnrecognizedVersionTagError(VersionException):
    "The VersionTag is not recognized."

    def __init__(self, version_tag_str:str, source:Optional[object]=None, message:Optional[str]=None) -> None:
        '''
        :version_tag_str: The VersionTag string that does not correspond to any VersionTag.
        :source: The object attempting to reference this Version.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_tag_str, source, message)
        self.version_tag_str = version_tag_str
        self.source = source
        self.message = message

    def __str__(self) -> str:
        output = "VersionTag \"%s\"" % (self.version_tag_str,)
        if self.source is not None:
            output += ", as referenced by %r," % (self.source,)
        if self.message is None:
            output += " does not exist!"
        else:
            output += " does not exist %s!" % (self.message,)
        return output

class UnreleasedDownloadableVersionError(VersionException):
    "A Version has the unreleased tag and has a method for downloading."

    def __init__(self, version:"Version.Version", version_tag:"VersionTags.VersionTag", message:Optional[str]=None) -> None:
        '''
        :version: The Version with an unreleased tag and a method for downloading.
        :version_tag: The unreleased VersionTag.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version, message)
        self.version = version
        self.version_tag = version_tag
        self.message = message

    def __str__(self) -> str:
        output = "%r has the %r tag but has a download method" % (self.version, self.version_tag)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output

class VersionChildError(VersionException):
    "The parent Version's ordering tag and child Version's ordering tag cannot go together."

    def __init__(self, parent_version:"Version.Version", parent_tag:"VersionTags.VersionTag", child_version:"Version.Version", child_tag:"VersionTags.VersionTag", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", child_tags:list["VersionTags.VersionTag"], error_child:"Version.Version", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", count:int, tags:list["VersionTags.VersionTag"], message:Optional[str]=None) -> None:
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

    def __init__(self, parent_version:"Version.Version", parent_tag:"VersionTags.VersionTag", child_version:"Version.Version", child_tag:"VersionTags.VersionTag", time_text:Literal["before", "after"], message:Optional[str]=None) -> None:
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

    def __init__(self, version_range:"VersionRange.VersionRange", start_version:"Version.Version", stop_version:"Version.Version", message:Optional[str]=None) -> None:
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

    def __init__(self, version:"Version.Version", top_level_tag:"VersionTags.VersionTag", message:Optional[str]=None) -> None:
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

class UnrecognizedVersionFileTypeError(VersionFileException):
    "The VersionFileType is unrecognized."

    def __init__(self, file_type_str:str, source:object, message:Optional[str]=None) -> None:
        '''
        :file_type_str: The name of the unrecognized VersionFileType.
        :source: The object that references the VersionFileType.
        :message: Additional text to place after the main message.
        '''
        super().__init__(file_type_str, source, message)
        self.file_type_str = file_type_str
        self.source = source
        self.message = message

    def __str__(self) -> str:
        output = "FileType %s, as referenced by %r, is unrecognized" % (self.file_type_str, self.source)
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
        :version_file: The VersionFile with no Accessors.
        :message: Additional text to place after the main message.
        '''
        super().__init__(version_file, message)
        self.version_file = version_file
        self.message = message

    def __str__(self) -> str:
        output = "%r has no Accessors" % (self.version_file,)
        output += "!" if self.message is None else " %s!" % (self.message,)
        return output