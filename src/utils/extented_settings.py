from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    YamlConfigSettingsSource,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
) 

__all__ = [
    "ExtendedBaseSettings"
]


class ExtendedBaseSettings(BaseSettings):

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources = super().settings_customise_sources(
            settings_cls,
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
        yaml_settings = YamlConfigSettingsSource(
            cls,
            yaml_file=cls.model_config.get("yaml_file", Path("")),
            yaml_file_encoding=cls.model_config.get("yaml_file_encoding", None)
        )
        json_settings = JsonConfigSettingsSource(
            cls,
            json_file=cls.model_config.get("json_file", Path("")),
            json_file_encoding=cls.model_config.get("json_file_encoding", None)
        )
        return (yaml_settings, json_settings) + sources