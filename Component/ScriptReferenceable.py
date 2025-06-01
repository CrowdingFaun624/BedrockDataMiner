from typing import Any, overload

import Domain.Domain as Domain
import Utilities.Exceptions as Exceptions


class ScriptReferenceable():
    '''
    Use get to access Components using their full path and type.
    '''

    __slots__ = (
        "domain",
        "objects",
    )

    def __init__(self, domain:"Domain.Domain") -> None:
        self.domain = domain
        self.objects:dict[str,dict[str,dict[str,Any]]]

    def update_objects(self, objects:dict[str,dict[str,dict[str,Any]]]) -> None:
        self.objects = objects

    def get_options(self, required_type:type|None) -> list[str]:
        '''
        Expensive function that returns all possible strings that can be used in __getitem__.
        Used for error messages.
        '''
        options:list[str] = []
        options.extend(
            f"{domain_name}!{group_name}/{object_name}"
            for domain_name, domain_content in self.objects.items()
            for group_name, group_content in domain_content.items()
            for object_name, object in group_content.items()
            if object is not ... and (required_type is None or isinstance(object, required_type))
        )
        options.extend(
            f"{group_name}/{object_name}"
            for group_name, group_content in self.objects[self.domain.name].items()
            for object_name, object in group_content.items()
            if object is not ... and (required_type is None or isinstance(object, required_type))
        )
        return options

    @overload
    def get(self, path:str, /) -> Any: ...
    @overload
    def get[A](self, path:str, required_type:type[A]|None=None, /) -> A: ...
    def get[A](self, path:str, required_type:type[A]|None=None, /) -> A:
        '''
        :path: The full path of the Component used to create the object, including the Component group name.
        :required_type: The type of the object returned.

        Raises a ComponentException if the path is invalid or the returned object is not an instance of `required_type`.

        Example usage:
        ```python
        script_referenceable.get("common!serializers/json_serializer", Serializer.Serializer]) # reference to any domain.
        script_referenceable.get("serializers/json_serializer", Serializer.Serializer]) # reference to current domain.
        ```
        '''
        # taken from Field.choose_component
        bang_index = path.find("!")
        slash_index = path.rfind("/", bang_index if bang_index != -1 else 0)
        if slash_index == -1:
            options = self.get_options(required_type)
            raise Exceptions.MalformedComponentReferenceError(path, options, "because it has no /")
        # only /
        elif bang_index == -1:
            domain_objects = self.objects[self.domain.name]
            group_name = path[:slash_index]
            object_name = path[slash_index+1:]
            if (group := domain_objects.get(group_name)) is None:
                options = self.get_options(required_type)
                raise Exceptions.UnrecognizedComponentGroupError(group_name, path, options)
        # ! and /
        else:
            domain_name = path[:bang_index]
            object_path = path[bang_index+1:]
            if (domain_objects := self.objects.get(domain_name)) is None:
                options = self.get_options(required_type)
                raise Exceptions.UnrecognizedComponentDomainError(domain_name, path, options)
            group_name = object_path[:slash_index-bang_index-1]
            object_name = object_path[slash_index-bang_index:]
            if (group := domain_objects.get(group_name)) is None:
                options = self.get_options(required_type)
                raise Exceptions.UnrecognizedComponentGroupError(group_name, path, options)

        if (object := group.get(object_name)) is None:
            options = self.get_options(required_type)
            raise Exceptions.UnrecognizedComponentError(object_name, path, options)
        if object is ...:
            options = self.get_options(required_type)
            raise Exceptions.ComponentScriptUnreferenceableError(path, options)
        if required_type is not None and not isinstance(object, required_type):
            options = self.get_options(required_type)
            raise Exceptions.InvalidComponentFinalTypeError(path, object, required_type, type(object), options)
        return object

    def get_future[A](self, path:str, required_type:type[A], /) -> "FutureObject[A]":
        '''
        Can get an object created by a Component during the Script initialization stage. The resulting object can only be gotten
        after Components are fully loaded.

        :path: The full path of the Component used to create the object, including the Component group name.
        :required_type: The type of the object returned.

        Raises a ComponentException if the path is invalid or the returned object is not an instance of `required_type`.

        Example usage:
        ```python
        script_referenceable.get_future("common!serializers/json_serializer", Serializer.Serializer]) # reference to any domain.
        script_referenceable.get_future("serializers/json_serializer", Serializer.Serializer]) # reference to current domain.
        ```
        '''
        return FutureObject(self, path, required_type)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name}>"

class FutureObject[A]():

    __slots__ = (
        "initialized",
        "object",
        "path",
        "required_type",
        "script_referenceable",
    )

    def __init__(self, script_referenceable:"ScriptReferenceable", path:str, required_type:type[A]) -> None:
        self.initialized = False
        self.object:A
        self.script_referenceable = script_referenceable
        self.path = path
        self.required_type = required_type

    def get(self) -> A:
        '''
        Returns the object encoded by the parameters to the `ScriptReferenceable.get_future` that created this.
        Can only be called after Components are finished initializing.
        '''
        if not self.initialized:
            self.object = self.script_referenceable.get(self.path, self.required_type)
        return self.object

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}"
