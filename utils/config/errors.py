class InvalidPromptError(Exception):
    pass

class ModelTimeoutError(Exception):
    pass

class ModelExecutionError(Exception):
    pass

class InvalidModelError(Exception):
    pass

class ConfigError(Exception):
    pass

class ConnectionError(Exception):
    pass