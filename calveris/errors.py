class CalverError(Exception):
    """Kesalahan yang dapat ditampilkan kepada pengguna CalverIS."""


class CalverSyntaxError(CalverError):
    def __init__(self, message: str, line: int = 1, column: int = 1):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} (baris {line}, kolom {column})")


class CalverRuntimeError(CalverError):
    pass
