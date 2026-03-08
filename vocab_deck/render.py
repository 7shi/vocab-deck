from pathlib import Path
from .helpers import detect_lang, make_title, list_tomls

STATIC = Path(__file__).parent / "static"


def _read(name: str) -> str:
    return (STATIC / name).read_text(encoding="utf-8")


def render_index() -> str:
    css = _read("base.css") + _read("index.css")
    items = list_tomls()
    rows = []
    for item in items:
        date_span = ('<span class="card-link-date">' + item["date"] + '</span>') if item["date"] else ""
        rows.append(
            '<a class="card-link" href="/card?f=' + item["stem"] + '">'
            '<span class="card-link-left">'
            '<span class="card-link-lang">' + item["lang"] + '</span>'
            + date_span +
            '<span class="card-link-title">' + item["topic"] + '</span>'
            '</span>'
            '<span class="card-link-meta">' + str(item["count"]) + ' cards</span>'
            '</a>'
        )
    content = "\n".join(rows) if rows else '<p class="empty">No vocab TOML files found.</p>'
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ja">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>VocabDeck</title>\n"
        "<style>" + css + "</style>\n"
        "</head>\n"
        "<body>\n"
        '<div class="library">\n'
        '<h1 class="library-title">VocabDeck</h1>\n'
        + content + "\n"
        "</div>\n"
        "</body>\n"
        "</html>"
    )


def render_card(stem: str) -> str:
    css = _read("base.css") + _read("card.css")
    js = _read("card.js").replace("%%STEM%%", stem).replace("%%LANG%%", detect_lang(stem))
    title = make_title(stem)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ja">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>" + title + "</title>\n"
        "<style>" + css + "</style>\n"
        "</head>\n"
        "<body>\n"
        '<a class="back-to" href="/">← VocabDeck</a>\n'
        "<h1>" + title + "</h1>\n"
        '<div class="controls">\n'
        '  <button class="btn layer-btn" data-layer="0">All</button>\n'
        '  <button class="btn layer-btn" data-layer="1">L1</button>\n'
        '  <button class="btn layer-btn" data-layer="2">L2</button>\n'
        '  <button class="btn layer-btn" data-layer="3">L3</button>\n'
        '  <button class="btn shuffle-btn" id="shuffle-btn">&#x1F500; Shuffle</button>\n'
        "</div>\n"
        '<div class="progress">\n'
        '  <span class="cur" id="cur">-</span> / <span id="tot">-</span>\n'
        "</div>\n"
        '<div class="card-scene" id="scene">\n'
        '  <div class="card" id="card">\n'
        '    <div class="card-face card-front">\n'
        '      <span class="layer-badge" id="front-badge"></span>\n'
        '      <div class="front-word" id="front-word"></div>\n'
        '      <div class="front-reading" id="front-reading"></div>\n'
        "    </div>\n"
        '    <div class="card-face card-back" id="card-back">\n'
        '      <div class="back-header">\n'
        '        <span class="layer-badge" id="back-badge"></span>\n'
        '        <span class="back-word-small" id="back-word"></span>\n'
        '        <span class="back-reading" id="back-reading"></span>\n'
        "      </div>\n"
        '      <div class="back-meaning" id="back-meaning"></div>\n'
        '      <div class="back-notes" id="back-notes"></div>\n'
        '      <div class="back-example" id="back-example"></div>\n'
        '      <div class="back-translation" id="back-translation"></div>\n'
        "    </div>\n"
        "  </div>\n"
        "</div>\n"
        '<div class="nav">\n'
        '  <button class="btn nav-btn" id="prev-btn">&#x2190; 前へ<br><small class="kbd-hint">[&#x2190;], [PgUp]</small></button>\n'
        '  <button class="speak-btn" id="speak-btn">&#x1F50A; <span id="speak-label">読み上げ</span><br><small class="kbd-hint">[Space]</small></button>\n'
        '  <button class="btn nav-btn" id="flip-btn">フリップ<br><small class="kbd-hint">[&#x2191;] / [&#x2193;]</small></button>\n'
        '  <button class="btn nav-btn" id="next-btn">次へ &#x2192;<br><small class="kbd-hint">[&#x2192;], [PgDn]</small></button>\n'
        "</div>\n"
        '<div class="memo-wrap" id="memo-front-wrap">\n'
        '  <button class="memo-toggle-btn" id="memo-toggle-btn">ヒントを見る &#x25BC;</button>\n'
        '  <div class="memo-collapsible" id="memo-collapsible">\n'
        '    <textarea class="memo-area" id="memo-front-area" placeholder="ヒントを入力..."></textarea>\n'
        '    <div class="ai-btn-wrap"><button class="ai-gen-btn" id="ai-hint-btn">✨ AI生成</button></div>\n'
        '    <div class="ai-suggestions" id="ai-hint-suggestions"></div>\n'
        '  </div>\n'
        "</div>\n"
        '<div class="memo-wrap" id="memo-back-wrap" style="display:none">\n'
        '  <div class="memo-hint-section" id="memo-hint-section">\n'
        '    <label for="memo-hint-area">ヒント</label>\n'
        '    <textarea class="memo-area" id="memo-hint-area" placeholder="ヒントを入力..."></textarea>\n'
        '  </div>\n'
        '  <label for="memo-back-area">メモ</label>\n'
        '  <textarea class="memo-area" id="memo-back-area" placeholder="このカードへの注釈..."></textarea>\n'
        '  <div class="ai-btn-wrap"><button class="ai-gen-btn" id="ai-memo-btn">✨ AI生成</button></div>\n'
        '  <div class="ai-suggestions" id="ai-memo-suggestions"></div>\n'
        "</div>\n"
        '<div class="ai-log" id="ai-log" style="display:none"></div>\n'
        '<p class="status-msg" id="status-msg">Loading...</p>\n'
        "<script>" + js + "</script>\n"
        "</body>\n"
        "</html>"
    )
