import argparse
from pathlib import Path
import sys
from . import __version__
from .errors import CalverError
from .parser import parse
from .runtime import Interpreter
from .polyglot import split_source, build_sources


def _read(path):
    p = Path(path)
    if not p.exists(): raise CalverError(f"Berkas tidak ditemukan: {path}")
    if p.suffix.lower() != ".cvis": raise CalverError("Berkas sumber CalverIS harus berekstensi .cvis")
    return p.read_text(encoding="utf-8")


def command_periksa(args):
    source = _read(args.berkas)
    split = split_source(source)
    if split.cvis_source.strip(): parse(split.cvis_source)
    print(f"Sintaks CalverIS valid: {args.berkas}")
    if split.blocks:
        languages = ", ".join(sorted({b.language for b in split.blocks}))
        print(f"Blok native terdeteksi: {languages}")
        print("Catatan: blok native diperiksa strukturnya, bukan sintaks internal bahasanya.")
    return 0


def command_jalankan(args):
    source = _read(args.berkas)
    split = split_source(source)
    if split.blocks:
        print("Berkas berisi blok bahasa native.", file=sys.stderr)
        print("Gunakan 'calver bangun' untuk mengekspor blok tersebut. Eksekusi lintas runtime belum tersedia.", file=sys.stderr)
        return 2
    program = parse(source)
    Interpreter().run(program)
    return 0


def command_bangun(args):
    source = _read(args.berkas)
    split = split_source(source)
    if split.cvis_source.strip():
        parse(split.cvis_source)
    try:
        written = build_sources(source, args.keluaran, args.target)
    except ValueError as exc:
        raise CalverError(str(exc)) from exc
    print(f"Build selesai: {len(written)} berkas dibuat di {args.keluaran}")
    for path in written: print(f"- {path}")
    print("Catatan: ini ekspor source native, bukan kompilasi atau eksekusi lintas runtime.")
    return 0


def make_parser():
    parser = argparse.ArgumentParser(prog="calver", description="CalverIS - bahasa pemrograman Indonesia-first")
    sub = parser.add_subparsers(dest="perintah")
    sub.add_parser("versi", help="Menampilkan versi CalverIS")
    sub.add_parser("bantu", help="Menampilkan bantuan")
    for name, help_text, handler in [
        ("periksa", "Memeriksa sintaks berkas .cvis", command_periksa),
        ("jalankan", "Menjalankan program inti CalverIS", command_jalankan),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("berkas")
        p.set_defaults(handler=handler)
    build = sub.add_parser("bangun", help="Mengekspor blok bahasa native")
    build.add_argument("berkas")
    build.add_argument("--target", choices=["sumber", "web"], default="sumber")
    build.add_argument("--keluaran", default="dist")
    build.set_defaults(handler=command_bangun)
    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)
    if args.perintah == "versi":
        print(f"CalverIS {__version__}")
        return 0
    if args.perintah in (None, "bantu"):
        parser.print_help()
        return 0
    try:
        return args.handler(args)
    except CalverError as exc:
        print(f"Kesalahan: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Kesalahan internal: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
