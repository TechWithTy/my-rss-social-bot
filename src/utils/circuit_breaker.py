import asyncio
import time
from functools import wraps
from typing import Callable, Dict, Any

# In-memory registry for circuit state per provider
_circuit_state = {}

def circuit_breaker(
    provider: str,
    max_failures: int = 3,
    reset_timeout: int = 60
) -> Callable:
    """
    Async circuit breaker decorator.
    :param provider: Unique name for the provider.
    :param max_failures: Number of consecutive failures before opening the circuit.
    :param reset_timeout: Time in seconds to keep the circuit open before retrying.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            state = _circuit_state.setdefault(provider, {
                "failures": 0,
                "opened_at": None,
                "open": False,
            })
            now = time.time()
            # If circuit is open, check if timeout expired
            if state["open"]:
                if now - state["opened_at"] < reset_timeout:
                    return {
                        "status": "error",
                        "response": f"Circuit breaker OPEN for {provider}. Try again later."
                    }
                else:
                    # Reset circuit
                    state["failures"] = 0
                    state["open"] = False
                    state["opened_at"] = None
            try:
                result = await func(*args, **kwargs)
                # If call succeeds, reset failure count
                state["failures"] = 0
                return result
            except Exception as e:
                state["failures"] += 1
                if state["failures"] >= max_failures:
                    state["open"] = True
                    state["opened_at"] = now
                return {
                    "status": "error",
                    "response": f"Circuit breaker: {provider} failed ({state['failures']}x): {str(e)}"
                }
        return wrapper
    return decorator
