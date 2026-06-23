"""
Shared tokenizer for TF-IDF retrieval over mixed ASCII + CJK text.

Used by both RetrievalService and the baseline retrievers so they index and
query with identical tokenization — otherwise cross-method comparisons would
be apples-to-oranges.
"""

from __future__ import annotations


def tokenize(text: str) -> list[str]:
    """Tokenize for TF-IDF retrieval over mixed ASCII + CJK text.

    Strategy:
      - ASCII runs are split on non-alphanumeric into word tokens (len >= 2).
      - CJK runs are decomposed into character bigrams (plus unigrams), the
        standard dictionary-free approach for Chinese retrieval. Without this,
        an entire Chinese sentence becomes one giant token that never matches
        any document, which is why Chinese queries previously scored 0.
    """
    text = text.lower()
    tokens: list[str] = []
    ascii_buf: list[str] = []
    cjk_buf: list[str] = []

    def _flush_ascii() -> None:
        if ascii_buf:
            word = "".join(ascii_buf)
            if len(word) >= 2:
                tokens.append(word)
            ascii_buf.clear()

    def _flush_cjk() -> None:
        if not cjk_buf:
            return
        chars = cjk_buf[:]
        cjk_buf.clear()
        tokens.extend(chars)  # unigrams
        for i in range(len(chars) - 1):  # overlapping bigrams
            tokens.append(chars[i] + chars[i + 1])

    for ch in text:
        if ch.isascii() and ch.isalnum():
            ascii_buf.append(ch)
        elif "\u4e00" <= ch <= "\u9fff":
            _flush_ascii()
            cjk_buf.append(ch)
        else:
            _flush_ascii()
            _flush_cjk()
    _flush_ascii()
    _flush_cjk()
    return tokens
