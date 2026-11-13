import unittest
from pathlib import Path
import tempfile

from calveris.parser import parse
from calveris.runtime import Interpreter
from calveris.polyglot import split_source, build_sources


class CoreTests(unittest.TestCase):
    def run_code(self, source, input_value="Calver"):
        output = []
        interpreter = Interpreter(
            input_fn=lambda prompt="": input_value,
            output_fn=lambda *args: output.append(" ".join(map(str, args))),
        )
        interpreter.run(parse(source))
        return output

    def test_variabel_keyword(self):
        self.assertEqual(self.run_code('variabel nama = "CVIS"\ntampilkan(nama)'), ["CVIS"])

    def test_var_short_alias(self):
        self.assertEqual(self.run_code('var nama = "CVIS"\nnama = "CalverIS"\ntampilkan(nama)'), ["CalverIS"])

    def test_konst_keyword(self):
        self.assertEqual(self.run_code('konst nama = "CVIS"\ntampilkan(nama)'), ["CVIS"])

    def test_constant_cannot_be_reassigned(self):
        with self.assertRaisesRegex(Exception, "konstanta"):
            self.run_code('konst x = 1\nx = 2')

    def test_function_and_kembali(self):
        code = 'fungsi tambah(a, b) { kembali a + b }\ntampilkan(tambah(2, 3))'
        self.assertEqual(self.run_code(code), ["5"])

    def test_jika_kalau_tidak(self):
        code = 'variabel x = 1\njika (x > 2) { tampilkan("ya") } kalau_tidak { tampilkan("tidak") }'
        self.assertEqual(self.run_code(code), ["tidak"])

    def test_selama(self):
        code = 'var x = 1\nselama (x <= 3) { tampilkan(x)\nx = x + 1 }'
        self.assertEqual(self.run_code(code), ["1", "2", "3"])

    def test_tanya_input(self):
        self.assertEqual(self.run_code('variabel nama = tanya("Nama: ")\ntampilkan(nama)', "Dina"), ["Dina"])

    def test_bukan_operator(self):
        code = 'variabel masuk = salah\njika (bukan masuk) { tampilkan("belum masuk") }'
        self.assertEqual(self.run_code(code), ["belum masuk"])

    def test_benar_salah_literals(self):
        code = 'jika (benar dan bukan salah) { tampilkan("ok") }'
        self.assertEqual(self.run_code(code), ["ok"])

    def test_polyglot_split(self):
        source = 'konst x = 1\n\njavascript {\nconst x = "}";\n}\n'
        result = split_source(source)
        self.assertIn('konst x = 1', result.cvis_source)
        self.assertEqual(len(result.blocks), 1)
        self.assertEqual(result.blocks[0].language, 'javascript')
        self.assertIn('const x', result.blocks[0].code)

    def test_build_preserves_cvis_core_and_native_blocks(self):
        source = 'konst judul = "Halo"\nhtml {\n<h1>Halo</h1>\n}'
        with tempfile.TemporaryDirectory() as tmp:
            written = build_sources(source, tmp, 'web')
            names = sorted(Path(p).name for p in written)
            self.assertEqual(names, ['index.html', 'main.cvis'])
            self.assertIn('konst judul', (Path(tmp) / 'main.cvis').read_text())

    def test_build_web_sources(self):
        source = 'html {\n<h1>Hi</h1>\n}\ncss {\nh1 { color: red; }\n}\njavascript {\nconsole.log("ok");\n}'
        with tempfile.TemporaryDirectory() as tmp:
            written = build_sources(source, tmp, 'web')
            names = sorted(Path(p).name for p in written)
            self.assertEqual(names, ['app.js', 'index.html', 'styles.css'])


if __name__ == '__main__':
    unittest.main()
