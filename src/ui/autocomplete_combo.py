import tkinter as tk
import customtkinter as ctk
from typing import Callable, List, Optional


class AutocompleteCombo(ctk.CTkFrame):
    """Campo de texto con sugerencias: se puede escribir parte del valor o elegirlo de la lista."""

    MAX_VISIBLE_ROWS = 10
    NAV_KEYS = {"Up", "Down", "Return", "KP_Enter", "Escape", "Tab"}

    def __init__(
        self,
        master,
        variable: ctk.StringVar,
        values: Optional[List[str]] = None,
        command: Optional[Callable[[str], None]] = None,
        width: int = 220,
        height: int = 32,
        **kwargs,
    ):
        super().__init__(master, height=1, fg_color="transparent", **kwargs)
        self._var = variable
        self._values: List[str] = list(values or [])
        self._command = command
        self._popup: Optional[tk.Toplevel] = None
        self._listbox: Optional[tk.Listbox] = None
        self._hide_job = None

        self.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(self, textvariable=variable, width=width - height, height=height)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.button = ctk.CTkButton(
            self,
            text="▼",
            width=height,
            height=height,
            command=self._toggle_all,
        )
        self.button.grid(row=0, column=1, padx=(2, 0))

        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<Down>", self._on_down)
        self.entry.bind("<Up>", self._on_up)
        self.entry.bind("<Return>", self._on_return)
        self.entry.bind("<KP_Enter>", self._on_return)
        self.entry.bind("<Escape>", lambda e: self._hide_popup())
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<FocusIn>", self._on_focus_in)

    def set_values(self, values: List[str]):
        self._values = list(values)

    # --- comportamiento del campo ---

    def _on_focus_in(self, _event=None):
        if self._var.get().strip().lower() == "todos":
            self.entry.select_range(0, "end")

    def _on_key_release(self, event):
        if event.keysym in self.NAV_KEYS:
            return
        text = self._var.get().strip().lower()
        if not text:
            self._hide_popup()
            return
        matches = [v for v in self._values if text in v.lower()]
        if matches:
            self._show_popup(matches)
        else:
            self._hide_popup()

    def _toggle_all(self):
        if self._popup_visible():
            self._hide_popup()
        else:
            self._show_popup(self._values)
            self.entry.focus_set()

    def _on_down(self, _event=None):
        if not self._popup_visible():
            text = self._var.get().strip().lower()
            matches = [v for v in self._values if not text or text == "todos" or text in v.lower()]
            self._show_popup(matches)
        self._move_selection(1)
        return "break"

    def _on_up(self, _event=None):
        if self._popup_visible():
            self._move_selection(-1)
        return "break"

    def _on_return(self, _event=None):
        if self._popup_visible() and self._listbox.curselection():
            self._choose(self._listbox.get(self._listbox.curselection()[0]))
        else:
            self._hide_popup()
            if self._command:
                self._command(self._var.get())
        return "break"

    def _on_focus_out(self, _event=None):
        # Diferido: un clic en la lista quita el foco del campo antes de registrar la selección
        self._hide_job = self.after(150, self._hide_unless_pointer_in_popup)

    def _hide_unless_pointer_in_popup(self):
        self._hide_job = None
        if not self._popup_visible():
            return
        widget = self.winfo_containing(*self.winfo_pointerxy())
        if widget is not None and str(widget).startswith(str(self._popup)):
            return
        self._hide_popup()

    # --- lista desplegable ---

    def _popup_visible(self) -> bool:
        return self._popup is not None and self._popup.winfo_viewable()

    def _ensure_popup(self):
        if self._popup is not None:
            return
        self._popup = tk.Toplevel(self)
        self._popup.overrideredirect(True)
        self._popup.attributes("-topmost", True)

        dark = ctk.get_appearance_mode() == "Dark"
        # tk.Listbox no aplica la escala de CustomTkinter: tamaño en píxeles ya escalado
        scaling = ctk.ScalingTracker.get_widget_scaling(self)
        font_px = -round(13 * scaling)
        frame = tk.Frame(self._popup, bg="#3d3d3d" if dark else "#b0b0b0", bd=1)
        frame.pack(fill="both", expand=True)

        self._listbox = tk.Listbox(
            frame,
            activestyle="none",
            exportselection=False,
            font=("Segoe UI", font_px),
            bg="#2b2b2b" if dark else "white",
            fg="white" if dark else "black",
            selectbackground="#1f6aa5",
            selectforeground="white",
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=scrollbar.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._listbox.bind("<ButtonRelease-1>", self._on_list_click)
        self._listbox.bind("<Motion>", self._on_list_hover)

        window = self.winfo_toplevel()
        # <Configure> de la ventana también llega por cada widget hijo: solo cerrar si se movió la ventana
        window.bind(
            "<Configure>",
            lambda e: self._hide_popup() if e.widget is window else None,
            add="+",
        )

    def _show_popup(self, items: List[str]):
        if self._hide_job:
            self.after_cancel(self._hide_job)
            self._hide_job = None
        self._ensure_popup()

        self._listbox.delete(0, "end")
        for item in items:
            self._listbox.insert("end", item)
        self._listbox.configure(height=min(len(items), self.MAX_VISIBLE_ROWS))

        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2
        width = max(self.winfo_width(), 260)
        self._popup.geometry(f"{width}x{self._listbox.winfo_reqheight() + 2}+{x}+{y}")
        self._popup.deiconify()
        self._popup.lift()

    def _hide_popup(self):
        self._hide_job = None
        if self._popup is not None:
            self._popup.withdraw()

    def _move_selection(self, delta: int):
        size = self._listbox.size()
        if not size:
            return
        current = self._listbox.curselection()
        index = (current[0] + delta) if current else (0 if delta > 0 else size - 1)
        index = max(0, min(size - 1, index))
        self._listbox.selection_clear(0, "end")
        self._listbox.selection_set(index)
        self._listbox.see(index)

    def _on_list_hover(self, event):
        index = self._listbox.nearest(event.y)
        self._listbox.selection_clear(0, "end")
        self._listbox.selection_set(index)

    def _on_list_click(self, event):
        if not self._listbox.size():
            return
        index = self._listbox.nearest(event.y)
        self._choose(self._listbox.get(index))

    def _choose(self, value: str):
        self._var.set(value)
        self._hide_popup()
        self.entry.icursor("end")
        self.entry.focus_set()
        if self._command:
            self._command(value)
