import tempfile
from pathlib import Path

from .config import default_config, set_config
from .helpers import bold_to_html, list_tomls, load_words


# --- expand_word=False (non-Indic, default) ---

def test_non_indic_full_word():
    assert bold_to_html("**abc** def") == "<strong>abc</strong> def"

def test_non_indic_partial_word_no_expansion():
    """Non-Indic: bold does NOT expand to word boundary."""
    assert bold_to_html("**ab**c def") == "<strong>ab</strong>c def"


# --- expand_word=True (Indic scripts) ---

def test_indic_already_full_word():
    """Bold already covers a full word → no change in output."""
    assert bold_to_html("**abc** def", True) == "<strong>abc</strong> def"

def test_indic_expand_suffix():
    """**ab**c → abc bolded (extend right to word end)."""
    assert bold_to_html("**ab**c def", True) == "<strong>abc</strong> def"

def test_indic_expand_prefix():
    """x**abc** → xabc bolded (extend left to word start)."""
    assert bold_to_html("x**abc** def", True) == "<strong>xabc</strong> def"

def test_indic_expand_both_ends():
    """x**ab**c → xabc bolded (extend both directions)."""
    assert bold_to_html("x**ab**c def", True) == "<strong>xabc</strong> def"

def test_indic_spans_word_boundary():
    """**abc de**f → 'abc def' bolded.

    Bold opens on word 1 (full) and closes mid-word 2; word 2 must be
    extended to its end so glyph rendering is not split.
    """
    assert bold_to_html("**abc de**f", True) == "<strong>abc def</strong>"

def test_indic_spans_word_boundary_with_context():
    """Same as above with surrounding text."""
    assert bold_to_html("some **abc de**f ghi", True) == "some <strong>abc def</strong> ghi"

def test_indic_spans_word_boundary_prefix_and_suffix():
    """x**bc de**f → 'xbc def' bolded (prefix on first word, suffix on last)."""
    assert bold_to_html("x**bc de**f", True) == "<strong>xbc def</strong>"

def test_indic_no_bold():
    """Text with no markers passes through unchanged."""
    assert bold_to_html("abc def", True) == "abc def"

def test_indic_multiple_separate_bold():
    """Two separate bold regions each expand to their own word."""
    assert bold_to_html("**ab**c **de**f", True) == "<strong>abc</strong> <strong>def</strong>"


def test_default_config_uses_vocab_deck_paths():
    config = default_config()
    assert config.settings_path == Path.home().joinpath(".config", "vocab-deck", "settings.toml")
    assert config.memo_db_path == Path.home().joinpath(".config", "vocab-deck", "memo.db")


def test_set_config_resolves_data_dir():
    with tempfile.TemporaryDirectory() as tmp:
        config = set_config(data_dir=Path(tmp))
        assert config.data_dir == Path(tmp).resolve()


def test_list_tomls_reads_current_config_directory():
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp)
        set_config(data_dir=data_dir)
        data_dir.joinpath("20260308-sample.en-orig.toml").write_text(
            '[[word]]\nword = "alpha"\nmeaning = "A"\n',
            encoding="utf-8",
        )
        data_dir.joinpath("empty.toml").write_text('title = "skip"\n', encoding="utf-8")

        items = list_tomls()

        assert [item["stem"] for item in items] == ["20260308-sample.en-orig"]


def test_load_words_reads_from_configured_directory():
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp)
        set_config(data_dir=data_dir)
        data_dir.joinpath("20260308-sample.hi-orig.toml").write_text(
            (
                '[[word]]\n'
                'word = "namaste"\n'
                'reading = "नमस्ते"\n'
                'meaning = "hello"\n'
                'example = "**na**maste"\n'
                'translation = "**hello**"\n'
            ),
            encoding="utf-8",
        )

        words = load_words("20260308-sample.hi-orig")

        assert words[0]["word"] == "namaste"
        assert words[0]["example"] == "<strong>namaste</strong>"
        assert words[0]["translation"] == "<strong>hello</strong>"
