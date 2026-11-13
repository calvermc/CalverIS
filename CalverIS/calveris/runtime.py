from dataclasses import dataclass
from .parser import (Program, VarDecl, FunctionDecl, IfStmt, WhileStmt, ReturnStmt,
                     AssignStmt, ExprStmt, Literal, Variable, Unary, Binary, Call)
from .errors import CalverRuntimeError

@dataclass
class Cell:
    value: object
    mutable: bool
    type_name: str | None = None

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}
    def define(self, name, value, mutable=True, type_name=None):
        if name in self.values:
            raise CalverRuntimeError(f"Nama '{name}' sudah dideklarasikan pada ruang lingkup ini")
        _check_type(name, value, type_name)
        self.values[name] = Cell(value, mutable, type_name)
    def cell(self, name):
        if name in self.values: return self.values[name]
        if self.parent: return self.parent.cell(name)
        raise CalverRuntimeError(f"Nama '{name}' belum dikenal")
    def get(self, name): return self.cell(name).value
    def assign(self, name, value):
        cell = self.cell(name)
        if not cell.mutable:
            raise CalverRuntimeError(f"'{name}' adalah konstanta dan tidak dapat diubah")
        _check_type(name, value, cell.type_name)
        cell.value = value


def _check_type(name, value, type_name):
    if type_name is None: return
    checks = {
        "angka": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
        "teks": lambda x: isinstance(x, str),
        "logika": lambda x: isinstance(x, bool),
        "daftar": lambda x: isinstance(x, list),
        "objek": lambda x: isinstance(x, dict),
    }
    if type_name not in checks:
        raise CalverRuntimeError(f"Tipe '{type_name}' belum didukung")
    if not checks[type_name](value):
        raise CalverRuntimeError(f"Nilai untuk '{name}' tidak sesuai tipe '{type_name}'")

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

@dataclass
class UserFunction:
    declaration: FunctionDecl
    closure: Environment

class Interpreter:
    def __init__(self, input_fn=input, output_fn=print):
        self.globals = Environment()
        self.environment = self.globals
        self.output_fn = output_fn
        self._install_builtins(input_fn)

    def _install_builtins(self, input_fn):
        self.globals.define("tampilkan", lambda *args: self.output_fn(*args), False)
        self.globals.define("tanya", lambda prompt="": input_fn(str(prompt)), False)
        self.globals.define("panjang", lambda value: len(value), False)
        self.globals.define("ke_angka", lambda value: float(value) if "." in str(value) else int(value), False)
        self.globals.define("ke_teks", lambda value: str(value), False)
        self.globals.define("jenis", self._jenis, False)

    @staticmethod
    def _jenis(value):
        if value is None: return "kosong"
        if isinstance(value, bool): return "logika"
        if isinstance(value, (int, float)): return "angka"
        if isinstance(value, str): return "teks"
        if isinstance(value, list): return "daftar"
        if isinstance(value, dict): return "objek"
        return type(value).__name__

    def run(self, program: Program):
        result = None
        for statement in program.statements:
            result = self._execute(statement)
        return result

    def _execute_block(self, statements, environment):
        previous = self.environment
        self.environment = environment
        try:
            result = None
            for statement in statements:
                result = self._execute(statement)
            return result
        finally:
            self.environment = previous

    def _execute(self, node):
        if isinstance(node, VarDecl):
            value = self._evaluate(node.value)
            self.environment.define(node.name, value, node.mutable, node.type_name)
            return value
        if isinstance(node, FunctionDecl):
            self.environment.define(node.name, UserFunction(node, self.environment), False)
            return None
        if isinstance(node, AssignStmt):
            value = self._evaluate(node.value)
            self.environment.assign(node.name, value)
            return value
        if isinstance(node, ExprStmt):
            return self._evaluate(node.expression)
        if isinstance(node, IfStmt):
            if self._truthy(self._evaluate(node.condition)):
                return self._execute_block(node.then_body, Environment(self.environment))
            if node.else_body:
                return self._execute_block(node.else_body, Environment(self.environment))
            return None
        if isinstance(node, WhileStmt):
            result = None
            count = 0
            while self._truthy(self._evaluate(node.condition)):
                result = self._execute_block(node.body, Environment(self.environment))
                count += 1
                if count > 1_000_000:
                    raise CalverRuntimeError("Perulangan dihentikan karena melewati batas 1.000.000 iterasi")
            return result
        if isinstance(node, ReturnStmt):
            raise ReturnSignal(self._evaluate(node.value))
        raise CalverRuntimeError(f"Pernyataan belum didukung: {type(node).__name__}")

    def _evaluate(self, node):
        if isinstance(node, Literal): return node.value
        if isinstance(node, Variable): return self.environment.get(node.name)
        if isinstance(node, Unary):
            value = self._evaluate(node.right)
            if node.operator == "-": return -value
            if node.operator in ("!", "bukan"): return not self._truthy(value)
        if isinstance(node, Binary):
            left = self._evaluate(node.left)
            if node.operator in ("dan", "and", "&&"):
                return self._truthy(left) and self._truthy(self._evaluate(node.right))
            if node.operator in ("atau", "or", "||"):
                return self._truthy(left) or self._truthy(self._evaluate(node.right))
            right = self._evaluate(node.right)
            operations = {
                "+": lambda: left + right, "-": lambda: left - right,
                "*": lambda: left * right, "/": lambda: left / right,
                "%": lambda: left % right, "==": lambda: left == right,
                "!=": lambda: left != right, "<": lambda: left < right,
                "<=": lambda: left <= right, ">": lambda: left > right,
                ">=": lambda: left >= right,
            }
            if node.operator in operations:
                try: return operations[node.operator]()
                except Exception as exc: raise CalverRuntimeError(f"Operasi '{node.operator}' gagal: {exc}") from exc
        if isinstance(node, Call):
            callee = self._evaluate(node.callee)
            args = [self._evaluate(arg) for arg in node.arguments]
            if isinstance(callee, UserFunction):
                decl = callee.declaration
                if len(args) != len(decl.params):
                    raise CalverRuntimeError(f"Fungsi '{decl.name}' membutuhkan {len(decl.params)} argumen, menerima {len(args)}")
                env = Environment(callee.closure)
                for name, value in zip(decl.params, args): env.define(name, value, True)
                try: return self._execute_block(decl.body, env)
                except ReturnSignal as signal: return signal.value
            if callable(callee):
                try: return callee(*args)
                except Exception as exc: raise CalverRuntimeError(f"Pemanggilan fungsi gagal: {exc}") from exc
            raise CalverRuntimeError("Nilai yang dipanggil bukan fungsi")
        raise CalverRuntimeError(f"Ekspresi belum didukung: {type(node).__name__}")

    @staticmethod
    def _truthy(value):
        return bool(value)

def interpret(source: str, input_fn=input, output_fn=print):
    from .parser import parse
    return Interpreter(input_fn=input_fn, output_fn=output_fn).run(parse(source))
