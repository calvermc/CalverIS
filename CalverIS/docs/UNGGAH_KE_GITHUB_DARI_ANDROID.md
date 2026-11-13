# Mengunggah CalverIS ke GitHub dari Android

## 1. Buat repository kosong

1. Buka https://github.com/new.
2. Nama repository: `CalverIS`.
3. Pilih Public atau Private sesuai kebutuhan.
4. Jangan centang opsi untuk membuat README, `.gitignore`, atau License karena semuanya sudah tersedia di paket proyek.
5. Buat repository.

## 2. Unggah source dari Android

Cara yang paling konsisten untuk mengunggah seluruh struktur folder adalah memakai Git dari lingkungan terminal Android (misalnya Termux):

```bash
pkg update
pkg install git
termux-setup-storage
```

Ekstrak `CalverIS-GitHub-Ready-v0.2.0-alpha.2.zip` ke penyimpanan perangkat. Masuk ke folder `CalverIS`, lalu jalankan:

```bash
git init
git add .
git commit -m "Update CalverIS syntax and Acode plugin to 0.2.0-alpha.2"
git branch -M main
git remote add origin https://github.com/USERNAME/CalverIS.git
git push -u origin main
```

Ganti `USERNAME` dengan username GitHub sendiri. Saat diminta autentikasi HTTPS, gunakan metode autentikasi GitHub yang berlaku; jangan menaruh password atau token di dalam source code.

## 3. Periksa hasil

Buka halaman repository GitHub. Pastikan folder `calveris`, `contoh`, `tests`, `docs`, `acode-plugin`, dan file README terlihat di halaman utama.

Jangan hanya mengunggah ZIP source sebagai satu file jika tujuanmu adalah repository kode yang dapat dibaca dan dikembangkan. Ekstrak ZIP terlebih dahulu, lalu unggah isi folder proyek.
