import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from . import database
from .clipboard import ClipboardMonitor
from .version import VERSION


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


COLORS = {
    "bg": "#1a1a2e",
    "surface": "#16213e",
    "card": "#0f3460",
    "pinned": "#1a3a5c",
    "accent": "#e94560",
    "text": "#e8e8e8",
    "text_muted": "#8892a4",
    "hover": "#1a4a7a",
    "border": "#2a2a4e",
}


class ClipCacheUI:
    def __init__(self, monitor: ClipboardMonitor):
        self.monitor = monitor
        self._loading = False
        self._card_refs = []  # keep references to card widgets for keyboard nav
        self._card_pinned = []  # parallel array: whether each card is pinned (for hover restore)
        self._selected_index = -1
        # bit of a hack: store item contents so keyboard nav can copy
        self._item_contents = []

        self.window = ctk.CTk()
        self.window.title("ClipCache")
        self.window.geometry("520x640")
        self.window.minsize(380, 420)

        # Position near the center of the screen
        self.window.after(50, self._center_window)

        # Make window stay on top, but allow hiding
        self.window.attributes("-topmost", True)
        self.window.configure(fg_color=COLORS["bg"])

        # Bind Escape to hide
        self.window.bind("<Escape>", lambda e: self.hide())

        self._build_widgets()
        self._load_items()

    def _center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 3
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def _build_widgets(self):
        # Header
        header = ctk.CTkFrame(self.window, fg_color=COLORS["bg"], height=50)
        header.pack(fill="x", padx=16, pady=(12, 0))
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="ClipCache",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text"],
        )
        title.pack(side="left")

        self._count_label = ctk.CTkLabel(
            header,
            text="0 items",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        )
        self._count_label.pack(side="right", padx=(0, 4))

        import_btn = ctk.CTkButton(
            header,
            text="Import",
            width=56,
            height=28,
            fg_color=COLORS["surface"],
            hover_color=COLORS["hover"],
            font=ctk.CTkFont(size=11),
            command=self._import_pins,
        )
        import_btn.pack(side="right", padx=(0, 4))

        export_btn = ctk.CTkButton(
            header,
            text="Export",
            width=56,
            height=28,
            fg_color=COLORS["surface"],
            hover_color=COLORS["hover"],
            font=ctk.CTkFont(size=11),
            command=self._export_pins,
        )
        export_btn.pack(side="right", padx=(0, 4))

        clear_btn = ctk.CTkButton(
            header,
            text="Clear",
            width=56,
            height=28,
            fg_color=COLORS["accent"],
            hover_color="#c73a50",
            font=ctk.CTkFont(size=11),
            command=self._confirm_clear,
        )
        clear_btn.pack(side="right", padx=(0, 4))

        # Search bar
        search_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        search_frame.pack(fill="x", padx=16, pady=(10, 6))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._on_search())
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search clipboard history...",
            textvariable=self.search_var,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=13),
            height=36,
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<Down>", lambda e: self._focus_list())

        # List frame with scrollbar
        list_container = ctk.CTkFrame(self.window, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=16, pady=(4, 12))

        self.list_canvas = tk.Canvas(
            list_container,
            bg=COLORS["bg"],
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.list_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            list_container, orient="vertical", command=self.list_canvas.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.list_canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = ctk.CTkFrame(
            self.list_canvas, fg_color="transparent"
        )
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")),
        )
        self.list_canvas_window = self.list_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw", width=self.list_canvas.winfo_reqwidth()
        )
        self.list_canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel scrolling
        self.list_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)

        # Keyboard nav
        self.list_canvas.bind("<Button-1>", lambda e: self.list_canvas.focus_set())
        self.window.bind("<Up>", lambda e: self._nav_up())
        self.window.bind("<Down>", lambda e: self._nav_down())
        self.window.bind("<Return>", lambda e: self._nav_copy())
        self.window.bind("<Control-p>", lambda e: self._nav_up())  # ctrl-p/down for vim users
        self.window.bind("<Control-n>", lambda e: self._nav_down())

        # Status bar at the bottom (TODO: might move this to a better spot)
        status_frame = ctk.CTkFrame(self.window, fg_color=COLORS["surface"], height=28)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"],
        )
        self.status_label.pack(side="left", padx=(12, 0))

        self.version_label = ctk.CTkLabel(
            status_frame,
            text=f"v{VERSION}",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_muted"],
        )
        self.version_label.pack(side="right", padx=(0, 12))

    def _on_canvas_configure(self, event):
        self.list_canvas.itemconfig(self.list_canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.list_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _focus_list(self):
        self.list_canvas.focus_set()

    def _on_search(self):
        self._load_items()

    def _load_items(self):
        query = self.search_var.get().strip()
        items = database.search_items(query)
        self._render_items(items)

    def _render_items(self, items):
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self._card_refs = []
        self._card_pinned = []
        self._item_contents = []
        self._selected_index = -1

        if not items:
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="Nothing copied yet.\nCopy some text and it'll appear here.",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_muted"],
                justify="center",
            )
            empty_label.pack(expand=True, pady=60)
            self._count_label.configure(text="0 items")
            self.status_label.configure(text="Ready | 0 items")
            return

        pinned_count = sum(1 for i in items if i["pinned"])
        self._count_label.configure(
            text=f"{len(items)} items" + (f" ({pinned_count} pinned)" if pinned_count else "")
        )

        # Pinned section
        pinned_items = [i for i in items if i["pinned"]]
        unpinned_items = [i for i in items if not i["pinned"]]

        if pinned_items:
            self._render_section_header("PINNED")
            for item in pinned_items:
                self._render_item_card(item, pinned=True)

            if unpinned_items:
                separator = ctk.CTkFrame(
                    self.scrollable_frame,
                    height=1,
                    fg_color=COLORS["border"],
                )
                separator.pack(fill="x", padx=8, pady=2)

                self._render_section_header("HISTORY")

        for item in unpinned_items:
            self._render_item_card(item, pinned=False)

        if self._card_refs:
            self._selected_index = 0
            self._highlight_selected()

    def _highlight_selected(self):
        """hacky highlight for keyboard nav"""
        for i, card in enumerate(self._card_refs):
            if i == self._selected_index:
                card.configure(fg_color=COLORS["hover"], border_width=1, border_color=COLORS["accent"])
            else:
                card.configure(border_width=0)
                original = COLORS["pinned"] if self._card_pinned[i] else COLORS["card"]
                card.configure(fg_color=original)
        total = len(self._item_contents)
        self.status_label.configure(text=f"{self._selected_index + 1} / {total} | Enter to copy")

    def _nav_down(self):
        if not self._card_refs:
            return
        self._selected_index = (self._selected_index + 1) % len(self._card_refs)
        self._highlight_selected()
        self._scroll_to_selected()

    def _nav_up(self):
        if not self._card_refs:
            return
        self._selected_index = (self._selected_index - 1) % len(self._card_refs)
        self._highlight_selected()
        self._scroll_to_selected()

    def _scroll_to_selected(self):
        """scroll the canvas so the selected card is visible"""
        # TODO: figure out why this doesn't always work
        card = self._card_refs[self._selected_index]
        y = card.winfo_y()
        h = card.winfo_height()
        canvas_h = self.list_canvas.winfo_height()
        bbox = self.list_canvas.bbox("all")
        if bbox and (y < 0 or y + h > canvas_h):
            self.list_canvas.yview_moveto(max(0, y / bbox[3] - 0.1))

    def _nav_copy(self):
        if 0 <= self._selected_index < len(self._item_contents):
            self._copy_item(self._item_contents[self._selected_index])

    def _render_section_header(self, text: str):
        header = ctk.CTkLabel(
            self.scrollable_frame,
            text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        )
        header.pack(anchor="w", padx=12, pady=(8, 2))

    def _render_item_card(self, item: dict, pinned: bool):
        idx = len(self._card_refs)
        content = item["content"]
        self._item_contents.append(content)

        card = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=COLORS["pinned"] if pinned else COLORS["card"],
            corner_radius=8,
            height=50,
            border_width=0,
        )
        card.pack(fill="x", padx=4, pady=2)
        card.pack_propagate(False)
        self._card_refs.append(card)
        self._card_pinned.append(pinned)

        preview = content[:120].replace("\n", " ↵ ") if content else "(empty)"
        if len(content) > 120:
            preview += "..."

        # Pin button
        pin_btn = ctk.CTkButton(
            card,
            text="📌" if pinned else "📍",
            width=30,
            height=26,
            fg_color="transparent",
            hover_color=COLORS["hover"],
            font=ctk.CTkFont(size=13),
            command=lambda iid=item["id"]: self._toggle_pin(iid),
        )
        pin_btn.pack(side="left", padx=(4, 0))

        # Content label
        content_label = ctk.CTkLabel(
            card,
            text=preview,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
            anchor="w",
            justify="left",
        )
        content_label.pack(side="left", fill="x", expand=True, padx=(4, 4))

        # click on the card itself selects for keyboard nav
        card.bind("<Button-1>", lambda e, c=content, i=idx: self._on_card_click(i, c))
        card.bind("<Enter>", lambda e: card.configure(fg_color=COLORS["hover"]))
        card.bind("<Leave>", lambda e: self._on_card_leave(card, idx))

        # Copy button
        copy_btn = ctk.CTkButton(
            card,
            text="Copy",
            width=52,
            height=26,
            fg_color=COLORS["accent"],
            hover_color="#c73a50",
            font=ctk.CTkFont(size=11),
            command=lambda c=content: self._copy_item(c),
        )
        copy_btn.pack(side="right", padx=(0, 6))

        # Delete button (only for unpinned)
        if not pinned:
            del_btn = ctk.CTkButton(
                card,
                text="✕",
                width=26,
                height=26,
                fg_color="transparent",
                hover_color="#5a1a1a",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_muted"],
                command=lambda iid=item["id"]: self._delete_item(iid),
            )
            del_btn.pack(side="right", padx=(0, 2))

    def _on_card_click(self, idx: int, content: str):
        self._selected_index = idx
        self._highlight_selected()
        self._copy_item(content)

    def _on_card_leave(self, card, idx: int):
        if idx == self._selected_index:
            card.configure(fg_color=COLORS["hover"])
        else:
            original = COLORS["pinned"] if self._card_pinned[idx] else COLORS["card"]
            card.configure(fg_color=original)

    def _toggle_pin(self, item_id: int):
        database.toggle_pin(item_id)
        self._load_items()

    def _delete_item(self, item_id: int):
        database.delete_item(item_id)
        self._load_items()

    def _copy_item(self, content: str):
        self.monitor.copy_to_clipboard(content)
        self.status_label.configure(text=f"Copied! ({len(content)} chars)")
        self.hide()

    def _export_pins(self):
        """Export pinned items as JSON."""
        items = database.export_pinned()
        pinned = [i for i in items if i["pinned"]]
        if not pinned:
            messagebox.showinfo("Export", "No pinned items to export.")
            return
        fp = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="clipcache-pins.json",
        )
        if not fp:
            return
        try:
            data = [{"content": i["content"], "created_at": i["created_at"]} for i in pinned]
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.status_label.configure(text=f"Exported {len(data)} pins")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _import_pins(self):
        """Import pinned items from JSON."""
        fp = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
        )
        if not fp:
            return
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            imported = database.import_pinned(data)
            self.status_label.configure(text=f"Imported {imported} pins")
            self._load_items()
        except Exception as e:
            messagebox.showerror("Import failed", str(e))



    def _confirm_clear(self):
        """Show a simple confirmation dialog."""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Clear history")
        dialog.geometry("320x140")
        dialog.configure(fg_color=COLORS["bg"])
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        # Center on parent
        dialog.update_idletasks()
        dw = dialog.winfo_width()
        dh = dialog.winfo_height()
        pw = self.window.winfo_width()
        ph = self.window.winfo_height()
        px = self.window.winfo_x()
        py = self.window.winfo_y()
        dialog.geometry(f"{dw}x{dh}+{px + (pw-dw)//2}+{py + (ph-dh)//2}")

        label = ctk.CTkLabel(
            dialog,
            text="Clear all unpinned clipboard history?\nPinned items will be kept.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"],
        )
        label.pack(pady=(20, 12))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=90,
            fg_color=COLORS["surface"],
            hover_color=COLORS["hover"],
            command=dialog.destroy,
        )
        cancel_btn.pack(side="left", padx=(0, 8))

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            width=90,
            fg_color=COLORS["accent"],
            hover_color="#c73a50",
            command=lambda: self._do_clear(dialog),
        )
        confirm_btn.pack(side="left")

    def _do_clear(self, dialog):
        database.clear_history()
        dialog.destroy()
        self._load_items()

    def refresh(self):
        """Called by the monitor when a new clipboard item is captured."""
        self._load_items()

    def show(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.search_entry.focus()
        self._load_items()

    def hide(self):
        self.window.withdraw()

    def run(self):
        self.hide()  # Start hidden
        self.window.mainloop()

    def close(self):
        self.window.quit()
        self.window.destroy()
