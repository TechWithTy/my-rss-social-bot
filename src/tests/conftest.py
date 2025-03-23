# conftest.py or inside your test file
import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.prompt_builder import init_globals_for_test, get_prompt_globals # ✅ This will ensure blog + prompt vars are initialized

@pytest.fixture(scope="session")
def initialized_prompt_state():
    init_globals_for_test()
    return get_prompt_globals()