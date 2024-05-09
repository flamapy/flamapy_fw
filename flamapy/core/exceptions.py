class FlamaException(Exception):
    pass


class ParsingException(Exception):
    pass


class PluginNotFound(FlamaException):
    pass


class OperationNotFound(FlamaException):
    pass


class TransformationNotFound(FlamaException):
    pass


class ElementNotFound(FlamaException):
    pass


class DuplicatedFeature(FlamaException):
    pass


class ConfigurationNotFound(FlamaException):
    pass
