const STEM = "%%STEM%%";
const LANG = "%%LANG%%";
const DEBUG = false;

let ALL_WORDS = [];
let words = [];
let idx = 0;
let memoMap = {};
let memoTimer = null;
let currentFace = 'front';  // 'front' | 'back'
let currentLayer = 0;
let synth = window.speechSynthesis;
let speechState = 'idle'; // 'idle' | 'starting' | 'speaking' | 'stopping'
let speechGeneration = 0;
let spokeAfterTransition = false;
let aiGenerating = false;
let exampleOriginalHTML = '';

function g(id) { return document.getElementById(id); }

function setSpeakingUI(active) {
  g('speak-btn').classList.toggle('speaking', active);
  g('speak-label').textContent = active ? '停止' : '読み上げ';
}

function badgeClass(layer) { return 'layer-badge badge-' + layer; }

function renderBack(w) {
  g('back-badge').textContent = 'Layer ' + w.layer;
  g('back-badge').className = badgeClass(w.layer);
  g('back-word').textContent = w.word;
  g('back-reading').textContent = w.reading || '';
  g('back-meaning').textContent = w.meaning;

  const notesEl = g('back-notes');
  if (w.notes) {
    notesEl.textContent = w.notes;
    notesEl.style.display = '';
  } else {
    notesEl.style.display = 'none';
  }

  g('back-example').innerHTML = w.example;
  g('back-translation').innerHTML = w.translation;
}

let pendingTransitionEnd = null;

function renderCard(startFlipped = false) {
  if (!words.length) return;
  const w = words[idx];

  // Cancel any deferred back-render from a previous navigation
  const card = g('card');
  if (pendingTransitionEnd) {
    card.removeEventListener('transitionend', pendingTransitionEnd);
    pendingTransitionEnd = null;
  }

  // Front
  g('front-badge').textContent = 'Layer ' + w.layer;
  g('front-badge').className = badgeClass(w.layer);
  g('front-word').textContent = w.word;
  g('front-reading').textContent = w.reading || '';

  // Counter & buttons
  g('cur').textContent = idx + 1;
  g('tot').textContent = words.length;
  g('prev-btn').disabled = idx === 0;
  g('next-btn').disabled = idx === words.length - 1;

  currentFace = startFlipped ? 'back' : 'front';
  cancelAiGeneration();
  g('ai-hint-suggestions').classList.remove('open');
  g('ai-memo-suggestions').classList.remove('open');
  loadMemoForCurrent();
  stopSpeechInternal();
  spokeAfterTransition = false;

  if (startFlipped) {
    // Navigate directly to back face; no auto-speak
    renderBack(w);
    g('card-back').scrollTop = 0;
    if (!card.classList.contains('flipped')) card.classList.add('flipped');
  } else if (card.classList.contains('flipped')) {
    // Flip back to front first; update back content only after animation ends
    card.classList.remove('flipped');
    pendingTransitionEnd = function onEnd(e) {
      if (e.propertyName !== 'transform') return;
      card.removeEventListener('transitionend', pendingTransitionEnd);
      pendingTransitionEnd = null;
      renderBack(w);
      g('card-back').scrollTop = 0;
    };
    card.addEventListener('transitionend', pendingTransitionEnd);
  } else {
    renderBack(w);
    g('card-back').scrollTop = 0;
  }
}

function updateLayerButtons() {
  document.querySelectorAll('.layer-btn').forEach(btn => {
    const layer = parseInt(btn.dataset.layer);
    const count = layer === 0
      ? ALL_WORDS.length
      : ALL_WORDS.filter(w => w.layer === layer).length;
    btn.textContent = (layer === 0 ? 'All' : 'L' + layer) + ' (' + count + ')';
    if (layer === currentLayer) btn.classList.add('active');
    else btn.classList.remove('active');
  });
}

// ── Memo ──────────────────────────────────────────────────────────────────────
function loadMemoForCurrent() {
  const word = words[idx]?.word;
  const entry = word ? (memoMap[word] || {}) : {};
  // Front textarea (表面)
  const frontText = entry.front || '';
  const hintOpen = !frontText;
  g('memo-front-area').value = frontText;
  g('memo-collapsible').classList.toggle('open', hintOpen);
  g('memo-toggle-btn').classList.toggle('open', hintOpen);
  g('memo-toggle-btn').textContent = hintOpen ? 'ヒントを隠す \u25B2' : 'ヒントを見る \u25BC';
  // Hint textarea (裏面で表メモを編集)
  g('memo-hint-area').value = entry.front || '';
  // Back textarea
  g('memo-back-area').value = entry.back || '';
  // Visibility
  g('memo-front-wrap').style.display = currentFace === 'front' ? '' : 'none';
  g('memo-back-wrap').style.display  = currentFace === 'back'  ? '' : 'none';
}

// face='front' の保存元: 表面なら memo-front-area、裏面なら memo-hint-area
function saveMemoNow(face) {
  if (!words.length) return;
  const f = face !== undefined ? face : currentFace;
  const word = words[idx].word;
  let areaId;
  if (f === 'back') {
    areaId = 'memo-back-area';
  } else {
    areaId = currentFace === 'back' ? 'memo-hint-area' : 'memo-front-area';
  }
  const text = g(areaId).value;
  if (!memoMap[word]) memoMap[word] = {};
  if (memoMap[word][f] === text) return;
  memoMap[word][f] = text;
  fetch('/api/memo', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({stem: STEM, word, face: f, text})
  }).catch(() => {});
}

// ナビゲーション前に両面のメモをまとめて保存（タイマーもキャンセル）
function saveAllPending() {
  if (memoTimer) { clearTimeout(memoTimer); memoTimer = null; }
  saveMemoNow('front');
  saveMemoNow('back');
}

function scheduleMemoSave(face) {
  if (memoTimer) clearTimeout(memoTimer);
  memoTimer = setTimeout(() => saveMemoNow(face), 3000);
}

function cancelAndSave(face) {
  if (memoTimer) { clearTimeout(memoTimer); memoTimer = null; }
  saveMemoNow(face);
}

// ── Server logging ────────────────────────────────────────────────────────────
function slog(msg) {
  fetch('/api/log', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: msg})
  }).catch(() => {});
}

// ── Speech ────────────────────────────────────────────────────────────────────
// lang → working voice name cache (persists across cards within the session)
const voiceCache = new Map();

function speak() {
  if (!synth) return;
  const gen = speechGeneration;

  const allVoices = synth.getVoices();
  let candidates = allVoices.filter(v => v.lang === LANG)
    .concat(allVoices.filter(v => v.lang !== LANG && v.lang.startsWith(LANG.split('-')[0])));

  // Move cached working voice to front
  const cachedName = voiceCache.get(LANG);
  if (cachedName) {
    const ci = candidates.findIndex(v => v.name === cachedName);
    if (ci > 0) candidates = [candidates[ci], ...candidates.slice(0, ci), ...candidates.slice(ci + 1)];
  }

  if (DEBUG) slog('speak() lang=' + LANG + ' candidates=' + candidates.length + (cachedName ? ' cached="' + cachedName + '"' : ''));
  speakWith(candidates, 0, gen);
}

function speakWith(candidates, vi, gen) {
  const utt = new SpeechSynthesisUtterance(words[idx].word);
  utt.lang = LANG;
  utt.rate = 0.85;

  const voice = candidates[vi] || null;
  if (voice) utt.voice = voice;
  if (DEBUG && vi > 0) slog('trying voice[' + vi + ']: "' + (voice ? voice.name : 'default') + '"');

  utt.onstart = () => {
    if (gen !== speechGeneration) return;
    spokeAfterTransition = true;
    if (voice) {
      const prev = voiceCache.get(LANG);
      voiceCache.set(LANG, voice.name);
      if (prev !== voice.name) {
        if (DEBUG) slog('saving voice for ' + LANG + ': "' + voice.name + '"');
        fetch('/api/voice', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({lang: LANG, name: voice.name})
        }).catch(() => {});
      }
    }
    if (speechState === 'starting') speechState = 'speaking';
  };
  utt.onend = () => {
    if (gen !== speechGeneration) return;
    speechState = 'idle';
    setSpeakingUI(false);
  };
  utt.onerror = (e) => {
    if (gen !== speechGeneration) return;
    slog('onerror voice[' + vi + ']: ' + e.error);
    if (e.error === 'synthesis-failed' && vi + 1 < candidates.length && speechState !== 'stopping') {
      speakWith(candidates, vi + 1, gen);
    } else {
      speechState = 'idle';
      setSpeakingUI(false);
    }
  };
  synth.speak(utt);
}

function stopSpeechInternal() {
  speechGeneration++;
  if (synth) synth.cancel();
  speechState = 'idle';
  setSpeakingUI(false);
  if (exampleOriginalHTML) {
    g('back-example').innerHTML = exampleOriginalHTML;
    exampleOriginalHTML = '';
  }
}

function requestStop() {
  if (speechState === 'idle' || speechState === 'stopping') return;
  speechState = 'stopping';
  if (synth) synth.cancel();
}

function startSpeak(faceAware) {
  speechGeneration++;
  speechState = 'starting';
  setSpeakingUI(true);
  if (faceAware && g('card').classList.contains('flipped')) speakExample(); else speak();
}

function handleSpeakToggle() {
  if (speechState === 'idle') startSpeak(true);
  else if (speechState === 'speaking') requestStop();
}

function enterAction() {
  if (speechState === 'starting' || speechState === 'stopping') return;

  if (speechState === 'speaking') {
    // 読み上げ中: 停止して次ステップへ進む
    stopSpeechInternal();
  }

  // idle (または直前に停止した)
  const isFlipped = g('card').classList.contains('flipped');
  if (!spokeAfterTransition) {
    // まだ読み上げていない: 読み上げ（face-aware: 表→語, 裏→例文）
    startSpeak(true);
  } else {
    // 読み上げ済み: 次のステップへ
    if (!isFlipped) {
      flipCard();  // 表→裏へフリップ
    } else {
      // 裏→次のカードへ
      if (idx < words.length - 1) { saveAllPending(); idx++; renderCard(); }
    }
  }
}

function stripHtml(html) {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || '';
}

function speakExample() {
  if (!synth) return;
  const plain = stripHtml(words[idx].example);
  if (!plain) return;
  const gen = speechGeneration;

  // Tokenize text nodes in place, preserving HTML structure (<strong> etc.)
  exampleOriginalHTML = g('back-example').innerHTML;
  const el = g('back-example');
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  let node;
  while ((node = walker.nextNode())) textNodes.push(node);
  let charPos = 0;
  for (const textNode of textNodes) {
    const frag = document.createDocumentFragment();
    textNode.textContent.split(/(\s+)/).forEach(t => {
      if (!t) return;
      if (/^\s+$/.test(t)) {
        frag.appendChild(document.createTextNode(t));
      } else {
        const span = document.createElement('span');
        span.className = 'word-token';
        span.dataset.start = String(charPos);
        span.textContent = t;
        frag.appendChild(span);
      }
      charPos += t.length;
    });
    textNode.parentNode.replaceChild(frag, textNode);
  }

  const utt = new SpeechSynthesisUtterance(plain);
  utt.lang = LANG;
  utt.rate = 0.85;

  const cachedName = voiceCache.get(LANG);
  if (cachedName) {
    const voice = synth.getVoices().find(v => v.name === cachedName);
    if (voice) utt.voice = voice;
  }

  utt.onboundary = (e) => {
    if (e.name !== 'word') return;
    document.querySelectorAll('.word-token').forEach(s => s.classList.remove('word-highlight'));
    const start = e.charIndex;
    let end;
    if (e.charLength != null) {
      end = start + e.charLength;
    } else {
      const m = plain.slice(start).search(/\s/);
      end = m === -1 ? plain.length : start + m;
    }
    document.querySelectorAll('.word-token').forEach(s => {
      const sStart = parseInt(s.dataset.start);
      if (sStart >= start && sStart < end) s.classList.add('word-highlight');
    });
  };
  utt.onstart = () => {
    if (gen !== speechGeneration) return;
    spokeAfterTransition = true;
    if (speechState === 'starting') speechState = 'speaking';
  };
  utt.onend = () => {
    if (gen !== speechGeneration) return;
    speechState = 'idle';
    setSpeakingUI(false);
    g('back-example').innerHTML = exampleOriginalHTML;
    exampleOriginalHTML = '';
  };
  utt.onerror = (e) => {
    if (gen !== speechGeneration) return;
    slog('onerror example: ' + e.error);
    speechState = 'idle';
    setSpeakingUI(false);
    g('back-example').innerHTML = exampleOriginalHTML;
    exampleOriginalHTML = '';
  };
  synth.speak(utt);
}

// ── Voice debug ───────────────────────────────────────────────────────────────
function logVoices() {
  const voices = synth.getVoices();
  const matching = voices.filter(v => v.lang === LANG || v.lang.startsWith(LANG.split('-')[0]));
  const selected = voices.find(v => v.lang === LANG) || voices.find(v => v.lang.startsWith(LANG.split('-')[0]));
  if (DEBUG) slog('voices total=' + voices.length + ' lang=' + LANG + ' matching=' + matching.length);
  if (DEBUG) slog('selected voice: ' + (selected ? '"' + selected.name + '" | ' + selected.lang : 'none'));
}
if (synth.getVoices().length > 0) {
  logVoices();
} else {
  synth.addEventListener('voiceschanged', logVoices, { once: true });
}

// ── Layer filter ──────────────────────────────────────────────────────────────
document.querySelectorAll('.layer-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.stopPropagation();
    saveAllPending();
    currentLayer = parseInt(btn.dataset.layer);
    words = currentLayer === 0 ? [...ALL_WORDS] : ALL_WORDS.filter(w => w.layer === currentLayer);
    idx = 0;
    updateLayerButtons();
    renderCard();
  });
});

// ── Shuffle ───────────────────────────────────────────────────────────────────
g('shuffle-btn').addEventListener('click', e => {
  e.stopPropagation();
  saveAllPending();
  for (let i = words.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [words[i], words[j]] = [words[j], words[i]];
  }
  idx = 0;
  renderCard();
});

// ── Navigation ────────────────────────────────────────────────────────────────
function flipCard() {
  spokeAfterTransition = false;
  cancelAiGeneration();
  g('ai-hint-suggestions').classList.remove('open');
  g('ai-memo-suggestions').classList.remove('open');
  saveAllPending();
  g('card').classList.toggle('flipped');
  currentFace = g('card').classList.contains('flipped') ? 'back' : 'front';
  g('memo-front-wrap').style.display = currentFace === 'front' ? '' : 'none';
  g('memo-back-wrap').style.display  = currentFace === 'back'  ? '' : 'none';
  const word = words[idx]?.word;
  if (currentFace === 'back') {
    // front memo を hint area に反映
    g('memo-hint-area').value = word ? (memoMap[word]?.front || '') : '';
  } else {
    // hint の編集内容を front area に反映
    g('memo-front-area').value = word ? (memoMap[word]?.front || '') : '';
  }
}
g('flip-btn').addEventListener('click', e => { e.stopPropagation(); flipCard(); });
g('speak-btn').addEventListener('click', e => { e.stopPropagation(); handleSpeakToggle(); });
g('prev-btn').addEventListener('click', e => {
  e.stopPropagation();
  if (idx > 0) { saveAllPending(); idx--; renderCard(); }
});
g('next-btn').addEventListener('click', e => {
  e.stopPropagation();
  if (idx < words.length - 1) { saveAllPending(); idx++; renderCard(); }
});

// ── Memo events ───────────────────────────────────────────────────────────────
g('memo-front-area').addEventListener('input', () => scheduleMemoSave('front'));
g('memo-front-area').addEventListener('blur',  () => cancelAndSave('front'));
g('memo-hint-area').addEventListener('input',  () => scheduleMemoSave('front'));
g('memo-hint-area').addEventListener('blur',   () => cancelAndSave('front'));
g('memo-back-area').addEventListener('input',  () => scheduleMemoSave('back'));
g('memo-back-area').addEventListener('blur',   () => cancelAndSave('back'));
g('memo-toggle-btn').addEventListener('click', e => {
  e.stopPropagation();
  const open = g('memo-collapsible').classList.toggle('open');
  g('memo-toggle-btn').classList.toggle('open', open);
  g('memo-toggle-btn').textContent = open ? 'ヒントを隠す \u25B2' : 'ヒントを見る \u25BC';
  if (open) g('memo-front-area').focus();
});

// ── Keyboard ──────────────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'TEXTAREA' && !(e.ctrlKey && e.key === 'Enter')) return;
  if (e.target.tagName === 'BUTTON') e.target.blur();
  switch (e.key) {
    case 'ArrowLeft':
    case 'PageUp':
      if (idx > 0) { saveAllPending(); idx--; renderCard(); }
      break;
    case 'ArrowRight':
    case 'PageDown':
      if (idx < words.length - 1) { saveAllPending(); idx++; renderCard(); }
      break;
    case 'ArrowDown':
      e.preventDefault();
      if (!g('card').classList.contains('flipped')) {
        flipCard();
      } else {
        if (idx < words.length - 1) { saveAllPending(); idx++; renderCard(); }
      }
      break;
    case 'ArrowUp':
      e.preventDefault();
      if (g('card').classList.contains('flipped')) {
        flipCard();
      } else {
        if (idx > 0) { saveAllPending(); idx--; renderCard(true); }
      }
      break;
    case ' ':
      e.preventDefault();
      handleSpeakToggle();
      break;
    case 'Enter':
      e.preventDefault();
      enterAction();
      break;
  }
});

// ── AI generation ─────────────────────────────────────────────────────────────
let aiLogSource = null;

function openAiLog() {
  closeAiLog();
  const el = g('ai-log');
  el.textContent = '';
  el.style.display = 'block';
  aiLogSource = new EventSource('/api/ai/log');
  aiLogSource.onmessage = (e) => {
    if (e.data === '[DONE]') { closeAiLog(); return; }
    try {
      el.textContent += JSON.parse(e.data);
      el.scrollTop = el.scrollHeight;
    } catch {}
  };
  aiLogSource.onerror = () => closeAiLog();
}

function closeAiLog() {
  if (aiLogSource) { aiLogSource.close(); aiLogSource = null; }
  const el = g('ai-log');
  if (el) { el.style.display = 'none'; el.textContent = ''; }
}

function cancelAiGeneration() {
  if (!aiGenerating) return;
  aiGenerating = false;
  g('ai-hint-btn').textContent = '✨ AI生成';
  g('ai-memo-btn').textContent = '✨ AI生成';
  fetch('/api/ai/cancel', {method: 'POST'}).catch(() => {});
  closeAiLog();
}

function showAiSuggestions(suggestionsId, items, targetAreaId) {
  const el = g(suggestionsId);
  el.innerHTML = '';
  const face = targetAreaId === 'memo-back-area' ? 'back' : 'front';
  items.forEach(text => {
    const div = document.createElement('div');
    div.className = 'ai-suggestion-item';
    div.textContent = text;
    div.addEventListener('click', () => {
      g(targetAreaId).value = text;
      cancelAndSave(face);
      el.classList.remove('open');
    });
    el.appendChild(div);
  });
  el.classList.add('open');
}

async function aiGenerateHint() {
  if (aiGenerating) return;
  const btn = g('ai-hint-btn');
  const word = words[idx]?.word;
  if (!word) return;
  aiGenerating = true;
  g('ai-hint-suggestions').classList.remove('open');
  g('ai-memo-suggestions').classList.remove('open');
  btn.textContent = '生成中...';
  openAiLog();
  try {
    const hint = g('memo-front-area').value.trim();
    const resp = await fetch('/api/ai/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({stem: STEM, word, ...(hint ? {hint} : {})})
    });
    if (resp.status === 204) return;
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    showAiSuggestions('ai-hint-suggestions', data.items || [], 'memo-front-area');
  } catch (e) {
    slog('ai hint error: ' + e.message);
  } finally {
    aiGenerating = false;
    closeAiLog();
    btn.textContent = '✨ AI生成';
  }
}

async function aiGenerateMemo() {
  if (aiGenerating) return;
  const btn = g('ai-memo-btn');
  const word = words[idx]?.word;
  if (!word) return;
  const hint = g('memo-hint-area').value.trim();
  if (!hint) {
    g('memo-hint-area').focus();
    return;
  }
  aiGenerating = true;
  g('ai-hint-suggestions').classList.remove('open');
  g('ai-memo-suggestions').classList.remove('open');
  btn.textContent = '生成中...';
  openAiLog();
  try {
    const memo = g('memo-back-area').value.trim();
    const resp = await fetch('/api/ai/memo', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({stem: STEM, word, hint, ...(memo ? {memo} : {})})
    });
    if (resp.status === 204) return;
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    showAiSuggestions('ai-memo-suggestions', data.items || [], 'memo-back-area');
  } catch (e) {
    slog('ai memo error: ' + e.message);
  } finally {
    aiGenerating = false;
    closeAiLog();
    btn.textContent = '✨ AI生成';
  }
}

g('ai-hint-btn').addEventListener('click', e => { e.stopPropagation(); if (aiGenerating) cancelAiGeneration(); else aiGenerateHint(); });
g('ai-memo-btn').addEventListener('click', e => { e.stopPropagation(); if (aiGenerating) cancelAiGeneration(); else aiGenerateMemo(); });

// ── Init: fetch settings + word data in parallel ──────────────────────────────
(async () => {
  const statusEl = g('status-msg');
  try {
    const [settingsResp, wordsResp, memosResp] = await Promise.all([
      fetch('/api/settings'),
      fetch('/api/words?f=' + encodeURIComponent(STEM)),
      fetch('/api/memo?f=' + encodeURIComponent(STEM))
    ]);
    if (settingsResp.ok) {
      const settings = await settingsResp.json();
      for (const [lang, name] of Object.entries(settings.voice || {})) {
        voiceCache.set(lang, name);
      }
      if (DEBUG) slog('loaded settings: ' + JSON.stringify(settings.voice || {}));
    }
    if (memosResp.ok) {
      memoMap = await memosResp.json();
    }
    if (!wordsResp.ok) throw new Error('HTTP ' + wordsResp.status);
    ALL_WORDS = await wordsResp.json();
    words = [...ALL_WORDS];
    statusEl.style.display = 'none';
    updateLayerButtons();
    renderCard();
  } catch (err) {
    statusEl.textContent = 'Error: ' + err.message;
    statusEl.style.color = '#cc4444';
  }
})();
