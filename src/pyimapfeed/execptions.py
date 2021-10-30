class ConfigError(ValueError):
    ...


class ConfigLoadingError(ConfigError):
    ...


class ConfigWritingError(ConfigError):
    ...
