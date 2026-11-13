(function () {
  "use strict";

  const PLUGIN_ID = "com.calver.calveris";
  const MODE_NAME = "calveris";

  const KEYWORDS = new Set([
    "variabel", "var", "konst", "fungsi", "kembali", "jika",
    "kalau_tidak", "selama", "benar", "salah", "kosong",
    "dan", "atau", "bukan"
  ]);
  const BUILTINS = new Set([
    "tampilkan", "tanya", "panjang", "ke_angka", "ke_teks", "jenis"
  ]);
  const BLOCKS = new Set([
    "html", "css", "javascript", "js", "typescript", "ts", "python", "py",
    "dart", "java", "kotlin", "swift", "c", "cpp", "csharp", "php", "ruby",
    "go", "rust", "lua", "sql"
  ]);

  const COMPLETIONS = [
    ...[...KEYWORDS].map((label) => ({ label, type: "keyword" })),
    ...[...BUILTINS].map((label) => ({ label, type: "function" })),
    ...[...BLOCKS].map((label) => ({ label, type: "type" }))
  ];

  function token(stream, state) {
    if (stream.eatSpace()) return null;

    if (stream.match("//")) {
      stream.skipToEnd();
      return "comment";
    }

    const ch = stream.peek();
    if (ch === '"' || ch === "'" || ch === "`") {
      const quote = stream.next();
      let escaped = false;
      while (!stream.eol()) {
        const current = stream.next();
        if (escaped) escaped = false;
        else if (current === "\\") escaped = true;
        else if (current === quote) break;
      }
      return "string";
    }

    if (/[0-9]/.test(ch || "")) {
      stream.match(/^[0-9]+(?:\.[0-9]+)?/);
      return "number";
    }

    if (/[A-Za-z_\u00C0-\u024F]/.test(ch || "")) {
      const word = stream.match(/^[A-Za-z_\u00C0-\u024F][A-Za-z0-9_\u00C0-\u024F]*/)[0];
      if (KEYWORDS.has(word)) return "keyword";
      if (BUILTINS.has(word)) return "function";
      if (BLOCKS.has(word)) return "typeName";
      return "variableName";
    }

    if (/[{}()[\],.;:+*/%=<>!-]/.test(ch || "")) {
      stream.next();
      return "operator";
    }

    stream.next();
    return null;
  }

  const mode = {
    startState() { return {}; },
    token,
    languageData: {
      commentTokens: { line: "//" }
    }
  };

  if (typeof window !== "undefined" && window.acode) {
    const acode = window.acode;
    let registered = false;

    acode.setPluginInit(PLUGIN_ID, async () => {
      const editorLanguages = acode.require("editorLanguages");
      const cm = acode.require("codemirror");
      const StreamLanguage = cm && cm.language && cm.language.StreamLanguage;
      if (!StreamLanguage) {
        throw new Error("CalverIS: CodeMirror StreamLanguage tidak tersedia pada versi Acode ini.");
      }

      const extensions = [StreamLanguage.define(mode)];
      const autocomplete = cm.autocomplete;
      if (autocomplete && autocomplete.autocompletion && autocomplete.completeFromList) {
        extensions.push(autocomplete.autocompletion({
          override: [autocomplete.completeFromList(COMPLETIONS)]
        }));
      }

      editorLanguages.register(
        MODE_NAME,
        ["cvis"],
        "CalverIS",
        async () => extensions,
        { aliases: ["CVIS", "Calver Indonesian Script"] }
      );
      registered = true;
    });

    acode.setPluginUnmount(PLUGIN_ID, () => {
      if (registered) {
        try { acode.require("editorLanguages").unregister(MODE_NAME); }
        finally { registered = false; }
      }
    });
  }
})();
