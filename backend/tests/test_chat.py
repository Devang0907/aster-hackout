import json
from types import SimpleNamespace

import httpx
import pytest
from pydantic import SecretStr

from app.schemas.chat import ChatRequest
from app.services import chat


@pytest.mark.asyncio
async def test_chat_uses_settings_key_and_current_free_router(monkeypatch) -> None:
    monkeypatch.setattr(
        chat,
        "get_settings",
        lambda: SimpleNamespace(
            openrouter_api_key=SecretStr("test-key"),
            openrouter_model="openrouter/free",
            openrouter_http_referer="http://localhost:8080",
            openrouter_app_title="CarbonLoop",
        ),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.headers["X-OpenRouter-Title"] == "CarbonLoop"
        payload = json.loads(request.content)
        assert payload["model"] == "openrouter/free"
        assert [message["role"] for message in payload["messages"]] == [
            "system",
            "assistant",
            "user",
        ]
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "  Lower transport emissions.  "}}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        response = await chat.send_message(
            ChatRequest(
                message="What should I improve?",
                history=[{"role": "assistant", "content": "Ask me anything."}],
            ),
            client=client,
        )

    assert response.content == "Lower transport emissions."
    assert response.timestamp.tzinfo is not None


@pytest.mark.asyncio
async def test_chat_reports_missing_key(monkeypatch) -> None:
    monkeypatch.setattr(
        chat,
        "get_settings",
        lambda: SimpleNamespace(openrouter_api_key=None),
    )

    with pytest.raises(chat.ChatConfigurationError, match="OPENROUTER_API_KEY"):
        await chat.send_message(ChatRequest(message="Hello"))


@pytest.mark.asyncio
async def test_chat_translates_provider_errors(monkeypatch) -> None:
    monkeypatch.setattr(
        chat,
        "get_settings",
        lambda: SimpleNamespace(
            openrouter_api_key=SecretStr("test-key"),
            openrouter_model="openrouter/free",
            openrouter_http_referer="http://localhost:8080",
            openrouter_app_title="CarbonLoop",
        ),
    )
    transport = httpx.MockTransport(
        lambda _: httpx.Response(429, json={"error": {"message": "provider detail"}})
    )

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(chat.ChatProviderError, match="request limit") as caught:
            await chat.send_message(ChatRequest(message="Hello"), client=client)

    assert caught.value.status_code == 429
