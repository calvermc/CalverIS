from dataclasses import dataclass
from .errors import CalverSyntaxError

@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int

class Lexer:
    TWO_CHAR = {"==", "!=", "<=", ">=", "&&", "||"}
    SINGLE = set("+-*/%(){}=<>!,:;")

    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.line = 1
        self.column = 1

    def _peek(self, offset=0):
        pos = self.i + offset
        return self.source[pos] if pos < len(self.source) else ""

    def _advance(self):
        ch = self._peek()
        if ch:
            self.i += 1
            if ch == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return ch

    def tokenize(self):
        tokens = []
        while self._peek():
            ch = self._peek()
            if ch.isspace():
                self._advance(); continue
            if ch == "/" and self._peek(1) == "/":
                while self._peek() and self._peek() != "\n": self._advance()
                continue
            if ch == "#":
                while self._peek() and self._peek() != "\n": self._advance()
                continue
            line, col = self.line, self.column
            if ch in "\"'":
                tokens.append(self._string()); continue
            if ch.isdigit():
                tokens.append(self._number()); continue
            if ch.isalpha() or ch == "_":
                tokens.append(self._identifier()); continue
            pair = ch + self._peek(1)
            if pair in self.TWO_CHAR:
                self._advance(); self._advance()
                tokens.append(Token("SYMBOL", pair, line, col)); continue
            if ch in self.SINGLE:
                self._advance()
                tokens.append(Token("SYMBOL", ch, line, col)); continue
            raise CalverSyntaxError(f"Karakter tidak dikenal: {ch!r}", line, col)
        tokens.append(Token("EOF", None, self.line, self.column))
        return tokens

    def _string(self):
        quote = self._advance()
        line, col = self.line, self.column - 1
        chars = []
        while self._peek():
            ch = self._advance()
            if ch == quote:
                return Token("STRING", "".join(chars), line, col)
            if ch == "\\":
                esc = self._advance()
                mapping = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "\"": "\"", "'": "'"}
                if not esc:
                    break
                chars.append(mapping.get(esc, esc))
            else:
                if ch == "\n":
                    raise CalverSyntaxError("Teks tidak boleh melewati baris tanpa penutup", line, col)
                chars.append(ch)
        raise CalverSyntaxError("Teks belum ditutup", line, col)

    def _number(self):
        line, col = self.line, self.column
        chars = []
        while self._peek().isdigit(): chars.append(self._advance())
        if self._peek() == "." and self._peek(1).isdigit():
            chars.append(self._advance())
            while self._peek().isdigit(): chars.append(self._advance())
        raw = "".join(chars)
        value = float(raw) if "." in raw else int(raw)
        return Token("NUMBER", value, line, col)

    def _identifier(self):
        line, col = self.line, self.column
        chars = []
        while self._peek() and (self._peek().isalnum() or self._peek() == "_"):
            chars.append(self._advance())
        return Token("IDENT", "".join(chars), line, col)
