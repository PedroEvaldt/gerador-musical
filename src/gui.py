"""
Interface gráfica do Gerador de Música por Texto.
Arquivo: src/gui.py

Esta classe é responsável apenas por construir os widgets do Tkinter e
conectar eventos da interface aos colaboradores que de fato implementam
cada funcionalidade (arquivos de texto, exportação MIDI, reprodução).
Toda a lógica de negócio foi extraída para
`music_generator.gui.*`, mantendo `MusicGeneratorApp` com uma única
responsabilidade: orquestrar a interface (princípio da Responsabilidade
Única). As dependências concretas (player de áudio, catálogo de
instrumentos, serviços) são recebidas no construtor em vez de
instanciadas internamente, para que a classe dependa apenas de
abstrações e possa ser testada com dublês (princípio da Inversão de
Dependência).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from music_generator.domain.settings import PlaybackSettings
from music_generator.gui.instrument_catalog import InstrumentCatalog, InMemoryInstrumentCatalog
from music_generator.gui.midi_export_service import MidiExportService
from music_generator.gui.playback_controller import PlaybackController
from music_generator.gui.text_file_service import TextFileService
from music_generator.infrastructure.audio.fluidsynth_player import FluidSynthPlayer


DEFAULT_BPM = 180
DEFAULT_OCTAVE = 4
DEFAULT_VOLUME = 64  # meio do slider (0–127)

# Caminho do SoundFont mantido como estava: cada ambiente de execução
# pode precisar de um caminho diferente; ajuste aqui se necessário.
DEFAULT_SOUNDFONT_PATH = "C:\\mysoundfont\\FluidR3_GM.sf2"


def _default_player_factory() -> FluidSynthPlayer:
    return FluidSynthPlayer(soundfont_path=DEFAULT_SOUNDFONT_PATH)


class MusicGeneratorApp(tk.Tk):
    def __init__(
        self,
        instrument_catalog: InstrumentCatalog | None = None,
        text_file_service: TextFileService | None = None,
        midi_export_service: MidiExportService | None = None,
        playback_controller: PlaybackController | None = None,
    ) -> None:
        super().__init__()

        self.title("INF01120 - Gerador de Música por Texto")
        self.resizable(False, False)
        self.configure(bg="#d0d0d0")

        # Colaboradores injetáveis — cada um com uma única responsabilidade.
        # Os padrões abaixo preservam o comportamento atual do app quando
        # nenhuma dependência é informada (uso normal via main()).
        self._instrument_catalog = instrument_catalog or InMemoryInstrumentCatalog()
        self._text_file_service = text_file_service or TextFileService()
        self._midi_export_service = midi_export_service or MidiExportService()
        self._playback_controller = playback_controller or PlaybackController(
            player_factory=_default_player_factory,
        )

        self._progress_job: str | None = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Título ──────────────────────────────────────────────────────
        header = tk.Frame(self, bg="#808080")
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="INF01120 - Gerador de Música por Texto",
            font=("Arial", 14, "bold"),
            bg="#808080",
            fg="white",
            pady=10,
        ).pack()

        # ── Área de texto ───────────────────────────────────────────────
        text_frame = tk.Frame(self, bg="#d0d0d0", padx=40, pady=20)
        text_frame.pack(fill=tk.BOTH)

        tk.Label(
            text_frame,
            text="Insira seu texto abaixo:",
            font=("Arial", 10, "bold"),
            bg="#d0d0d0",
        ).pack(anchor="w")

        self._text_box = tk.Text(
            text_frame,
            width=70,
            height=10,
            font=("Arial", 11),
            relief=tk.FLAT,
            bg="#c0c0c0",
            insertbackground="black",
            wrap=tk.WORD,
        )
        self._text_box.pack(fill=tk.BOTH, pady=(4, 0))

        # ── Botões da Área de Texto ─────────────────────────────────────
        text_btn_frame = tk.Frame(text_frame, bg="#d0d0d0")
        text_btn_frame.pack(fill=tk.X)

        # Botão import
        tk.Button(
            text_btn_frame,
            text="Importar .txt",
            font=("Arial", 10),
            command=self._on_import_file,
            relief=tk.RAISED,
            bg="#d0d0d0",
            padx=10,
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Botão salvar
        tk.Button(
            text_btn_frame,
            text="Salvar .txt",
            font=("Arial", 10),
            command=self._on_save_file,
            relief=tk.RAISED,
            bg="#d0d0d0",
            padx=10,
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Botão limpar texto
        tk.Button(
            text_btn_frame,
            text="Limpar Texto",
            font=("Arial", 10),
            command=self._on_clear,
            relief=tk.RAISED,
            bg="#d0d0d0",
            padx=10,
        ).pack(side=tk.LEFT)

        # Botão exportar MIDI
        tk.Button(
            text_btn_frame,
            text="Exportar MIDI (.mid)",
            font=("Arial", 10),
            command=self._on_export_midi,
            relief=tk.RAISED,
            bg="#d0d0d0",
            padx=10,
        ).pack(side=tk.LEFT, padx=(10, 0))

        # ── Configurações ───────────────────────────────────────────────
        config_frame = tk.Frame(self, bg="#808080", padx=20, pady=14)
        config_frame.pack(fill=tk.X)

        tk.Label(
            config_frame,
            text="Configurações",
            font=("Arial", 10, "bold"),
            bg="#808080",
            fg="white",
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        # Instrumento inicial
        tk.Label(config_frame, text="Instrumento inicial:", bg="#808080", fg="white").grid(
            row=1, column=0, sticky="w", padx=(0, 8)
        )
        self._instrument_var = tk.StringVar(value=self._instrument_catalog.default_name())
        self._instrument_combo = ttk.Combobox(
            config_frame,
            textvariable=self._instrument_var,
            values=list(self._instrument_catalog.names()),
            state="readonly",
            width=18,
        )
        self._instrument_combo.grid(row=2, column=0, sticky="w", padx=(0, 30))

        # BPM
        tk.Label(config_frame, text="BPM:", bg="#808080", fg="white").grid(
            row=1, column=1, sticky="w"
        )
        self._bpm_var = tk.IntVar(value=DEFAULT_BPM)
        bpm_spin = tk.Spinbox(
            config_frame,
            from_=20,
            to=300,
            textvariable=self._bpm_var,
            width=6,
            font=("Arial", 11),
        )
        bpm_spin.grid(row=2, column=1, sticky="w", padx=(0, 30))

        # Oitava padrão
        tk.Label(config_frame, text="Oitava Padrão:", bg="#808080", fg="white").grid(
            row=3, column=0, sticky="w", pady=(10, 0)
        )
        self._octave_var = tk.IntVar(value=DEFAULT_OCTAVE)
        octave_spin = tk.Spinbox(
            config_frame,
            from_=0,
            to=9,
            textvariable=self._octave_var,
            width=4,
            font=("Arial", 11),
        )
        octave_spin.grid(row=4, column=0, sticky="w")

        # Volume inicial
        tk.Label(config_frame, text="Volume inicial:", bg="#808080", fg="white").grid(
            row=3, column=1, sticky="w", pady=(10, 0)
        )

        volume_row = tk.Frame(config_frame, bg="#808080")
        volume_row.grid(row=4, column=1, columnspan=2, sticky="w")

        tk.Label(volume_row, text="🔈", bg="#808080", fg="white", font=("Arial", 12)).pack(
            side=tk.LEFT
        )
        self._volume_var = tk.IntVar(value=DEFAULT_VOLUME)
        self._volume_slider = tk.Scale(
            volume_row,
            from_=0,
            to=127,
            orient=tk.HORIZONTAL,
            variable=self._volume_var,
            length=220,
            bg="#808080",
            fg="white",
            troughcolor="#555555",
            highlightthickness=0,
            showvalue=False,
        )
        self._volume_slider.pack(side=tk.LEFT)

        # ── Controles de playback ───────────────────────────────────────
        control_frame = tk.Frame(self, bg="#b0b0b0", padx=14, pady=10)
        control_frame.pack(fill=tk.X)

        # Botão play
        self._play_btn = tk.Button(
            control_frame,
            text="▶",
            font=("Arial", 16),
            width=3,
            command=self._on_play,
            relief=tk.RAISED,
            bg="#d0d0d0",
        )
        self._play_btn.pack(side=tk.LEFT, padx=(0, 4))

        # Botão pause
        self._pause_btn = tk.Button(
            control_frame,
            text="⏸",
            font=("Arial", 16),
            width=3,
            command=self._on_pause,
            relief=tk.RAISED,
            bg="#d0d0d0",
            state=tk.DISABLED,
        )
        self._pause_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Tempo decorrido
        self._time_label = tk.Label(
            control_frame,
            text="00:00",
            font=("Arial", 11, "bold"),
            bg="#b0b0b0",
        )
        self._time_label.pack(side=tk.LEFT, padx=(0, 8))

        # Barra de progresso
        self._progress = ttk.Progressbar(
            control_frame,
            orient=tk.HORIZONTAL,
            length=380,
            mode="determinate",
        )
        self._progress.pack(side=tk.LEFT)

        # ── Barra de status ─────────────────────────────────────────────
        status_bar = tk.Frame(self, bg="#909090", pady=4)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(status_bar, text="♩", bg="#909090", fg="white", font=("Arial", 12)).pack(
            side=tk.LEFT, padx=(8, 4)
        )
        self._status_var = tk.StringVar(value="Pronto")
        tk.Label(
            status_bar,
            textvariable=self._status_var,
            bg="#909090",
            fg="white",
            font=("Arial", 10),
        ).pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Handlers — cada um delega a lógica de negócio ao colaborador
    # responsável, mantendo aqui apenas leitura de widgets e feedback
    # visual (mensagens, status, habilitação de botões).
    # ------------------------------------------------------------------

    def _on_import_file(self) -> None:
        """Abre uma janela para selecionar um arquivo .txt e joga o conteúdo na caixa de texto."""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo de texto",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )

        if not file_path:
            return

        try:
            content = self._text_file_service.read(file_path)
        except Exception as exc:
            messagebox.showerror("Erro de leitura", f"Não foi possível ler o arquivo:\n{exc}")
            return

        self._text_box.delete("1.0", tk.END)
        self._text_box.insert(tk.END, content)

    def _on_save_file(self) -> None:
        """Abre uma janela para salvar o conteúdo atual da caixa de texto em um arquivo .txt."""
        content = self._text_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Texto vazio", "Não há texto digitado para salvar.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Salvar arquivo de texto",
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )

        if not file_path:
            return

        try:
            self._text_file_service.write(file_path, content)
            self._status_var.set("Texto salvo com sucesso!")
        except Exception as exc:
            messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o arquivo:\n{exc}")

    def _on_play(self) -> None:
        """Inicia a reprodução a partir do texto e configurações atuais."""
        if self._playback_controller.is_playing():
            return

        text = self._text_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Texto vazio", "Insira algum texto antes de reproduzir.")
            return

        try:
            settings = self._build_settings()
        except ValueError as exc:
            messagebox.showerror("Configuração inválida", str(exc))
            return

        try:
            self._playback_controller.start(text, settings)
        except Exception as exc:
            messagebox.showerror("Erro ao reproduzir", str(exc))
            return

        self._play_btn.config(state=tk.DISABLED)
        self._pause_btn.config(state=tk.NORMAL, text="⏸")

        self._progress["value"] = 0
        self._status_var.set("Reproduzindo...")
        self._tick_progress()

    def _on_pause(self) -> None:
        """Alterna entre pause e retomada (stop/start simples, pois não há seek)."""
        if self._playback_controller.is_playing():
            self._playback_controller.pause()
            self._pause_btn.config(text="▶▶")
            self._status_var.set("Pausado")
            if self._progress_job:
                self.after_cancel(self._progress_job)
        else:
            self._pause_btn.config(text="⏸")
            self._playback_controller.resume()
            self._status_var.set("Reproduzindo...")
            self._tick_progress()

    def _on_clear(self) -> None:
        self._text_box.delete("1.0", tk.END)

    def _on_export_midi(self) -> None:
        """Gera a composição polifônica e salva como arquivo .mid escolhido pelo usuário."""
        text = self._text_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Texto vazio", "Insira algum texto antes de exportar.")
            return

        try:
            settings = self._build_settings()
        except ValueError as exc:
            messagebox.showerror("Configuração inválida", str(exc))
            return

        file_path = filedialog.asksaveasfilename(
            title="Exportar arquivo MIDI",
            defaultextension=".mid",
            filetypes=[("Arquivo MIDI", "*.mid"), ("Todos os arquivos", "*.*")],
        )
        if not file_path:
            return  # usuário cancelou

        try:
            self._midi_export_service.export(text, settings, file_path)
            self._status_var.set(f"MIDI exportado: {file_path}")
        except Exception as exc:
            messagebox.showerror("Erro ao exportar MIDI", f"Não foi possível salvar o arquivo:\n{exc}")

    def _on_close(self) -> None:
        self._playback_controller.close()
        self.destroy()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_settings(self) -> PlaybackSettings:
        return PlaybackSettings(
            bpm=self._bpm_var.get(),
            initial_volume=self._volume_var.get(),
            default_octave=self._octave_var.get(),
            initial_instrument=self._instrument_catalog.midi_program(
                self._instrument_var.get()
            ),
        )

    def _tick_progress(self) -> None:
        """Atualiza barra de progresso e tempo a cada 200 ms."""
        if not self._playback_controller.is_playing():
            self._play_btn.config(state=tk.NORMAL)
            self._pause_btn.config(state=tk.DISABLED, text="⏸")
            self._status_var.set("Pronto")
            self._progress["value"] = 0
            self._time_label.config(text="00:00")
            return

        percentage = self._playback_controller.advance_progress(0.2)
        self._progress["value"] = percentage

        elapsed = self._playback_controller.elapsed_seconds
        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        self._time_label.config(text=f"{mins:02d}:{secs:02d}")

        self._progress_job = self.after(200, self._tick_progress)


# ------------------------------------------------------------------
# Entry-point
# ------------------------------------------------------------------

def main() -> None:
    app = MusicGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
