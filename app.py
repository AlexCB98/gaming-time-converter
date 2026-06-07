import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Any

from calculators import CalculationResult, format_number, parse_number
from catalog import TOOLS, TOOLS_BY_KEY, Field, Mode
from i18n import LANGUAGES, translate
from theme import COLORS, FONT_MONO


class LifestyleConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("1180x760")
        self.minsize(1060, 700)
        self.configure(bg=COLORS["background"])

        self.language = "en"
        self.language_name = tk.StringVar(value=LANGUAGES["en"])
        self.active_tool = TOOLS[0]
        self.active_mode = self.active_tool.modes[0]
        self.input_vars: dict[str, tk.StringVar] = {}
        self.tool_buttons: dict[str, tk.Button] = {}
        self.mode_buttons: dict[str, tk.Button] = {}
        self.localized_widgets: list[tuple[tk.Widget, str]] = []
        self.last_result: CalculationResult | None = None
        self.last_summary = ""

        self.result_value = tk.StringVar(value="0")
        self.result_unit = tk.StringVar()
        self.detail_value = tk.StringVar()
        self.status_value = tk.StringVar()
        self.stat_labels = [tk.StringVar() for _ in range(2)]
        self.stat_values = [tk.StringVar(value="0") for _ in range(2)]

        self._configure_styles()
        self._build_layout()
        self._bind_shortcuts()
        self.select_tool(self.active_tool.key)
        self._apply_language()

    def tr(self, key: str, **values: Any) -> str:
        return translate(self.language, key, **values)

    def _localize_widget(self, widget: tk.Widget, key: str) -> tk.Widget:
        self.localized_widgets.append((widget, key))
        widget.config(text=self.tr(key))
        return widget

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "History.Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 9),
        )
        style.map(
            "History.Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", COLORS["white"])],
        )
        style.configure(
            "History.Treeview.Heading",
            background=COLORS["surface_alt"],
            foreground=COLORS["muted"],
            relief="flat",
            font=("Segoe UI Semibold", 8),
            padding=(8, 7),
        )
        style.configure(
            "Language.TCombobox",
            fieldbackground=COLORS["surface_alt"],
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["accent"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            padding=6,
        )
        style.map(
            "Language.TCombobox",
            fieldbackground=[("readonly", COLORS["surface_alt"])],
            foreground=[("readonly", COLORS["text"])],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["surface_alt"],
            troughcolor=COLORS["surface"],
            bordercolor=COLORS["surface"],
            arrowcolor=COLORS["muted"],
        )

    def _build_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._build_sidebar()

        self.content = tk.Frame(self, bg=COLORS["background"])
        self.content.grid(row=0, column=1, sticky="nsew", padx=24, pady=(22, 15))
        self.content.columnconfigure((0, 1), weight=1)
        self.content.rowconfigure(2, weight=1)

        self._build_header()
        self._build_converter_card()
        self._build_result_card()
        self._build_history_card()
        self._build_status_bar()

    def _build_sidebar(self) -> None:
        sidebar = tk.Frame(
            self,
            bg=COLORS["sidebar"],
            width=215,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = tk.Frame(sidebar, bg=COLORS["sidebar"])
        brand.pack(fill="x", padx=18, pady=(22, 18))
        tk.Label(
            brand,
            text="EC",
            bg=COLORS["primary"],
            fg=COLORS["white"],
            width=3,
            height=2,
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left")
        brand_text = tk.Frame(brand, bg=COLORS["sidebar"])
        brand_text.pack(side="left", padx=10)
        self._localize_widget(
            tk.Label(
                brand_text,
                bg=COLORS["sidebar"],
                fg=COLORS["text"],
                font=("Segoe UI", 11, "bold"),
            ),
            "brand_top",
        ).pack(anchor="w")
        self._localize_widget(
            tk.Label(
                brand_text,
                bg=COLORS["sidebar"],
                fg=COLORS["accent"],
                font=("Segoe UI Semibold", 8),
            ),
            "brand_bottom",
        ).pack(anchor="w")

        self._localize_widget(
            tk.Label(
                sidebar,
                bg=COLORS["sidebar"],
                fg=COLORS["muted"],
                font=("Segoe UI Semibold", 8),
            ),
            "language",
        ).pack(anchor="w", padx=20)
        language_box = ttk.Combobox(
            sidebar,
            textvariable=self.language_name,
            values=tuple(LANGUAGES.values()),
            state="readonly",
            style="Language.TCombobox",
            font=("Segoe UI", 9),
        )
        language_box.pack(fill="x", padx=18, pady=(6, 18))
        language_box.bind("<<ComboboxSelected>>", self._change_language)

        self._localize_widget(
            tk.Label(
                sidebar,
                bg=COLORS["sidebar"],
                fg=COLORS["muted"],
                font=("Segoe UI Semibold", 8),
            ),
            "tools",
        ).pack(anchor="w", padx=20, pady=(0, 7))

        for tool in TOOLS:
            button = tk.Button(
                sidebar,
                command=lambda key=tool.key: self.select_tool(key),
                anchor="w",
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI Semibold", 9),
                padx=12,
                pady=10,
            )
            button.pack(fill="x", padx=10, pady=1)
            self.tool_buttons[tool.key] = button

        info = tk.Frame(sidebar, bg=COLORS["surface"], padx=14, pady=12)
        info.pack(side="bottom", fill="x", padx=12, pady=16)
        self._localize_widget(
            tk.Label(
                info,
                bg=COLORS["surface"],
                fg=COLORS["accent"],
                font=("Segoe UI Semibold", 8),
            ),
            "tools_count",
        ).pack(anchor="w")
        self._localize_widget(
            tk.Label(
                info,
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                justify="left",
                wraplength=175,
                font=("Segoe UI", 8),
            ),
            "sidebar_info",
        ).pack(anchor="w", pady=(4, 0))

    def _build_header(self) -> None:
        header = tk.Frame(self.content, bg=COLORS["background"])
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        title_group = tk.Frame(header, bg=COLORS["background"])
        title_group.grid(row=0, column=0, sticky="w")
        self.header_badge = tk.Label(
            title_group,
            bg=COLORS["primary"],
            fg=COLORS["white"],
            font=("Segoe UI Semibold", 8),
            padx=10,
            pady=3,
        )
        self.header_badge.pack(anchor="w")
        self.header_title = tk.Label(
            title_group,
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Segoe UI", 25, "bold"),
        )
        self.header_title.pack(anchor="w", pady=(4, 0))
        self.header_subtitle = tk.Label(
            title_group,
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        )
        self.header_subtitle.pack(anchor="w")
        self.header_fact = tk.Label(
            header,
            bg=COLORS["surface_alt"],
            fg=COLORS["accent"],
            font=FONT_MONO,
            padx=15,
            pady=10,
        )
        self.header_fact.grid(row=0, column=1, sticky="e")

    def _card(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=20,
            pady=17,
        )

    def _section_title(self, parent: tk.Widget, number: str, key: str) -> None:
        row = tk.Frame(parent, bg=COLORS["surface"])
        row.pack(fill="x", pady=(0, 13))
        tk.Label(
            row,
            text=number,
            bg=COLORS["primary"],
            fg=COLORS["white"],
            width=3,
            pady=3,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left")
        self._localize_widget(
            tk.Label(
                row,
                bg=COLORS["surface"],
                fg=COLORS["text"],
                font=("Segoe UI Semibold", 11),
            ),
            key,
        ).pack(side="left", padx=9)

    def _build_converter_card(self) -> None:
        card = self._card(self.content)
        card.grid(row=1, column=0, sticky="nsew", padx=(0, 7))
        self._section_title(card, "01", "configure")
        self._localize_widget(
            tk.Label(
                card,
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                font=("Segoe UI Semibold", 7),
            ),
            "calculation_mode",
        ).pack(anchor="w")
        self.mode_frame = tk.Frame(card, bg=COLORS["surface_alt"], padx=4, pady=4)
        self.mode_frame.pack(fill="x", pady=(6, 11))
        self.fields_frame = tk.Frame(card, bg=COLORS["surface"])
        self.fields_frame.pack(fill="both", expand=True)

        actions = tk.Frame(card, bg=COLORS["surface"])
        actions.pack(fill="x", pady=(3, 0))
        actions.columnconfigure(0, weight=1)
        self.calculate_button = self._localize_widget(
            tk.Button(
                actions,
                command=self.calculate,
                bg=COLORS["primary"],
                activebackground=COLORS["primary_hover"],
                fg=COLORS["white"],
                activeforeground=COLORS["white"],
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI Semibold", 9),
                pady=10,
            ),
            "calculate",
        )
        self.calculate_button.grid(row=0, column=0, sticky="ew", padx=(0, 7))
        self._localize_widget(
            tk.Button(
                actions,
                command=self.reset,
                bg=COLORS["surface_alt"],
                activebackground=COLORS["border"],
                fg=COLORS["muted"],
                activeforeground=COLORS["text"],
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI Semibold", 8),
                padx=13,
                pady=11,
            ),
            "reset",
        ).grid(row=0, column=1)

    def _build_result_card(self) -> None:
        card = self._card(self.content)
        card.grid(row=1, column=1, sticky="nsew", padx=(7, 0))
        self._section_title(card, "02", "your_result")
        tk.Label(
            card,
            textvariable=self.result_value,
            bg=COLORS["surface"],
            fg=COLORS["accent"],
            font=("Segoe UI", 30, "bold"),
        ).pack(anchor="w")
        tk.Label(
            card,
            textvariable=self.result_unit,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
        ).pack(anchor="w")
        tk.Frame(card, bg=COLORS["border"], height=1).pack(fill="x", pady=12)
        self._localize_widget(
            tk.Label(
                card,
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                font=("Segoe UI Semibold", 7),
            ),
            "details",
        ).pack(anchor="w")
        tk.Label(
            card,
            textvariable=self.detail_value,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            justify="left",
            wraplength=400,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 10))

        stats = tk.Frame(card, bg=COLORS["surface_alt"], padx=10, pady=9)
        stats.pack(fill="x")
        stats.columnconfigure((0, 1), weight=1)
        for index in range(2):
            block = tk.Frame(stats, bg=COLORS["surface_alt"])
            block.grid(row=0, column=index, sticky="ew")
            tk.Label(
                block,
                textvariable=self.stat_labels[index],
                bg=COLORS["surface_alt"],
                fg=COLORS["muted"],
                font=("Segoe UI Semibold", 7),
            ).pack()
            tk.Label(
                block,
                textvariable=self.stat_values[index],
                bg=COLORS["surface_alt"],
                fg=COLORS["text"],
                font=("Segoe UI", 12, "bold"),
            ).pack(pady=(2, 0))
        self._localize_widget(
            tk.Button(
                card,
                command=self.copy_result,
                bg=COLORS["surface"],
                activebackground=COLORS["surface_alt"],
                fg=COLORS["muted"],
                activeforeground=COLORS["text"],
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI", 8, "underline"),
            ),
            "copy_result",
        ).pack(anchor="e", pady=(8, 0))

    def _build_history_card(self) -> None:
        card = self._card(self.content)
        card.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(13, 0))
        heading = tk.Frame(card, bg=COLORS["surface"])
        heading.pack(fill="x", pady=(0, 9))
        heading.columnconfigure(0, weight=1)
        title = tk.Frame(heading, bg=COLORS["surface"])
        title.grid(row=0, column=0, sticky="w")
        tk.Label(
            title,
            text="03",
            bg=COLORS["primary"],
            fg=COLORS["white"],
            width=3,
            pady=3,
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left")
        self._localize_widget(
            tk.Label(
                title,
                bg=COLORS["surface"],
                fg=COLORS["text"],
                font=("Segoe UI Semibold", 11),
            ),
            "history_title",
        ).pack(side="left", padx=9)
        self._localize_widget(
            tk.Button(
                heading,
                command=self.clear_history,
                bg=COLORS["surface"],
                activebackground=COLORS["surface_alt"],
                fg=COLORS["danger"],
                activeforeground=COLORS["danger"],
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI", 8),
            ),
            "clear_history",
        ).grid(row=0, column=1)

        table_frame = tk.Frame(card, bg=COLORS["surface"])
        table_frame.pack(fill="both", expand=True)
        columns = ("time", "tool", "mode", "input", "result", "details")
        self.history = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=4,
            style="History.Treeview",
        )
        widths = (60, 105, 115, 165, 105, 220)
        for column, width in zip(columns, widths):
            self.history.column(
                column,
                width=width,
                minwidth=55,
                anchor="w",
                stretch=column == "details",
            )
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.history.yview,
            style="Vertical.TScrollbar",
        )
        self.history.configure(yscrollcommand=scrollbar.set)
        self.history.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_status_bar(self) -> None:
        status = tk.Frame(self.content, bg=COLORS["background"])
        status.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(9, 0))
        status.columnconfigure(1, weight=1)
        self.status_dot = tk.Label(
            status,
            text="*",
            bg=COLORS["background"],
            fg=COLORS["accent"],
            font=("Segoe UI", 11, "bold"),
        )
        self.status_dot.grid(row=0, column=0, padx=(0, 5))
        tk.Label(
            status,
            textvariable=self.status_value,
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8),
        ).grid(row=0, column=1, sticky="w")
        self._localize_widget(
            tk.Label(
                status,
                bg=COLORS["background"],
                fg=COLORS["muted"],
                font=("Segoe UI", 8),
            ),
            "shortcuts",
        ).grid(row=0, column=2, sticky="e")

    def _bind_shortcuts(self) -> None:
        self.bind("<Return>", lambda _event: self.calculate())
        self.bind("<Control-l>", lambda _event: self.reset())
        self.bind("<Control-L>", lambda _event: self.reset())
        self.bind("<Control-c>", self._copy_shortcut)
        self.bind("<Control-C>", self._copy_shortcut)

    def _copy_shortcut(self, _event: tk.Event) -> str | None:
        if isinstance(self.focus_get(), (tk.Entry, ttk.Entry, ttk.Combobox)):
            return None
        self.copy_result()
        return "break"

    def _change_language(self, _event: tk.Event | None = None) -> None:
        selected = self.language_name.get()
        self.language = next(
            (code for code, name in LANGUAGES.items() if name == selected),
            "en",
        )
        self._apply_language()

    def _apply_language(self) -> None:
        self.title(self.tr("app_title"))
        for widget, key in self.localized_widgets:
            if widget.winfo_exists():
                widget.config(text=self.tr(key))
        self._update_history_headings()
        self._update_tool_buttons()
        self._update_header()
        self._render_modes()
        self._render_fields()
        self.reset(message=self.tr("ready"))

    def _update_history_headings(self) -> None:
        keys = (
            "history_time",
            "history_tool",
            "history_mode",
            "history_input",
            "history_result",
            "history_details",
        )
        for column, key in zip(self.history["columns"], keys):
            self.history.heading(column, text=self.tr(key))

    def select_tool(self, key: str) -> None:
        self.active_tool = TOOLS_BY_KEY[key]
        self.active_mode = self.active_tool.modes[0]
        self._update_tool_buttons()
        self._update_header()
        self._render_modes()
        self._render_fields()
        self.reset(message=self.tr("tool_selected"))

    def _update_tool_buttons(self) -> None:
        for tool in TOOLS:
            button = self.tool_buttons[tool.key]
            selected = tool.key == self.active_tool.key
            button.config(
                text=f"  {tool.badge}    {self.tr(tool.short_key)}",
                bg=COLORS["surface_alt"] if selected else COLORS["sidebar"],
                fg=COLORS["white"] if selected else COLORS["muted"],
                activebackground=COLORS["border"],
                activeforeground=COLORS["white"],
            )

    def _update_header(self) -> None:
        tool = self.active_tool
        self.header_badge.config(text=self.tr(tool.short_key).upper())
        self.header_title.config(text=self.tr(tool.title_key))
        self.header_subtitle.config(text=self.tr(tool.subtitle_key))
        self.header_fact.config(text=self.tr(tool.fact_key))

    def _render_modes(self) -> None:
        for widget in self.mode_frame.winfo_children():
            widget.destroy()
        self.mode_buttons.clear()
        for column, mode in enumerate(self.active_tool.modes):
            self.mode_frame.columnconfigure(column, weight=1)
            button = tk.Button(
                self.mode_frame,
                text=self.tr(mode.label_key),
                command=lambda selected=mode: self.select_mode(selected),
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=("Segoe UI Semibold", 8),
                pady=8,
            )
            button.grid(row=0, column=column, sticky="ew")
            self.mode_buttons[mode.key] = button
        self._update_mode_buttons()

    def select_mode(self, mode: Mode) -> None:
        self.active_mode = mode
        self._update_mode_buttons()
        self._render_fields()
        self.reset(message=self.tr("mode_changed"))

    def _update_mode_buttons(self) -> None:
        for key, button in self.mode_buttons.items():
            selected = key == self.active_mode.key
            button.config(
                bg=COLORS["primary"] if selected else COLORS["surface_alt"],
                fg=COLORS["white"] if selected else COLORS["muted"],
                activebackground=(
                    COLORS["primary_hover"] if selected else COLORS["border"]
                ),
                activeforeground=COLORS["white"],
            )

    def _render_fields(self) -> None:
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.input_vars.clear()
        for field in self.active_mode.fields:
            self._build_field(field)
        self.after(40, self._focus_first_field)

    def _build_field(self, field: Field) -> None:
        variable = tk.StringVar(value=field.default)
        self.input_vars[field.key] = variable
        tk.Label(
            self.fields_frame,
            text=self.tr(field.label_key),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI Semibold", 7),
        ).pack(anchor="w")
        shell = tk.Frame(
            self.fields_frame,
            bg=COLORS["surface_alt"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        shell.pack(fill="x", pady=(4, 8))
        shell.columnconfigure(0, weight=1)
        entry = tk.Entry(
            shell,
            textvariable=variable,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 12, "bold"),
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(12, 5), pady=7)
        entry.bind(
            "<FocusIn>",
            lambda _event, example=field.example: self._set_status(
                self.tr("example", value=example)
            ),
        )
        tk.Label(
            shell,
            text=self.tr(field.unit_key),
            bg=COLORS["surface_alt"],
            fg=COLORS["accent"],
            font=("Segoe UI Semibold", 8),
            padx=11,
        ).grid(row=0, column=1)

    def _focus_first_field(self) -> None:
        entries = self._find_entries(self.fields_frame)
        if entries:
            entries[0].focus_set()

    def _find_entries(self, parent: tk.Widget) -> list[tk.Entry]:
        entries = []
        for child in parent.winfo_children():
            if isinstance(child, tk.Entry):
                entries.append(child)
            else:
                entries.extend(self._find_entries(child))
        return entries

    def calculate(self) -> None:
        try:
            values = {
                key: parse_number(variable.get(), self.tr)
                for key, variable in self.input_vars.items()
            }
            result = self.active_tool.calculator(
                values,
                self.active_mode.key,
                self.tr,
            )
        except ValueError as error:
            self._set_status(str(error), is_error=True)
            self.bell()
            return

        self.last_result = result
        unit = self.tr(result.unit_key)
        self.result_value.set(format_number(result.value))
        self.result_unit.set(unit)
        self.detail_value.set(result.detail)
        for index, (label, value) in enumerate(result.stats):
            self.stat_labels[index].set(label)
            self.stat_values[index].set(value)

        input_summary = ", ".join(
            f"{self.tr(field.label_key).lower()}: "
            f"{format_number(values[field.key])} {self.tr(field.unit_key)}"
            for field in self.active_mode.fields
        )
        tool_name = self.tr(self.active_tool.title_key)
        mode_name = self.tr(self.active_mode.label_key)
        self.last_summary = (
            f"{tool_name} - {mode_name}: "
            f"{format_number(result.value)} {unit}. {result.detail}"
        )
        self._add_history(input_summary, result, tool_name, mode_name, unit)
        self._set_status(self.tr("calculation_complete"))

    def _add_history(
        self,
        input_summary: str,
        result: CalculationResult,
        tool_name: str,
        mode_name: str,
        unit: str,
    ) -> None:
        self.history.insert(
            "",
            0,
            values=(
                datetime.now().strftime("%H:%M:%S"),
                tool_name,
                mode_name,
                input_summary,
                f"{format_number(result.value)} {unit}",
                result.detail,
            ),
        )
        children = self.history.get_children()
        if len(children) > 30:
            self.history.delete(children[-1])

    def reset(self, message: str | None = None) -> None:
        defaults = {field.key: field.default for field in self.active_mode.fields}
        for key, variable in self.input_vars.items():
            variable.set(defaults.get(key, ""))
        self.result_value.set("0")
        self.result_unit.set(self.tr(self.active_mode.label_key))
        self.detail_value.set(self.tr("fill_fields"))
        for label, value in zip(self.stat_labels, self.stat_values):
            label.set(self.tr("statistic"))
            value.set("0")
        self.last_result = None
        self.last_summary = ""
        self._set_status(message or self.tr("fields_reset"))
        self.after(20, self._focus_first_field)

    def copy_result(self) -> None:
        if not self.last_summary:
            self._set_status(self.tr("nothing_to_copy"), is_error=True)
            return
        self.clipboard_clear()
        self.clipboard_append(self.last_summary)
        self._set_status(self.tr("result_copied"))

    def clear_history(self) -> None:
        if not self.history.get_children():
            self._set_status(self.tr("history_empty"))
            return
        if messagebox.askyesno(
            self.tr("clear_history_title"),
            self.tr("clear_history_question"),
            parent=self,
        ):
            self.history.delete(*self.history.get_children())
            self._set_status(self.tr("history_cleared"))

    def _set_status(self, message: str, is_error: bool = False) -> None:
        self.status_value.set(message)
        self.status_dot.config(
            fg=COLORS["danger"] if is_error else COLORS["accent"]
        )
