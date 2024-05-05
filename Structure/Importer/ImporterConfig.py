class ImporterConfig():
    '''The Importer gives this to components while checking them.'''

    def __init__(
            self, *,
            allow_imports:bool=True,
            allow_normalizer_dependencies:bool=True
        ) -> None:
        self.allow_imports = allow_imports
        self.allow_normalizer_dependencies = allow_normalizer_dependencies

DEFAULT = ImporterConfig()
