# Arsitektur CalverIS

## Implementasi alpha

```text
File .cvis
   ├── Lexer → Parser → AST → Interpreter (kode inti CalverIS)
   └── Polyglot Block Extractor → source files per bahasa
```

## Arsitektur target

```text
.cvis → Lexer → Parser → AST → Intermediate Representation (IR)
                                ├── CalverIS Runtime
                                ├── Web Adapter
                                ├── Python Adapter
                                ├── Dart Adapter
                                └── Adapter bahasa lain

Adapters ↔ Interoperability Bridge ↔ Native runtimes / SDKs
```

Setiap bahasa native tetap memakai sintaks dan toolchain aslinya. Bridge harus menentukan format data, aturan pemanggilan, error propagation, lifecycle, dan batas keamanan antar-runtime.

## Batas versi alpha

Pemisah blok polyglot dan ekspor source sudah tersedia. Kode inti disimpan sebagai `main.cvis`, sedangkan blok native diekspor ke file sesuai bahasanya. Adapter runtime dan komunikasi lintas bahasa belum tersedia. Karena itu, source JavaScript/Python/Dart yang diekspor perlu dijalankan menggunakan toolchain masing-masing.
