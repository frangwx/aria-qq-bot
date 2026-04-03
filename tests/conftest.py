import asyncio
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def setup_config():
    from src.utils.config import load_config
    
    config_path = project_root / "config" / "config.yaml"
    if config_path.exists():
        load_config()
    
    return True
