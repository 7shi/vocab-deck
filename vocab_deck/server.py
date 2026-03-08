import sys
import asyncio
import json
import argparse
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path

from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from .helpers import validate_stem, load_words, detect_lang
from .settings import load_settings, save_settings
from .render import render_index, render_card
from .memo import init_db, load_memos, save_memo
from .ai import generate_hint, generate_memo, llm_client
from .config import default_config, set_config


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def index():
    return render_index()


@app.get("/card", response_class=HTMLResponse)
def card(f: str = Query(..., description="File stem (without .toml)")):
    if not validate_stem(f):
        raise HTTPException(status_code=400, detail="Invalid file stem")
    return render_card(f)


@app.get("/api/words")
def api_words(f: str = Query(..., description="File stem (without .toml)")):
    if not validate_stem(f):
        raise HTTPException(status_code=400, detail="Invalid file stem")
    try:
        return load_words(f)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/log")
async def api_log(request: Request):
    body = await request.json()
    print(f"[browser] {body.get('message', '')}", flush=True)
    return {"ok": True}


@app.get("/api/settings")
def api_settings():
    return load_settings()


@app.post("/api/voice")
async def api_voice(request: Request):
    body = await request.json()
    lang = body.get("lang", "")
    name = body.get("name", "")
    if not lang or not name:
        raise HTTPException(status_code=400, detail="lang and name required")
    settings = load_settings()
    settings.setdefault("voice", {})[lang] = name
    save_settings(settings)
    print(f"[settings] {lang} = {name!r}", flush=True)
    return {"ok": True}


@app.get("/api/memo")
def api_memo_get(f: str = Query(..., description="File stem (without .toml)")):
    if not validate_stem(f):
        raise HTTPException(status_code=400, detail="Invalid file stem")
    return load_memos(detect_lang(f))


@app.post("/api/memo")
async def api_memo_post(request: Request):
    body = await request.json()
    stem = body.get("stem", "")
    word = body.get("word", "")
    face = body.get("face", "front")
    text = body.get("text", "")
    if not validate_stem(stem) or not word:
        raise HTTPException(status_code=400, detail="stem and word required")
    if face not in ("front", "back"):
        raise HTTPException(status_code=400, detail="face must be 'front' or 'back'")
    save_memo(detect_lang(stem), word, face, text)
    return {"ok": True}


class AiHintRequest(BaseModel):
    stem: str
    word: str
    hint: str = ""


class AiMemoRequest(BaseModel):
    stem: str
    word: str
    hint: str
    memo: str = ""


@app.post("/api/ai/hint")
async def api_ai_hint(req: AiHintRequest):
    if not validate_stem(req.stem) or not req.word:
        raise HTTPException(status_code=400, detail="stem and word required")
    try:
        words = load_words(req.stem)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    word_data = next((w for w in words if w["word"] == req.word), None)
    if not word_data:
        raise HTTPException(status_code=404, detail="word not found")
    lang_code = detect_lang(req.stem)
    items = await generate_hint(req.word, lang_code, word_data["reading"], req.hint)
    if items is None:
        return Response(status_code=204)
    return {"items": items}


@app.post("/api/ai/memo")
async def api_ai_memo(req: AiMemoRequest):
    if not validate_stem(req.stem) or not req.word or not req.hint:
        raise HTTPException(status_code=400, detail="stem, word, and hint required")
    try:
        words = load_words(req.stem)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    word_data = next((w for w in words if w["word"] == req.word), None)
    if not word_data:
        raise HTTPException(status_code=404, detail="word not found")
    items = await generate_memo(req.word, word_data["meaning"], req.hint, req.memo)
    if items is None:
        return Response(status_code=204)
    return {"items": items}


@app.post("/api/ai/cancel")
def api_ai_cancel():
    llm_client.cancel()
    print("[ai] cancelled", flush=True)
    return {"ok": True}


@app.get("/api/ai/log")
async def api_ai_log():
    async def event_stream():
        while True:
            try:
                msg = await asyncio.wait_for(llm_client._log_queue.get(), timeout=60.0)
            except asyncio.TimeoutError:
                break
            if msg is None:
                yield "data: [DONE]\n\n"
                break
            yield f"data: {json.dumps(msg)}\n\n"
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def main():
    from . import ai
    from . import __name__ as _name, __version__
    parser = argparse.ArgumentParser(description="VocabDeck Web Server")
    parser.add_argument("--version", action="version", version=f"{_name} {__version__}")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("-m", "--model", default=ai.MODEL, help=f"LLM model (default: {ai.MODEL})")
    defaults = default_config()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=defaults.data_dir,
        help=f"Directory containing vocab TOML files (default: {defaults.data_dir})",
    )
    parser.add_argument(
        "--memo-db",
        type=Path,
        default=defaults.memo_db_path,
        help=f"Memo DB path (default: {defaults.memo_db_path})",
    )
    args = parser.parse_args()
    set_config(data_dir=args.data_dir, memo_db_path=args.memo_db)
    ai.MODEL = args.model
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
