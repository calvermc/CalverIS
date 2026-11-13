from dataclasses import dataclass
from .lexer import Lexer, Token
from .errors import CalverSyntaxError

@dataclass
class Program: statements: list
@dataclass
class VarDecl: name: str; mutable: bool; value: object; type_name: str | None = None
@dataclass
class FunctionDecl: name: str; params: list; body: list
@dataclass
class IfStmt: condition: object; then_body: list; else_body: list
@dataclass
class WhileStmt: condition: object; body: list
@dataclass
class ReturnStmt: value: object
@dataclass
class AssignStmt: name: str; value: object
@dataclass
class ExprStmt: expression: object
@dataclass
class Literal: value: object
@dataclass
class Variable: name: str
@dataclass
class Unary: operator: str; right: object
@dataclass
class Binary: left: object; operator: str; right: object
@dataclass
class Call: callee: object; arguments: list

PRECEDENCE = {
    "atau": 1, "or": 1, "||": 1,
    "dan": 2, "and": 2, "&&": 2,
    "==": 3, "!=": 3,
    "<": 4, "<=": 4, ">": 4, ">=": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6, "%": 6,
}

class Parser:
    def __init__(self, source: str):
        self.tokens = Lexer(source).tokenize()
        self.i = 0

    def _current(self): return self.tokens[self.i]
    def _check(self, value):
        token = self._current()
        return token.kind != "STRING" and token.value == value
    def _advance(self):
        token = self._current()
        if token.kind != "EOF": self.i += 1
        return token
    def _match(self, *values):
        token = self._current()
        if token.kind != "STRING" and token.value in values:
            return self._advance()
        return None
    def _expect(self, value, message=None):
        token = self._current()
        if token.kind == "STRING" or token.value != value:
            raise CalverSyntaxError(message or f"Diharapkan {value!r}, ditemukan {token.value!r}", token.line, token.column)
        return self._advance()
    def _expect_ident(self, message="Diharapkan nama/identifier"):
        token = self._current()
        if token.kind != "IDENT":
            raise CalverSyntaxError(message, token.line, token.column)
        return self._advance().value
    def _optional_semicolon(self): self._match(";")

    def parse(self):
        statements = []
        while self._current().kind != "EOF":
            statements.append(self._statement())
        return Program(statements)

    def _statement(self):
        # "variabel" is the Indonesian-first spelling; "var" is its short alias.
        if self._match("variabel", "var"):
            return self._var_decl(True)
        if self._match("konst"):
            return self._var_decl(False)
        if self._match("fungsi"):
            return self._function_decl()
        if self._match("jika"):
            return self._if_stmt()
        if self._match("selama"):
            return self._while_stmt()
        if self._match("kembali"):
            value = self._expression()
            self._optional_semicolon()
            return ReturnStmt(value)
        if self._current().kind == "IDENT" and self.tokens[self.i + 1].value == "=":
            name = self._advance().value
            self._advance()
            value = self._expression()
            self._optional_semicolon()
            return AssignStmt(name, value)
        expr = self._expression()
        self._optional_semicolon()
        return ExprStmt(expr)

    def _var_decl(self, mutable):
        name = self._expect_ident("Diharapkan nama variabel setelah kata kunci")
        type_name = None
        if self._match(":"):
            type_name = self._expect_ident("Diharapkan nama tipe setelah ':'")
        self._expect("=", "Deklarasi variabel harus memiliki '='")
        value = self._expression()
        self._optional_semicolon()
        return VarDecl(name, mutable, value, type_name)

    def _function_decl(self):
        name = self._expect_ident("Diharapkan nama fungsi")
        self._expect("(")
        params = []
        if not self._check(")"):
            params.append(self._expect_ident("Diharapkan nama parameter"))
            while self._match(","):
                params.append(self._expect_ident("Diharapkan nama parameter setelah ','"))
        self._expect(")")
        body = self._block()
        return FunctionDecl(name, params, body)

    def _if_stmt(self):
        self._expect("(", "Kondisi 'jika' harus memakai tanda kurung")
        condition = self._expression()
        self._expect(")")
        then_body = self._block()
        else_body = self._block() if self._match("kalau_tidak") else []
        return IfStmt(condition, then_body, else_body)

    def _while_stmt(self):
        self._expect("(", "Kondisi 'selama' harus memakai tanda kurung")
        condition = self._expression()
        self._expect(")")
        return WhileStmt(condition, self._block())

    def _block(self):
        self._expect("{", "Diharapkan '{' untuk memulai blok")
        body = []
        while not self._check("}") and self._current().kind != "EOF":
            body.append(self._statement())
        self._expect("}", "Blok belum ditutup dengan '}'")
        return body

    def _expression(self, min_precedence=1):
        left = self._unary()
        while True:
            op = self._current().value
            precedence = PRECEDENCE.get(op, 0)
            if precedence < min_precedence:
                break
            self._advance()
            right = self._expression(precedence + 1)
            left = Binary(left, op, right)
        return left

    def _unary(self):
        if self._match("-", "!", "bukan"):
            op = self.tokens[self.i - 1].value
            return Unary(op, self._unary())
        expr = self._primary()
        while self._match("("):
            args = []
            if not self._check(")"):
                args.append(self._expression())
                while self._match(","):
                    args.append(self._expression())
            self._expect(")", "Pemanggilan fungsi belum ditutup dengan ')'")
            expr = Call(expr, args)
        return expr

    def _primary(self):
        token = self._current()
        if token.kind == "NUMBER":
            self._advance(); return Literal(token.value)
        if token.kind == "STRING":
            self._advance(); return Literal(token.value)
        if token.kind == "IDENT":
            self._advance()
            if token.value == "benar": return Literal(True)
            if token.value == "salah": return Literal(False)
            if token.value == "kosong": return Literal(None)
            return Variable(token.value)
        if self._match("("):
            expr = self._expression()
            self._expect(")", "Ekspresi belum ditutup dengan ')'")
            return expr
        raise CalverSyntaxError("Diharapkan nilai atau ekspresi", token.line, token.column)

def parse(source: str):
    return Parser(source).parse()
