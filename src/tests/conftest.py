import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from utils.index import get_env_variable

# Add src to path
from utils.prompt_builder import init_globals_for_test, get_prompt_globals  # This will ensure blog + prompt vars are initialized

# Get environment variable
ONE_WORKING_LLM = get_env_variable("ONE_WORKING_LLM").lower() == "true"

# Add command line option for one working LLM requirement
def pytest_addoption(parser):
    parser.addoption(
        "--one-working-llm",
        action="store_true",
        default=False,
        help="Require at least one working LLM test"
    )

@pytest.fixture(scope="session")
def initialized_prompt_state():
    init_globals_for_test()
    return get_prompt_globals()

# Track test results for different categories
test_results = {
    'ai': {'passed': False},
    'socials': {'all_passed': True, 'total': 0, 'passed': 0},
    'feeds': {'all_passed': True, 'total': 0, 'passed': 0}
}

def pytest_runtest_makereport(item, call):
    """Hook to run after each test, check which category it belongs to and if it passed."""
    
    # Only execute if ONE_WORKING_LLM is True
    if not ONE_WORKING_LLM:
        return  # Skip execution if ONE_WORKING_LLM is False

    # Always track results regardless of option
    if call.when == "call":
        # Check test category and update results
        if "ai/" in item.nodeid:
            if call.excinfo is None:  # Test passed
                test_results['ai']['passed'] = True
        elif "socials/" in item.nodeid:
            test_results['socials']['total'] += 1
            if call.excinfo is None:  # Test passed
                test_results['socials']['passed'] += 1
            else:
                test_results['socials']['all_passed'] = False
        elif "feeds/" in item.nodeid:
            test_results['feeds']['total'] += 1
            if call.excinfo is None:  # Test passed
                test_results['feeds']['passed'] += 1
            else:
                test_results['feeds']['all_passed'] = False

def pytest_sessionfinish(session, exitstatus):
    """After all tests, ensure all socials and feeds tests pass, and at least one AI test passes."""
    
    # Only execute if ONE_WORKING_LLM is True
    if not ONE_WORKING_LLM:
        return  # Skip execution if ONE_WORKING_LLM is False

    # Print status for each category
    print("\n--- Test Results by Category ---")
    print(f"AI tests: {'PASSED' if test_results['ai']['passed'] else 'FAILED'} (At least one must pass)")
    print(f"Social tests: {'PASSED' if test_results['socials']['all_passed'] else 'FAILED'} ({test_results['socials']['passed']}/{test_results['socials']['total']} passed, all must pass)")
    print(f"Feed tests: {'PASSED' if test_results['feeds']['all_passed'] else 'FAILED'} ({test_results['feeds']['passed']}/{test_results['feeds']['total']} passed, all must pass)")
    
    # Check if requirements are met
    if not test_results['ai']['passed']:
        print("\nWARNING: No AI tests passed during this test run! At least one AI test must pass.")
        session.exitstatus = 1
    elif not test_results['socials']['all_passed']:
        print(f"\nWARNING: Not all Social tests passed! ({test_results['socials']['passed']}/{test_results['socials']['total']} passed)")
        session.exitstatus = 1
    elif not test_results['feeds']['all_passed']:
        print(f"\nWARNING: Not all Feed tests passed! ({test_results['feeds']['passed']}/{test_results['feeds']['total']} passed)")
        session.exitstatus = 1
    elif exitstatus != 0 and test_results['ai']['passed'] and test_results['socials']['all_passed'] and test_results['feeds']['all_passed']:
        # If requirements are met but other tests failed, make the test suite succeed
        print("\nAll requirements met! At least one AI test passed and all Socials/Feeds tests passed. Overriding failure status.")
        session.exitstatus = 0
