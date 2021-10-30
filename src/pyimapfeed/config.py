import dataclasses
import getpass
import json
from pathlib import Path
from typing import Callable, Dict

import keyring

from pyimapfeed.execptions import ConfigLoadingError, ConfigWritingError


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass
class IMAPServerConfig:
    server: str
    user: str
    use_keyring: bool


@dataclasses.dataclass
class InternalIMAPServerConfig(IMAPServerConfig):
    password: str


def get_settings_folder() -> Path:
    """
    Returns:
        The path where the settings should be saved
    """
    # TODO maybe select a better place for Windows like %APP_FOLDER%
    # TODO for linux maybe select better "~/.config/
    return Path.home() / ".pyimapfeed"


def get_settings_file_path() -> Path:
    return get_settings_folder() / "imap_servers.json"


def get_server_configs() -> Dict[str, IMAPServerConfig]:
    result: Dict[str, IMAPServerConfig] = {}
    if get_settings_file_path().exists():
        data = json.loads(get_settings_file_path().read_bytes())
        if not isinstance(data, dict):
            raise ConfigLoadingError(
                "Could not load config, as JSON file is not a dict"
            )
        for key, kwargs in data.items():
            if not isinstance(kwargs, dict):
                raise ConfigLoadingError(
                    f"The key '{key}' of the JSON config does not contain a server dict"
                )
            try:
                result[key] = IMAPServerConfig(**kwargs)
            except TypeError as e:
                raise ConfigLoadingError(f"Invalid server dict for '{key}': {e}")
    return result


def save_server_configs(configs: Dict[str, IMAPServerConfig]):
    """
    Write Server config to a JSON file, cleaning them from possible
    passwords

    Args:
        configs: The configs to write

    Returns:
        None
    """
    # Make sure folder exists
    get_settings_folder().mkdir(parents=True, exist_ok=True)
    # Make sure all IMAPServerConfigs do not contain passwords
    cleaned: Dict[str, IMAPServerConfig] = {}
    for name, config in configs.items():
        if isinstance(config, InternalIMAPServerConfig):
            kwargs = dataclasses.asdict(config)
            del kwargs["password"]
            cleaned[name] = IMAPServerConfig(**kwargs)
        elif isinstance(config, IMAPServerConfig):
            cleaned[name] = config
        else:
            raise ConfigWritingError("Can only write Server configs!")
    # Write JSON file
    with get_settings_file_path().open("w", encoding="UTF-8") as f:
        json.dump(cleaned, f, cls=EnhancedJSONEncoder)


def ask_password_cli_func(config) -> Callable[[], str]:
    def ask_password_cli():
        return getpass.getpass(
            f"Please enter password for IMAP server '{config.server}'"
            f" and user '{config.user}: "
        )

    return ask_password_cli


def get_service_name(config: IMAPServerConfig):
    return f"PyIMAPFeed://{config.server}"


def get_full_server_config(
    config: IMAPServerConfig, get_password_from_user_func: Callable[[], str] = None
) -> InternalIMAPServerConfig:
    """
    Try to complete config from the user including password

    Password will be loaded from the keyring if wanted

    Args:
        config: information about the IMAP server
        get_password_from_user_func: function to call if password is not set

    Returns:
        Config with password
    """
    if get_password_from_user_func is None:
        get_password_from_user_func = ask_password_cli_func(config)

    if isinstance(config, InternalIMAPServerConfig):
        if config.password:
            return config
    password = ""
    if config.use_keyring:
        password = keyring.get_password(get_service_name(config), config.user)
    if not password:
        password = get_password_from_user_func()
    return InternalIMAPServerConfig(**dataclasses.asdict(config), password=password)


def save_password_if_wanted(config: InternalIMAPServerConfig):
    """
    Function called once accessing the server was successful

    Args:
        config: The Internal Config with the

    """
    if config.use_keyring:
        keyring.set_password(get_service_name(config), config.user, config.password)
