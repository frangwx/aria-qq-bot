import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

_config: Optional[Dict[str, Any]] = None

def get_config_path() -> Path:
    env_path = os.getenv("CONFIG_FILE", "config/config.yaml")
    return Path(env_path)

def load_config() -> Dict[str, Any]:
    global _config
    if _config is not None:
        return _config
    
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        _config = yaml.safe_load(f)
    
    return _config

def get_config(key: str, default: Any = None) -> Any:
    config = load_config()
    keys = key.split(".")
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value

def reload_config() -> Dict[str, Any]:
    global _config
    _config = None
    return load_config()
