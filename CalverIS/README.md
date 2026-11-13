# CalverIS (CVIS)

**Calver Indonesian Script** adalah bahasa pemrograman dengan sintaks utama Bahasa Indonesia. CalverIS dirancang agar mudah dipelajari tanpa membatasi developer pada satu bahasa atau runtime.

> **Satu bahasa utama. Banyak teknologi. Satu ekosistem.**

## Status proyek

**Versi pengembangan: `0.2.0-alpha.2`**

Yang tersedia dalam paket ini:

- Interpreter dasar untuk subset sintaks CalverIS.
- Deklarasi variabel menggunakan `variabel` atau alias singkat `var`.
- Deklarasi konstanta menggunakan `konst`.
- Fungsi, kondisi, perulangan, input, output, dan operator logika dasar.
- CLI `calver` untuk memeriksa, menjalankan, dan membangun berkas.
- Pemisah blok polyglot untuk mengekspor blok bahasa native menjadi berkas sumber terpisah.
- Plugin Acode untuk ekstensi `.cvis`, syntax highlighting dasar, dan autocomplete.
- Tes otomatis dan GitHub Actions.

Yang **belum** tersedia:

- Pemanggilan fungsi lintas runtime (misalnya JavaScript memanggil fungsi Python secara langsung).
- Compiler produksi untuk Android, iOS, desktop, dan seluruh target lain.
- Syntax highlighting bertingkat penuh untuk semua bahasa di dalam satu file `.cvis`.
- CalverIS Studio, debugger, dan package manager.

## Prinsip desain

1. **Indonesia First** — sintaks inti dan pesan kesalahan menggunakan Bahasa Indonesia yang sederhana.
2. **Native Compatibility** — kode di dalam blok bahasa native dipertahankan tanpa diterjemahkan.
3. **Familiar** — struktur, tanda kurung, kurung kurawal, dan operator tetap familier bagi pengguna JavaScript.
4. **Polyglot** — beberapa bahasa dapat ditempatkan dalam satu berkas `.cvis`.
5. **Modular** — adapter dan runtime ditambahkan bertahap tanpa mengubah bahasa inti.

## Sintaks CalverIS

```cvis
konst namaAplikasi = "CalverIS"
variabel umur = 18
var nama = "Calver"

fungsi sapa(panggilan) {
    kembali "Halo, " + panggilan
}

jika (umur >= 17) {
    tampilkan(sapa(nama))
} kalau_tidak {
    tampilkan("Selamat belajar!")
}
```

### Kata kunci inti

| CalverIS | Kegunaan |
|---|---|
| `variabel` / `var` | Variabel yang dapat diubah |
| `konst` | Konstanta yang tidak dapat ditugaskan ulang |
| `fungsi` | Membuat fungsi |
| `kembali` | Mengembalikan nilai |
| `jika` | Percabangan |
| `kalau_tidak` | Cabang alternatif |
| `selama` | Perulangan |
| `tampilkan()` | Output |
| `tanya()` | Input |
| `bukan` | NOT |
| `benar` / `salah` | Nilai logika |

`variabel` dan `var` memiliki fungsi yang sama. Gunakan `variabel` untuk penulisan Indonesia penuh atau `var` jika ingin lebih singkat.

Lihat [docs/SINTAKS.md](docs/SINTAKS.md) untuk panduan sintaks lebih lengkap.

## Polyglot: satu file, beberapa bahasa

```cvis
html {
    <!doctype html>
    <html>
      <body><h1 id="judul">Halo CalverIS</h1></body>
    </html>
}

css {
    h1 { color: royalblue; }
}

javascript {
    const judul = document.getElementById("judul");
    console.log(judul.textContent);
}

python {
    def sapa(nama):
        return f"Halo {nama}"
}
```

Blok native mempertahankan sintaks bahasa asal. Bahasa yang dikenali oleh pemisah blok saat ini meliputi HTML, CSS, JavaScript, TypeScript, Python, Dart, Java, Kotlin, Swift, C, C++, C#, PHP, Ruby, Go, Rust, Lua, dan SQL.

**Catatan:** `calver bangun` mengekspor setiap blok ke berkas native yang sesuai. Ini belum berarti runtime lintas bahasa sudah terhubung. Bridge untuk pemanggilan fungsi dan pertukaran data antar-runtime merupakan pekerjaan berikutnya.

## Instalasi Core

Persyaratan: Python 3.10 atau lebih baru.

```bash
python -m pip install -e .
calver versi
calver periksa contoh/halo.cvis
calver jalankan contoh/halo.cvis
```

Tanpa instalasi:

```bash
python -m calveris.cli versi
python -m calveris.cli periksa contoh/halo.cvis
python -m calveris.cli jalankan contoh/halo.cvis
```

## Perintah CLI

```bash
calver bantu
calver versi
calver periksa contoh/halo.cvis
calver jalankan contoh/halo.cvis
calver bangun contoh/polyglot-web.cvis --target web --keluaran dist
calver bangun contoh/polyglot-campuran.cvis --target sumber --keluaran dist
```

- `periksa`: memeriksa sintaks inti dan struktur blok bahasa.
- `jalankan`: menjalankan subset program CalverIS inti.
- `bangun`: mengekspor blok bahasa native ke folder keluaran.

## Plugin Acode

Plugin Acode menambahkan dukungan editor untuk file `.cvis`, bukan menjalankan Core. Fitur awalnya:

- Mengenali ekstensi `.cvis`.
- Syntax highlighting dasar untuk sintaks CalverIS dan label blok polyglot.
- Autocomplete kata kunci dan fungsi bawaan.

Cara memasang:

1. Unduh `acode-plugin/calveris-acode-plugin-0.2.0.zip` ke HP.
2. Buka Acode → **Settings → Plugins**.
3. Tekan **+ → LOCAL**.
4. Pilih ZIP plugin, lalu pasang.
5. Buka atau buat file berekstensi `.cvis`.

## Pengujian

```bash
python -m unittest discover -s tests -v
node --check acode-plugin/main.js
```

## Kontribusi

Issue, laporan bug, usulan sintaks, dan kontribusi kode dipersilakan. Perubahan sintaks harus disertai tes dan pembaruan dokumentasi.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
