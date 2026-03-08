import asyncio
from pydantic import BaseModel
from ollama import AsyncClient

MODEL = "gpt-oss:120b"


class Suggestions(BaseModel):
    items: list[str]


class LLMClient:
    def __init__(self):
        self._cancelled = False
        self._log_queue: asyncio.Queue = asyncio.Queue()

    def cancel(self):
        self._cancelled = True

    async def _emit(self, msg: str):
        await self._log_queue.put(msg)

    async def chat(self, contents: list[str]) -> list[str] | None:
        self._cancelled = False
        while not self._log_queue.empty():
            self._log_queue.get_nowait()
        model = MODEL
        text = ""
        thinking_started = False
        client = AsyncClient()
        try:
            async for part in await client.chat(
                model=model,
                messages=[{'role': 'user', 'content': '\n\n'.join(contents)}],
                format=Suggestions.model_json_schema(),
                stream=True,
                keep_alive=-1,
            ):
                if self._cancelled:
                    await self._emit("[ai] cancelled\n")
                    return None
                if getattr(part.message, 'thinking', None):
                    if not thinking_started:
                        await self._emit("[ai] thinking...\n")
                        thinking_started = True
                    await self._emit(part.message.thinking)
                chunk = part.message.content
                if chunk:
                    if thinking_started:
                        await self._emit("\n")
                        thinking_started = False
                    await self._emit(chunk)
                    text += chunk
        finally:
            await client._client.aclose()
            await self._emit("\n")
            await self._log_queue.put(None)
        if self._cancelled:
            return None
        return Suggestions.model_validate_json(text).items


llm_client = LLMClient()


async def generate_hint(word: str, lang_code: str, reading: str = "", existing_hint: str = "") -> list[str] | None:
    context = f"単語: {word}（言語コード: {lang_code}）" + (f"　読み: {reading}" if reading else "")
    if existing_hint:
        context += f"\n既存のヒント: {existing_hint}"
        prompt = (
            "上記の既存のヒントをベースに、この単語の音からこじつけられる改良案や別のアプローチを5つ提案してください。"
            "意味には言及せず、音の類似だけに基づいた短い連想（1〜2文）を日本語で書いてください。"
            "itemsリストに5つの提案を格納してください。"
        )
    else:
        prompt = (
            "この単語の音（響き）から日本語でこじつけられる言葉や表現を5つ提案してください。"
            "意味には言及せず、音の類似だけに基づいた短い連想（1〜2文）を日本語で書いてください。"
            "itemsリストに5つの提案を格納してください。"
        )
    return await llm_client.chat([context, prompt])


async def generate_memo(word: str, meaning: str, hint: str, existing_memo: str = "") -> list[str] | None:
    context = f"単語: {word}\n意味（日本語）: {meaning}\nヒント: {hint}"
    if existing_memo:
        context += f"\n既存のメモ: {existing_memo}"
        prompt = (
            "上記の既存のメモをベースに、ヒントから意味を思い出しやすい改良案や別のアプローチを5つ提案してください。"
            "短い説明（1〜2文）をitemsリストに格納してください。"
            "日本語で答えてください。"
        )
    else:
        prompt = (
            "上記のヒントを手がかりにして、この単語の意味にこじつける覚え方を5つ提案してください。"
            "ヒントから意味を思い出すための短い説明（1〜2文）をitemsリストに格納してください。"
            "日本語で答えてください。"
        )
    return await llm_client.chat([context, prompt])
