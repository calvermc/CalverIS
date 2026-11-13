"""Pemisah blok bahasa native dalam satu file .cvis.

Versi alpha mengekspor blok sebagai file sumber terpisah; belum menjalankan bridge lintas runtime.
"""
from dataclasses import dataclass
import re
from pathlib import Path
from .errors import CalverSyntaxError

LANGUAGE_EXTENSIONS = {
    "html": "html", "css": "css", "javascript": "js", "typescript": "ts",
    "python": "py", "dart": "dart", "java": "java", "kotlin": "kt",
    "swift": "swift", "c": "c", "cpp": "cpp", "csharp": "cs",
    "php": "php", "ruby": "rb", "go": "go", "rust": "rs", "lua": "lua", "sql": "sql",
}
ALIASES = {"js": "javascript", "ts": "typescript", "py": "python", "c++": "cpp", "cs": "csharp"}
OUTPUT_NAMES = {
    "html": "index.html", "css": "styles.css", "javascript": "app.js",
    "typescript": "app.ts", "python": "backend.py", "dart": "main.dart",
    "java": "Main.java", "kotlin": "Main.kt", "swift": "main.swift",
    "c": "main.c", "cpp": "main.cpp", "csharp": "Program.cs", "php": "index.php",
    "ruby": "main.rb", "go": "main.go", "rust": "main.rs", "lua": "main.lua", "sql": "schema.sql",
}
BLOCK_PATTERN = re.compile(r"(?m)^[ \t]*(html|css|javascript|js|typescript|ts|python|py|dart|java|kotlin|swift|csharp|cs|cpp|c\+\+|c|php|ruby|go|rust|lua|sql)\s*\{[ \t]*(?:\r?\n)?")

@dataclass
class NativeBlock:
    language: str
    code: str
    line: int

@dataclass
class SplitSource:
    cvis_source: str
    blocks: list[NativeBlock]


def _find_close(source: str, open_index: int, language: str):
    depth = 0
    i = open_index
    quote = None
    triple = False
    escaped = False
    line_comment = False
    block_comment = False
    html_comment = False
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        nxt2 = source[i + 2] if i + 2 < len(source) else ""
        if html_comment:
            if source.startswith("-->", i): html_comment = False; i += 3; continue
            i += 1; continue
        if line_comment:
            if ch == "\n": line_comment = False
            i += 1; continue
        if block_comment:
            if ch == "*" and nxt == "/": block_comment = False; i += 2; continue
            i += 1; continue
        if quote:
            if escaped:
                escaped = False; i += 1; continue
            if ch == "\\":
                escaped = True; i += 1; continue
            if triple:
                marker = quote * 3
                if source.startswith(marker, i): quote = None; triple = False; i += 3; continue
            elif ch == quote:
                quote = None
            i += 1; continue
        if language == "html" and source.startswith("<!--", i):
            html_comment = True; i += 4; continue
        if language in ("javascript", "typescript", "css", "java", "kotlin", "swift", "c", "cpp", "csharp", "go", "rust", "php", "dart"):
            if ch == "/" and nxt == "/": line_comment = True; i += 2; continue
            if ch == "/" and nxt == "*": block_comment = True; i += 2; continue
        if language == "python" and ch == "#":
            line_comment = True; i += 1; continue
        if ch in "\"'`":
            if language == "python" and ch in "\"'" and source.startswith(ch * 3, i):
                quote = ch; triple = True; i += 3; continue
            quote = ch; i += 1; continue
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: return i
        i += 1
    return -1


def split_source(source: str) -> SplitSource:
    blocks = []
    removed = []
    cursor = 0
    while True:
        match = BLOCK_PATTERN.search(source, cursor)
        if not match: break
        raw_language = match.group(1).lower()
        language = ALIASES.get(raw_language, raw_language)
        open_index = source.rfind("{", match.start(), match.end())
        close_index = _find_close(source, open_index, language)
        if close_index < 0:
            line = source.count("\n", 0, open_index) + 1
            raise CalverSyntaxError(f"Blok bahasa '{raw_language}' belum ditutup dengan '}}'", line, 1)
        code = source[match.end():close_index]
        line = source.count("\n", 0, match.start()) + 1
        blocks.append(NativeBlock(language, code.strip("\r\n"), line))
        removed.append((match.start(), close_index + 1))
        cursor = close_index + 1
    if not removed:
        return SplitSource(source, [])
    pieces = []
    last = 0
    for start, end in removed:
        pieces.append(source[last:start])
        last = end
    pieces.append(source[last:])
    return SplitSource("\n".join(pieces), blocks)


def build_sources(source: str, output_dir: str | Path, target: str = "sumber"):
    split = split_source(source)
    if not split.blocks:
        raise ValueError("Tidak ditemukan blok bahasa native untuk dibangun")
    if target not in ("sumber", "web"):
        raise ValueError("Target harus 'sumber' atau 'web'")
    allowed = set(LANGUAGE_EXTENSIONS) if target == "sumber" else {"html", "css", "javascript", "typescript"}
    rejected = sorted({b.language for b in split.blocks if b.language not in allowed})
    if rejected:
        raise ValueError("Target 'web' tidak menerima blok: " + ", ".join(rejected))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped = {}
    for block in split.blocks:
        grouped.setdefault(block.language, []).append(block.code)
    written = []
    if split.cvis_source.strip():
        core_path = output_dir / "main.cvis"
        core_path.write_text(split.cvis_source.strip() + "\n", encoding="utf-8")
        written.append(core_path)
    for language, chunks in grouped.items():
        name = OUTPUT_NAMES[language]
        path = output_dir / name
        path.write_text("\n\n".join(chunks).rstrip() + "\n", encoding="utf-8")
        written.append(path)
    return written
