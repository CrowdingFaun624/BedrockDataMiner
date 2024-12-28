from typing import Any, Callable

import Version.VersionRange as VersionRange


class Normalizer[IN, OUT]():
    '''Changes data before a Structure looks at it.'''

    def __init__(self, name:str, function:Callable[[IN], OUT], arguments:dict[str,Any]) -> None:
        '''
        :name: The Component name of this Normalizer.
        :function: A Callable that modifies the original object and returns nothing.
        :arguments: kwargs that are given to the function when this Normalizer is called.
        '''
        self.name = name
        self.function = function
        self.arguments = arguments
        self.version_range:VersionRange.VersionRange|None = None

    def __repr__(self) -> str:
        function_name:str|None
        if hasattr(self.function, "__name__"):
            function_name = self.function.__name__
        elif hasattr(self.function, "name"):
            function_name = self.function.name
        else:
            function_name = None
        if function_name is None:
            return "<%s %s>" % (self.__class__.__name__, self.name)
        else:
            return "<%s %s %s>" % (self.__class__.__name__, self.name, function_name)

    def link_subcomponents(self, version_range:VersionRange.VersionRange) -> None:
        '''
        :version_range: Running this Normalizer is only allowed when the Version is within this range.
        '''
        self.version_range = version_range if not version_range.is_all_versions() else None

    def __call__(self, data:IN) -> OUT|None:
        '''
        Calls the Normalizer's function.
        :data: The argument of the Normalizer's function.
        '''
        return self.function(data, **self.arguments)
