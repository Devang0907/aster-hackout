from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.chat import ChatRequest, ChatResponse, ChatRole

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert carbon emissions advisor for the CarbonLoop platform.
You help users understand:
- Carbon emissions concepts and calculations
- How to reduce their factory's carbon footprint
- How to interpret and act on recommendations
- General platform navigation and features

Be concise, practical, and action-oriented. If asked about specific factory data,
provide general guidance and recommend checking the dashboard for actual numbers.

Keep responses under 200 words when possible."""


class ChatConfigurationError(RuntimeError):
    pass


class ChatProviderError(RuntimeError):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _messages(request: ChatRequest) -> list[dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(
        {"role": message.role.value, "content": message.content}
        for message in request.history[-10:]
    )
    messages.append({"role": "user", "content": request.message})
    return messages


def _provider_error(status_code: int) -> str:
    if status_code == 401:
        return "OpenRouter rejected the configured API key"
    if status_code == 402:
        return "OpenRouter credits are unavailable for the selected model"
    if status_code == 404:
        return "The configured OpenRouter model is unavailable"
    if status_code == 429:
        return "OpenRouter's request limit has been reached; try again later"
    return f"OpenRouter returned HTTP {status_code}"


async def send_message(
    request: ChatRequest,
    *,
    client: httpx.AsyncClient | None = None,
) -> ChatResponse:
    settings = get_settings()
    if settings.openrouter_api_key is None:
        raise ChatConfigurationError("OPENROUTER_API_KEY is not configured")

    owns_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0))

    try:
        try:
            response = await client.post(
                OPENROUTER_CHAT_URL,
                headers={
                    "Authorization": (
                        f"Bearer {settings.openrouter_api_key.get_secret_value()}"
                    ),
                    "Content-Type": "application/json",
                    "HTTP-Referer": settings.openrouter_http_referer,
                    "X-OpenRouter-Title": settings.openrouter_app_title,
                },
                json={
                    "model": settings.openrouter_model,
                    "messages": _messages(request),
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ChatProviderError(
                exc.response.status_code, _provider_error(exc.response.status_code)
            ) from exc
        except httpx.TimeoutException as exc:
            raise ChatProviderError(504, "OpenRouter timed out; try again later") from exc
        except httpx.RequestError as exc:
            raise ChatProviderError(503, "OpenRouter could not be reached") from exc

        try:
            data: dict[str, Any] = response.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ChatProviderError(502, "OpenRouter returned an invalid response") from exc
        if not isinstance(content, str) or not content.strip():
            raise ChatProviderError(502, "OpenRouter returned an empty response")

        return ChatResponse(
            role=ChatRole.assistant,
            content=content.strip(),
            timestamp=datetime.now(UTC),
        )
    finally:
        if owns_client:
            await client.aclose()
