# Sintaks CalverIS

CalverIS menggunakan sintaks Indonesia sebagai bahasa utama, dengan struktur yang tetap familier bagi pengguna JavaScript.

## Variabel dan konstanta

```cvis
variabel nama = "Calver"  // bentuk lengkap
var umur = 18              // bentuk singkat; sama dengan variabel
konst versi = "0.2.0"      // konstanta; tidak dapat ditugaskan ulang

umur = 19
```

`variabel` dan `var` adalah dua penulisan untuk deklarasi variabel yang dapat diubah. `konst` digunakan untuk nilai yang tidak dapat ditugaskan ulang.

## Fungsi

```cvis
fungsi tambah(a, b) {
    kembali a + b
}

tampilkan(tambah(2, 3))
```

## Kondisi dan perulangan

```cvis
variabel umur = 17

jika (umur >= 18) {
    tampilkan("Dewasa")
} kalau_tidak {
    tampilkan("Belum dewasa")
}

variabel hitung = 1
selama (hitung <= 3) {
    tampilkan(hitung)
    hitung = hitung + 1
}
```

## Input dan logika

```cvis
variabel nama = tanya("Nama kamu: ")
variabel sudahLogin = salah

jika (bukan sudahLogin) {
    tampilkan("Halo, " + nama + ". Silakan masuk.")
}
```

- `tanya()` meminta input dari pengguna.
- `bukan` membalik nilai logika (NOT).
- `benar` dan `salah` adalah nilai logika.

## Kata kunci inti

| CalverIS | Kegunaan |
|---|---|
| `variabel`, `var` | Membuat variabel yang dapat diubah |
| `konst` | Membuat konstanta |
| `fungsi` | Membuat fungsi |
| `kembali` | Mengembalikan nilai dari fungsi |
| `jika` | Percabangan kondisi |
| `kalau_tidak` | Cabang alternatif |
| `selama` | Perulangan selama kondisi benar |
| `tampilkan()` | Menampilkan output |
| `tanya()` | Meminta input |
| `bukan` | Operator NOT |
| `benar`, `salah` | Nilai logika |

## Blok bahasa native

```cvis
javascript {
    const nilai = 10;
    console.log(nilai);
}

python {
    def kuadrat(x):
        return x * x
}
```

Isi blok native dipertahankan sebagai source bahasa asal. Pada versi alpha ini, Core mengekspor blok tersebut ke berkas terpisah; pemanggilan fungsi lintas runtime belum tersedia.
