from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datapizza.clients.anthropic import AnthropicClient
import anthropic

class RetryAnthropicClient(AnthropicClient):
    """
    A wrapper around AnthropicClient that adds retry logic for specific errors.
    Specifically targets 529 Overloaded errors.
    """

    def _is_overloaded_error(exception):
        """Check if the exception is a 529 Overloaded error."""
        return (
            isinstance(exception, anthropic.APIStatusError) and 
            exception.status_code == 529
        )

    # Retry configuration:
    # - Wait exponentially: 1s, 2s, 4s, 8s, 16s...
    # - Stop after 5 attempts
    # - Retry only on 529 Overloaded errors
    _retry_config = {
        "wait": wait_exponential(multiplier=1, min=1, max=60),
        "stop": stop_after_attempt(5),
        "retry": retry_if_exception_type(anthropic.APIStatusError) # We refine this in the wrapper if needed, but tenacity checks type primarily.
                                                                   # To be more specific on status code, we can use a custom predicate,
                                                                   # but for now retrying on APIStatusError (which includes 5xx) is generally safe for idempotent ops.
                                                                   # However, to be precise as requested:
    }
    
    # Let's define a custom retry predicate for exactness
    def _should_retry(retry_state):
        exception = retry_state.outcome.exception()
        return (
            isinstance(exception, anthropic.APIStatusError) and 
            exception.status_code == 529
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        retry=_should_retry
    )
    def invoke(self, *args, **kwargs) -> str:
        return super().invoke(*args, **kwargs)

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        retry=_should_retry
    )
    def stream_invoke(self, *args, **kwargs) -> Iterator[str]:
        return super().stream_invoke(*args, **kwargs)

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        retry=_should_retry
    )
    async def a_invoke(self, *args, **kwargs) -> str:
        return await super().a_invoke(*args, **kwargs)

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        retry=_should_retry
    )
    def a_stream_invoke(self, *args, **kwargs) -> AsyncIterator[str]:
        # Note: retrying a generator is tricky. If it fails mid-stream, 
        # we might get partial output. Tenacity will retry the *call* to the function.
        # For a_stream_invoke, it returns an async generator.
        # If the *creation* of the generator fails, it retries.
        # If the *iteration* fails, tenacity on the wrapper won't catch it unless we wrap the generator.
        # However, 529 usually happens at connection time (start of request).
        return super().a_stream_invoke(*args, **kwargs)
