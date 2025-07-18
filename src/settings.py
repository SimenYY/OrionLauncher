from pathlib import Path

from pydantic_settings import SettingsConfigDict

from src.utils.extented_settings import ExtendedBaseSettings
from src import _version

ROOT_DIR: Path = Path(__file__).resolve().parent.parent

class Settings(ExtendedBaseSettings):
    """配置类

    读取顺序：环境变量>配置文件>默认值

    注意：环境变量带有前缀
    """
    api_mirror: str = "Official"
    api_proxy: str = ""
    api_proxy_username: str = ""
    api_proxy_password: str = ""
    
    # constant
    name: str = "OrionLauncher"
    organization: str = "OrionLauncher"
    repository: str = "https://github.com/OrionLauncher/OrionLauncher"
    license: str = "GNU LGPL-2.1 license"
    license_url: str = "https://github.com/OrionLauncher/OrionLauncher/blob/main/LICENSE"
    version: str = _version.__version__
    
    model_config = SettingsConfigDict(
        yaml_file="config.yaml",
        yaml_file_encoding="utf-8",
        env_prefix="orion_"
    )

settings = Settings()