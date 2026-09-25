import os
import sys
import io
import runpy
import threading
import contextlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "CCI → CIA Converter"

def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("760x540")
        self.minsize(700, 480)
        self.configure(padx=16, pady=16)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Bereit.")
        self.progress_var = tk.DoubleVar(value=0)
        self.files = []

        self._build()
        self._enable_drop()

    def _build(self):
        ttk.Label(self, text=APP_NAME, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            self,
            text="Konvertiert einzelne Dateien oder alle CCI/3DS-Dateien eines Ordners in CIA."
        ).pack(anchor="w", pady=(2, 18))

        f1 = ttk.LabelFrame(self, text="Quelle")
        f1.pack(fill="x", pady=5)

        ttk.Entry(f1, textvariable=self.input_var).pack(
            side="left", fill="x", expand=True, padx=8, pady=8
        )
        ttk.Button(f1, text="Datei auswählen…", command=self.choose_input).pack(
            side="right", padx=(0, 4), pady=8
        )
        ttk.Button(f1, text="Ordner auswählen…", command=self.choose_folder).pack(
            side="right", padx=(0, 8), pady=8
        )

        self.file_info = ttk.Label(self, text="Keine Dateien ausgewählt.")
        self.file_info.pack(anchor="w", pady=(4, 8))

        f2 = ttk.LabelFrame(self, text="Ausgabeordner")
        f2.pack(fill="x", pady=5)

        ttk.Entry(f2, textvariable=self.output_var).pack(
            side="left", fill="x", expand=True, padx=8, pady=8
        )
        ttk.Button(f2, text="Auswählen…", command=self.choose_output).pack(
            side="right", padx=(0, 8), pady=8
        )

        self.convert_btn = ttk.Button(
            self, text="Konvertierung starten", command=self.start
        )
        self.convert_btn.pack(pady=14, ipadx=18, ipady=5)

        ttk.Progressbar(
            self, variable=self.progress_var, maximum=100
        ).pack(fill="x", pady=(0, 8))

        ttk.Label(self, textvariable=self.status_var).pack(anchor="w")

        log_frame = ttk.LabelFrame(self, text="Ausgabe")
        log_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.log = tk.Text(
            log_frame, height=12, wrap="word", state="disabled"
        )
        self.log.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        scroll = ttk.Scrollbar(log_frame, command=self.log.yview)
        scroll.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=scroll.set)

    def _enable_drop(self):
        # Native Tkinter hat keine Windows-Drag-and-Drop-Unterstützung.
        pass

    def choose_input(self):
        p = filedialog.askopenfilename(
            title="CCI/3DS-Datei auswählen",
            filetypes=[
                ("Nintendo 3DS ROM", "*.cci *.3ds"),
                ("Alle Dateien", "*.*")
            ]
        )
        if p:
            self.files = [p]
            self.input_var.set(p)
            self.file_info.configure(text="1 Datei ausgewählt.")
            if not self.output_var.get():
                self.output_var.set(os.path.dirname(p))

    def choose_folder(self):
        folder = filedialog.askdirectory(
            title="Ordner mit CCI/3DS-Dateien auswählen"
        )
        if not folder:
            return

        files = []
        for name in os.listdir(folder):
            full = os.path.join(folder, name)
            if os.path.isfile(full) and name.lower().endswith((".cci", ".3ds")):
                files.append(full)

        files.sort(key=lambda x: os.path.basename(x).lower())

        if not files:
            messagebox.showwarning(
                APP_NAME,
                "In diesem Ordner wurden keine .CCI- oder .3DS-Dateien gefunden."
            )
            return

        self.files = files
        self.input_var.set(folder)
        self.file_info.configure(
            text=f"{len(files)} Datei(en) gefunden."
        )

        if not self.output_var.get():
            self.output_var.set(folder)

        self.write_log(
            f"\nOrdner ausgewählt: {folder}\n"
            f"Gefundene Dateien: {len(files)}\n"
        )

    def choose_output(self):
        p = filedialog.askdirectory(title="Ausgabeordner auswählen")
        if p:
            self.output_var.set(p)

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        out = self.output_var.get().strip().strip('"')

        if not self.files:
            inp = self.input_var.get().strip().strip('"')

            if os.path.isfile(inp) and inp.lower().endswith((".cci", ".3ds")):
                self.files = [inp]
            elif os.path.isdir(inp):
                self.files = [
                    os.path.join(inp, n)
                    for n in os.listdir(inp)
                    if os.path.isfile(os.path.join(inp, n))
                    and n.lower().endswith((".cci", ".3ds"))
                ]
                self.files.sort(key=lambda x: os.path.basename(x).lower())

        if not self.files:
            messagebox.showerror(
                APP_NAME,
                "Bitte zuerst eine Datei oder einen Ordner auswählen."
            )
            return

        if not out:
            out = os.path.dirname(self.files[0])
            self.output_var.set(out)

        os.makedirs(out, exist_ok=True)

        self.convert_btn.configure(state="disabled")
        self.progress_var.set(0)
        self.status_var.set(
            f"Starte Konvertierung von {len(self.files)} Datei(en)…"
        )

        self.write_log(
            f"\n{'=' * 60}\n"
            f"Starte Batch-Konvertierung: {len(self.files)} Datei(en)\n"
            f"Ausgabe: {out}\n"
            f"{'=' * 60}\n"
        )

        threading.Thread(
            target=self._convert_all,
            args=(list(self.files), out),
            daemon=True
        ).start()

    def _convert_all(self, files, out):
        script = resource_path(os.path.join("vendor", "3dsconv.py"))

        if not os.path.isfile(script):
            self.after(
                0,
                self._failed,
                "Die eingebettete 3dsconv.py wurde nicht gefunden."
            )
            return

        successful = 0
        failed = 0
        total = len(files)

        for index, inp in enumerate(files, start=1):
            self.after(
                0,
                self.status_var.set,
                f"Datei {index}/{total}: {os.path.basename(inp)}"
            )

            self.after(
                0,
                self.write_log,
                f"\n[{index}/{total}] {os.path.basename(inp)}\n"
            )

            try:
                old_argv = sys.argv[:]
                old_cwd = os.getcwd()
                buf = io.StringIO()

                try:
                    os.chdir(out)

                    sys.argv = [
                        script,
                        "--output=" + out,
                        "--overwrite",
                        "--verbose",
                        inp,
                    ]

                    with contextlib.redirect_stdout(buf), \
                         contextlib.redirect_stderr(buf):
                        try:
                            runpy.run_path(script, run_name="__main__")
                        except SystemExit as e:
                            if e.code not in (None, 0):
                                raise RuntimeError(
                                    f"3dsconv wurde mit Exit-Code {e.code} beendet."
                                )
                finally:
                    sys.argv = old_argv
                    os.chdir(old_cwd)

                output = buf.getvalue()
                self.after(0, self.write_log, output)

                expected = os.path.join(
                    out,
                    os.path.splitext(os.path.basename(inp))[0] + ".cia"
                )

                if os.path.isfile(expected):
                    successful += 1
                    self.after(
                        0,
                        self.write_log,
                        f"  ✓ Erfolgreich: {os.path.basename(expected)}\n"
                    )
                else:
                    failed += 1
                    self.after(
                        0,
                        self.write_log,
                        "  ✗ CIA-Datei wurde nicht gefunden.\n"
                    )

            except Exception as e:
                failed += 1
                self.after(
                    0,
                    self.write_log,
                    f"  ✗ FEHLER: {e}\n"
                )

            progress = (index / total) * 100
            self.after(0, self.progress_var.set, progress)

        self.after(
            0,
            self._batch_finished,
            successful,
            failed,
            total
        )

    def _batch_finished(self, successful, failed, total):
        self.convert_btn.configure(state="normal")

        if failed == 0:
            self.status_var.set(
                f"Fertig – {successful}/{total} Datei(en) erfolgreich konvertiert."
            )
            messagebox.showinfo(
                APP_NAME,
                f"Alle {total} Dateien wurden erfolgreich konvertiert."
            )
        else:
            self.status_var.set(
                f"Fertig – {successful} erfolgreich, {failed} fehlgeschlagen."
            )
            messagebox.showwarning(
                APP_NAME,
                f"Konvertierung abgeschlossen.\n\n"
                f"Erfolgreich: {successful}\n"
                f"Fehlgeschlagen: {failed}\n"
                f"Gesamt: {total}\n\n"
                f"Details findest du im Ausgabefenster."
            )

    def _failed(self, reason):
        self.convert_btn.configure(state="normal")
        self.progress_var.set(0)
        self.status_var.set("Konvertierung fehlgeschlagen.")
        self.write_log(f"\nFEHLER: {reason}\n")
        messagebox.showerror(
            APP_NAME,
            f"Konvertierung fehlgeschlagen:\n\n{reason}"
        )

if __name__ == "__main__":
    App().mainloop()
