"""
Interface gráfica do Gerador de Música por Texto.
Arquivo: src/gui.py
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from music_generator.application.playback_service import PlaybackService
from music_generator.application.sequence_generator import SequenceGenerator
from music_generator.domain.settings import PlaybackSettings
from music_generator.infrastructure.audio.fluidsynth_player import FluidSynthPlayer


# Mapeamento de nome legível → índice MIDI General MIDI
INSTRUMENTS: dict[str, int] = {
    # Pianos (0–7)
    "Piano Acústico (Grand)": 0,
    "Piano Acústico (Bright)": 1,
    "Piano Elétrico Grande": 2,
    "Honky-Tonk Piano": 3,
    "Piano Elétrico 1 (Rhodes)": 4,
    "Piano Elétrico 2 (Chorus)": 5,
    "Cravo": 6,
    "Clavicórdio": 7,
    # Instrumentos de Teclas Cromáticas (8–15)
    "Celesta": 8,
    "Glockenspiel": 9,
    "Caixinha de Música": 10,
    "Vibrafone": 11,
    "Marimba": 12,
    "Xilofone": 13,
    "Sinos Tubulares": 14,
    "Dulcimer": 15,
    # Órgãos (16–23)
    "Órgão Hammond": 16,
    "Órgão Percussivo": 17,
    "Órgão de Rock": 18,
    "Órgão de Igreja": 19,
    "Órgão de Reed": 20,
    "Acordeão": 21,
    "Harmônica": 22,
    "Bandoneón": 23,
    # Guitarras (24–31)
    "Violão (Nylon)": 24,
    "Violão (Aço)": 25,
    "Guitarra Jazz": 26,
    "Guitarra Limpa": 27,
    "Guitarra Muted": 28,
    "Guitarra Overdrive": 29,
    "Guitarra Distorção": 30,
    "Guitarra Harmonics": 31,
    # Baixos (32–39)
    "Contrabaixo Acústico": 32,
    "Baixo Elétrico (Dedos)": 33,
    "Baixo Elétrico (Palheta)": 34,
    "Baixo Fretless": 35,
    "Baixo Slap 1": 36,
    "Baixo Slap 2": 37,
    "Baixo Synth 1": 38,
    "Baixo Synth 2": 39,
    # Cordas (40–47)
    "Violino": 40,
    "Viola": 41,
    "Violoncelo": 42,
    "Contrabaixo": 43,
    "Cordas Tremolo": 44,
    "Cordas Pizzicato": 45,
    "Harpa Orquestral": 46,
    "Tímpano": 47,
    # Ensemble de Cordas (48–55)
    "Ensemble de Cordas 1": 48,
    "Ensemble de Cordas 2": 49,
    "Cordas Synth 1": 50,
    "Cordas Synth 2": 51,
    "Coro Ahh": 52,
    "Voz Ooh": 53,
    "Voz Synth": 54,
    "Hit Orquestral": 55,
    # Metais (56–63)
    "Trompete": 56,
    "Trombone": 57,
    "Tuba": 58,
    "Trompete Muted": 59,
    "Trompa Francesa": 60,
    "Seção de Metais": 61,
    "Trompete Synth": 62,
    "Trombone Synth": 63,
    # Reed (64–71)
    "Soprano Sax": 64,
    "Alto Sax": 65,
    "Tenor Sax": 66,
    "Barítono Sax": 67,
    "Oboé": 68,
    "Corne Inglês": 69,
    "Fagote": 70,
    "Clarinete": 71,
    # Palhetas / Flautas (72–79)
    "Piccolo": 72,
    "Flauta": 73,
    "Recorder": 74,
    "Flauta Pan": 75,
    "Garrafa Soprada": 76,
    "Shakuhachi": 77,
    "Assobio": 78,
    "Ocarina": 79,
    # Synth Lead (80–87)
    "Lead Quadrado": 80,
    "Lead Serrilhado": 81,
    "Lead Calliope": 82,
    "Lead Chiff": 83,
    "Lead Charang": 84,
    "Lead Voz": 85,
    "Lead Fifths": 86,
    "Lead Bass + Lead": 87,
    # Synth Pad (88–95)
    "Pad New Age": 88,
    "Pad Warm": 89,
    "Pad Polysynth": 90,
    "Pad Choir": 91,
    "Pad Bowed": 92,
    "Pad Metallic": 93,
    "Pad Halo": 94,
    "Pad Sweep": 95,
    # Synth FX (96–103)
    "FX Rain": 96,
    "FX Soundtrack": 97,
    "FX Crystal": 98,
    "FX Atmosphere": 99,
    "FX Brightness": 100,
    "FX Goblins": 101,
    "FX Echoes": 102,
    "FX Sci-Fi": 103,
    # Étnico (104–111)
    "Sitar": 104,
    "Banjo": 105,
    "Shamisen": 106,
    "Koto": 107,
    "Kalimba": 108,
    "Gaita de Foles": 109,
    "Fiddle": 110,
    "Shanai": 111,
    # Percussivo (112–119)
    "Sino Tinkle": 112,
    "Agogô": 113,
    "Steel Drum": 114,
    "Woodblock": 115,
    "Taiko Drum": 116,
    "Tom Melódico": 117,
    "Bombo Synth": 118,
    "Prato Synth": 119,
    # Efeitos Sonoros (120–127)
    "Guitarra Fret Noise": 120,
    "Breath Noise": 121,
    "Litoral": 122,
    "Pássaros": 123,
    "Telefone": 124,
    "Helicóptero": 125,
    "Aplausos": 126,
    "Tiro de Pistola": 127,
}

DEFAULT_BPM = 180
DEFAULT_OCTAVE = 4
DEFAULT_VOLUME = 64  # meio do slider (0–127)


class MusicGeneratorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("INF01120 - Gerador de Música por Texto")
        self.resizable(False, False)
        self.configure(bg="#d0d0d0")

        # Estado de playback
        self._playback_service: PlaybackService | None = None
        self._is_paused = False
        self._composition = None
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
        self._instrument_var = tk.StringVar(value="")
        instrument_names = list(INSTRUMENTS.keys())
        self._instrument_combo = ttk.Combobox(
            config_frame,
            textvariable=self._instrument_var,
            values=instrument_names,
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
    # Handlers
    # ------------------------------------------------------------------

    def _on_import_file(self) -> None:
        """Abre uma janela para selecionar um arquivo .txt e joga o conteúdo na caixa de texto."""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo de texto",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                
                # Limpa a caixa de texto atual e insere o conteúdo novo
                self._text_box.delete("1.0", tk.END)
                self._text_box.insert(tk.END, content)
            except Exception as exc:
                messagebox.showerror("Erro de leitura", f"Não foi possível ler o arquivo:\n{exc}")
    
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
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self._status_var.set("Texto salvo com sucesso!")
            except Exception as exc:
                messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o arquivo:\n{exc}")
                
    def _on_play(self) -> None:
        """Inicia a reprodução a partir do texto e configurações atuais."""
        if self._playback_service and self._playback_service.is_playing():
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
            composition = SequenceGenerator().generate(text, settings)
        except Exception as exc:
            messagebox.showerror("Erro ao gerar composição", str(exc))
            return

        try:
            player = FluidSynthPlayer("C:\soundfont\FluidR3_GM.sf2")  # Substitua pelo caminho correto do seu SoundFont
        except Exception as exc:
            messagebox.showerror("Erro de áudio", str(exc))
            return

        self._composition = composition
        self._playback_service = PlaybackService(player)
        self._is_paused = False

        self._playback_service.start(composition)

        self._play_btn.config(state=tk.DISABLED)
        self._pause_btn.config(state=tk.NORMAL)

        # Calcula duração total estimada
        seconds_per_beat = 60.0 / settings.bpm
        total_beats = sum(
            getattr(ev, "duration_beats", 0) for ev in composition.events
        )
        self._total_seconds = total_beats * seconds_per_beat
        self._elapsed_seconds = 0.0
        self._progress["value"] = 0

        self._status_var.set("Reproduzindo...")
        self._tick_progress()

    def _on_pause(self) -> None:
        """Alterna entre pause e retomada (stop/start simples, pois não há seek)."""
        if not self._playback_service:
            return

        if self._playback_service.is_playing():
            self._playback_service.stop()
            self._is_paused = True
            self._pause_btn.config(text="▶▶")
            self._status_var.set("Pausado")
            if self._progress_job:
                self.after_cancel(self._progress_job)
        else:
            # Retoma do início (sem seek disponível na engine)
            self._is_paused = False
            self._pause_btn.config(text="⏸")
            if self._composition:
                self._playback_service.start(self._composition)
                self._status_var.set("Reproduzindo...")
                self._elapsed_seconds = 0.0
                self._tick_progress()

    def _on_clear(self) -> None:
        self._text_box.delete("1.0", tk.END)

    def _on_close(self) -> None:
        if self._playback_service:
            self._playback_service.close()
        self.destroy()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_settings(self) -> PlaybackSettings:
        return PlaybackSettings(
            bpm=self._bpm_var.get(),
            initial_volume=self._volume_var.get(),
            default_octave=self._octave_var.get(),
            initial_instrument=INSTRUMENTS[self._instrument_var.get()],
        )

    def _tick_progress(self) -> None:
        """Atualiza barra de progresso e tempo a cada 200 ms."""
        if not self._playback_service or not self._playback_service.is_playing():
            self._play_btn.config(state=tk.NORMAL)
            self._pause_btn.config(state=tk.DISABLED, text="⏸")
            self._status_var.set("Pronto")
            self._progress["value"] = 0
            self._time_label.config(text="00:00")
            return

        self._elapsed_seconds += 0.2
        if self._total_seconds > 0:
            pct = min(self._elapsed_seconds / self._total_seconds * 100, 100)
        else:
            pct = 0
        self._progress["value"] = pct

        mins = int(self._elapsed_seconds) // 60
        secs = int(self._elapsed_seconds) % 60
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