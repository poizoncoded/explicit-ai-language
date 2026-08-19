#!/usr/bin/env python3
"""Check immutable spans and narrow lexical boundaries in a rewritten response."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
from typing import Iterable


MARKERS_PATH = Path(__file__).resolve().parents[1] / "references" / "forbidden-markers.json"
WORD_RE = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*", re.UNICODE)


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    value: str


PATTERNS: tuple[tuple[re.Pattern[str], int], ...] = (
    (re.compile(r"```[^\n]*\n.*?```", re.DOTALL), 0),
    (re.compile(r"`[^`\n]+`"), 0),
    (re.compile(r"\[[^\]\n]+\]\(([^)\n]+)\)"), 1),
    (re.compile(r"https?://[^\s)>\]}]+"), 0),
    (re.compile(r"«[^»\n]+»"), 0),
    (re.compile(r'"[^"\n]+"'), 0),
    (re.compile(r"\b[A-ZА-ЯЁ][A-ZА-ЯЁ0-9_]{1,}\b"), 0),
    (re.compile(r"(?<![\w])\d+(?:[.,]\d+)*(?:[A-Za-zА-Яа-яЁё%°]+)?"), 0),
)


def extract_spans(text: str) -> list[Span]:
    """Extract non-overlapping protected spans in priority order."""
    occupied = [False] * len(text)
    spans: list[Span] = []
    for pattern, group in PATTERNS:
        for match in pattern.finditer(text):
            start, end = match.span(group)
            if any(occupied[start:end]):
                continue
            spans.append(Span(start, end, match.group(group)))
            occupied[start:end] = [True] * (end - start)
    return sorted(spans, key=lambda item: item.start)


def counter_diff(left: Counter[str], right: Counter[str]) -> list[str]:
    return sorted((left - right).elements())


def prose_without_spans(text: str, spans: Iterable[Span]) -> str:
    chars = list(text)
    for span in spans:
        chars[span.start : span.end] = " " * (span.end - span.start)
    return "".join(chars)


def normalized_words(text: str) -> list[str]:
    return [word.casefold() for word in WORD_RE.findall(text)]


def repeated_phrases(source_prose: str, candidate_prose: str) -> list[str]:
    def ngrams(words: list[str], size: int = 4) -> Counter[tuple[str, ...]]:
        return Counter(tuple(words[index : index + size]) for index in range(len(words) - size + 1))

    source_counts = ngrams(normalized_words(source_prose))
    candidate_counts = ngrams(normalized_words(candidate_prose))
    repeated = [
        " ".join(phrase)
        for phrase, count in candidate_counts.items()
        if count > 1 and count > source_counts[phrase]
    ]
    return sorted(repeated)


def forbidden_matches(candidate: str) -> list[str]:
    data = json.loads(MARKERS_PATH.read_text(encoding="utf-8"))
    masked = list(candidate)
    for pattern, group in PATTERNS[:6]:
        for match in pattern.finditer(candidate):
            start, end = match.span(group)
            masked[start:end] = " " * (end - start)
    folded = "".join(masked).casefold()
    matches: list[str] = []
    for phrase in data["exact_phrases"]:
        marker = phrase.casefold()
        if re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", folded):
            matches.append(phrase)
    return sorted(matches)


def validate(source: str, candidate: str) -> dict[str, object]:
    source_spans = extract_spans(source)
    candidate_spans = extract_spans(candidate)
    source_counter = Counter(span.value for span in source_spans)
    candidate_counter = Counter(span.value for span in candidate_spans)

    source_prose = prose_without_spans(source, source_spans)
    candidate_prose = prose_without_spans(candidate, candidate_spans)
    source_word_count = len(normalized_words(source_prose))
    candidate_word_count = len(normalized_words(candidate_prose))
    allowed_word_count = math.ceil(source_word_count * 1.2)

    result: dict[str, object] = {
        "ok": False,
        "forbidden": forbidden_matches(candidate),
        "missing_protected": counter_diff(source_counter, candidate_counter),
        "unexpected_protected": counter_diff(candidate_counter, source_counter),
        "excessive_growth": candidate_word_count > allowed_word_count,
        "repeated_phrases": repeated_phrases(source_prose, candidate_prose),
    }
    result["ok"] = not any(
        (
            result["forbidden"],
            result["missing_protected"],
            result["unexpected_protected"],
            result["excessive_growth"],
            result["repeated_phrases"],
        )
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate(
        args.source.read_text(encoding="utf-8"),
        args.candidate.read_text(encoding="utf-8"),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
