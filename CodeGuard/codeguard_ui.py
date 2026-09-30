import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from codeguard import Lexer, Parser, SemanticAnalyzer


class CodeGuardUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeGuard - Static Analyzer for a C-Subset")
        self.root.geometry("1200x750")
        self.root.minsize(950, 600)

        self.current_file = None

        self.create_ui()

    # ============================================================
    # UI SETUP
    # ============================================================

    def create_ui(self):

        # ========================================================
        # HEADER
        # ========================================================

        header = ttk.Frame(
            self.root,
            padding=15
        )

        header.pack(
            fill="x"
        )

        title = ttk.Label(
            header,
            text="CodeGuard",
            font=("Arial", 24, "bold")
        )

        title.pack(
            side="left"
        )

        subtitle = ttk.Label(
            header,
            text="Static Analyzer for a C-Subset",
            font=("Arial", 11)
        )

        subtitle.pack(
            side="left",
            padx=(12, 0),
            pady=(8, 0)
        )

        # ========================================================
        # TOOLBAR
        # ========================================================

        toolbar = ttk.Frame(
            self.root,
            padding=(15, 0, 15, 10)
        )

        toolbar.pack(
            fill="x"
        )

        ttk.Button(
            toolbar,
            text="Open File",
            command=self.open_file
        ).pack(
            side="left",
            padx=(0, 5)
        )

        ttk.Button(
            toolbar,
            text="Save",
            command=self.save_file
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            toolbar,
            text="Analyze Code",
            command=self.analyze
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            toolbar,
            text="Clear",
            command=self.clear_editor
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            toolbar,
            text="Load Sample",
            command=self.load_sample
        ).pack(
            side="left",
            padx=5
        )

        # ========================================================
        # MAIN AREA
        # ========================================================

        main = ttk.PanedWindow(
            self.root,
            orient="horizontal"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 10)
        )

        # ========================================================
        # LEFT SIDE - SOURCE CODE
        # ========================================================

        editor_frame = ttk.LabelFrame(
            main,
            text="Source Code",
            padding=10
        )

        main.add(
            editor_frame,
            weight=1
        )

        # Editor container
        editor_container = ttk.Frame(
            editor_frame
        )

        editor_container.pack(
            fill="both",
            expand=True
        )

        self.editor = tk.Text(
            editor_container,
            wrap="none",
            font=("Courier New", 12),
            undo=True
        )

        self.editor.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        editor_container.rowconfigure(
            0,
            weight=1
        )

        editor_container.columnconfigure(
            0,
            weight=1
        )

        # Vertical scrollbar
        editor_scroll_y = ttk.Scrollbar(
            editor_container,
            orient="vertical",
            command=self.editor.yview
        )

        editor_scroll_y.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        # Horizontal scrollbar
        editor_scroll_x = ttk.Scrollbar(
            editor_container,
            orient="horizontal",
            command=self.editor.xview
        )

        editor_scroll_x.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.editor.configure(
            yscrollcommand=editor_scroll_y.set,
            xscrollcommand=editor_scroll_x.set
        )

        # ========================================================
        # RIGHT SIDE - RESULTS
        # ========================================================

        results_frame = ttk.LabelFrame(
            main,
            text="Analysis Results",
            padding=10
        )

        main.add(
            results_frame,
            weight=1
        )

        self.notebook = ttk.Notebook(
            results_frame
        )

        self.notebook.pack(
            fill="both",
            expand=True
        )

        # ========================================================
        # TOKENS TAB
        # ========================================================

        token_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            token_tab,
            text="Tokens"
        )

        token_container = ttk.Frame(
            token_tab
        )

        token_container.pack(
            fill="both",
            expand=True
        )

        self.token_output = tk.Text(
            token_container,
            wrap="none",
            font=("Courier New", 11),
            state="disabled"
        )

        self.token_output.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        token_container.rowconfigure(
            0,
            weight=1
        )

        token_container.columnconfigure(
            0,
            weight=1
        )

        token_scroll_y = ttk.Scrollbar(
            token_container,
            orient="vertical",
            command=self.token_output.yview
        )

        token_scroll_y.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        token_scroll_x = ttk.Scrollbar(
            token_container,
            orient="horizontal",
            command=self.token_output.xview
        )

        token_scroll_x.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.token_output.configure(
            yscrollcommand=token_scroll_y.set,
            xscrollcommand=token_scroll_x.set
        )

        # ========================================================
        # AST TAB
        # ========================================================

        ast_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            ast_tab,
            text="AST"
        )

        ast_container = ttk.Frame(
            ast_tab
        )

        ast_container.pack(
            fill="both",
            expand=True
        )

        self.ast_output = tk.Text(
            ast_container,
            wrap="none",
            font=("Courier New", 11),
            state="disabled"
        )

        self.ast_output.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        ast_container.rowconfigure(
            0,
            weight=1
        )

        ast_container.columnconfigure(
            0,
            weight=1
        )

        ast_scroll_y = ttk.Scrollbar(
            ast_container,
            orient="vertical",
            command=self.ast_output.yview
        )

        ast_scroll_y.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        ast_scroll_x = ttk.Scrollbar(
            ast_container,
            orient="horizontal",
            command=self.ast_output.xview
        )

        ast_scroll_x.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.ast_output.configure(
            yscrollcommand=ast_scroll_y.set,
            xscrollcommand=ast_scroll_x.set
        )

        # ========================================================
        # ERRORS TAB
        # ========================================================

        error_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            error_tab,
            text="Errors / Summary"
        )

        error_container = ttk.Frame(
            error_tab
        )

        error_container.pack(
            fill="both",
            expand=True
        )

        self.error_output = tk.Text(
            error_container,
            wrap="word",
            font=("Courier New", 11),
            state="disabled"
        )

        self.error_output.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        error_container.rowconfigure(
            0,
            weight=1
        )

        error_container.columnconfigure(
            0,
            weight=1
        )

        error_scroll_y = ttk.Scrollbar(
            error_container,
            orient="vertical",
            command=self.error_output.yview
        )

        error_scroll_y.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.error_output.configure(
            yscrollcommand=error_scroll_y.set
        )

        # ========================================================
        # STATUS BAR
        # ========================================================

        self.status = tk.StringVar()

        self.status.set(
            "Ready"
        )

        status_bar = ttk.Label(
            self.root,
            textvariable=self.status,
            relief="sunken",
            anchor="w",
            padding=5
        )

        status_bar.pack(
            fill="x"
        )

    # ============================================================
    # FILE FUNCTIONS
    # ============================================================

    def open_file(self):

        filepath = filedialog.askopenfilename(
            title="Open CodeGuard File",
            filetypes=[
                ("CodeGuard Files", "*.cg"),
                ("C Files", "*.c"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not filepath:
            return

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                content = file.read()

            self.editor.delete(
                "1.0",
                tk.END
            )

            self.editor.insert(
                "1.0",
                content
            )

            self.current_file = filepath

            self.status.set(
                f"Opened: {filepath}"
            )

        except Exception as e:

            messagebox.showerror(
                "File Error",
                str(e)
            )

    def save_file(self):

        if self.current_file is None:

            filepath = filedialog.asksaveasfilename(
                defaultextension=".cg",
                filetypes=[
                    ("CodeGuard Files", "*.cg"),
                    ("C Files", "*.c"),
                    ("Text Files", "*.txt")
                ]
            )

            if not filepath:
                return

            self.current_file = filepath

        try:

            with open(
                self.current_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    self.editor.get(
                        "1.0",
                        tk.END
                    )
                )

            self.status.set(
                f"Saved: {self.current_file}"
            )

        except Exception as e:

            messagebox.showerror(
                "Save Error",
                str(e)
            )

    # ============================================================
    # ANALYSIS
    # ============================================================

    def analyze(self):

        source = self.editor.get(
            "1.0",
            tk.END
        ).strip()

        if not source:

            messagebox.showwarning(
                "No Code",
                "Enter or open source code first."
            )

            return

        self.clear_outputs()

        self.status.set(
            "Analyzing..."
        )

        try:

            # ====================================================
            # PHASE 1: LEXICAL ANALYSIS
            # ====================================================

            lexer = Lexer(source)

            tokens = lexer.tokenize()

            token_text = (
                "TOKEN TYPE      VALUE           LINE\n"
            )

            token_text += (
                "=" * 50 + "\n"
            )

            for token in tokens:

                if token.type == "EOF":
                    continue

                token_text += (
                    f"{token.type:<15}"
                    f"{token.value:<16}"
                    f"{token.line}\n"
                )

            self.set_output(
                self.token_output,
                token_text
            )

            # ----------------------------------------------------
            # CHECK LEXICAL ERRORS
            # ----------------------------------------------------

            if lexer.errors:

                error_text = (
                    "ANALYSIS FAILED\n\n"
                    "✗ Lexical Analysis: Failed\n"
                    "○ Syntax Analysis: Not performed\n"
                    "○ Semantic Analysis: Not performed\n\n"
                    "ERRORS\n"
                    + "-" * 40
                    + "\n"
                )

                error_text += "\n".join(
                    lexer.errors
                )

                self.set_output(
                    self.error_output,
                    error_text
                )

                self.status.set(
                    "Lexical analysis failed"
                )

                # Automatically show Errors tab
                self.notebook.select(2)

                return

            # ====================================================
            # PHASE 2: SYNTAX ANALYSIS
            # ====================================================

            parser = Parser(
                tokens
            )

            ast = parser.parse()

            ast_text = self.format_ast(
                ast
            )

            self.set_output(
                self.ast_output,
                ast_text
            )

            # ----------------------------------------------------
            # CHECK SYNTAX ERRORS
            # ----------------------------------------------------

            if parser.errors:

                error_text = (
                    "ANALYSIS FAILED\n\n"
                    "✓ Lexical Analysis: Passed\n"
                    "✗ Syntax Analysis: Failed\n"
                    "○ Semantic Analysis: Not performed\n\n"
                    "ERRORS\n"
                    + "-" * 40
                    + "\n"
                )

                error_text += "\n".join(
                    parser.errors
                )

                self.set_output(
                    self.error_output,
                    error_text
                )

                self.status.set(
                    "Syntax analysis failed"
                )

                self.notebook.select(2)

                return

            # ====================================================
            # PHASE 3: SEMANTIC ANALYSIS
            # ====================================================

            semantic = SemanticAnalyzer()

            semantic.analyze(
                ast
            )

            # ----------------------------------------------------
            # CHECK SEMANTIC ERRORS
            # ----------------------------------------------------

            if semantic.errors:

                error_text = (
                    "ANALYSIS FAILED\n\n"
                    "✓ Lexical Analysis: Passed\n"
                    "✓ Syntax Analysis: Passed\n"
                    "✗ Semantic Analysis: Failed\n\n"
                    "ERRORS\n"
                    + "-" * 40
                    + "\n"
                )

                error_text += "\n".join(
                    semantic.errors
                )

                self.set_output(
                    self.error_output,
                    error_text
                )

                self.status.set(
                    "Semantic analysis failed"
                )

                self.notebook.select(2)

                return

            # ====================================================
            # ALL PHASES PASSED
            # ====================================================

            success_message = (
                "ANALYSIS SUCCESSFUL\n\n"
                "✓ Lexical Analysis: Passed\n"
                "✓ Syntax Analysis: Passed\n"
                "✓ Semantic Analysis: Passed\n\n"
                "No lexical, syntax, or semantic "
                "errors were detected."
            )

            self.set_output(
                self.error_output,
                success_message
            )

            self.status.set(
                "Analysis completed successfully"
            )

            self.notebook.select(2)

        except Exception as e:

            self.set_output(
                self.error_output,
                "ANALYSIS FAILED\n\n"
                + "Unexpected application error:\n"
                + str(e)
            )

            self.status.set(
                "Analysis completed with errors"
            )

            self.notebook.select(2)

    # ============================================================
    # AST DISPLAY
    # ============================================================

    def format_ast(
        self,
        node,
        level=0
    ):

        indent = (
            "    " * level
        )

        if node is None:

            return (
                indent
                + "None\n"
            )

        # --------------------------------------------------------
        # LIST
        # --------------------------------------------------------

        if isinstance(
            node,
            list
        ):

            result = ""

            for item in node:

                result += self.format_ast(
                    item,
                    level
                )

            return result

        # --------------------------------------------------------
        # SIMPLE VALUES
        # --------------------------------------------------------

        if isinstance(
            node,
            (str, int, float)
        ):

            return (
                indent
                + repr(node)
                + "\n"
            )

        # --------------------------------------------------------
        # AST OBJECT
        # --------------------------------------------------------

        result = (
            indent
            + node.__class__.__name__
            + "\n"
        )

        if hasattr(
            node,
            "__dict__"
        ):

            for name, value in vars(node).items():

                result += (
                    indent
                    + "    "
                    + name
                    + ": "
                )

                if isinstance(
                    value,
                    (str, int, float)
                ):

                    result += (
                        repr(value)
                        + "\n"
                    )

                else:

                    result += "\n"

                    result += self.format_ast(
                        value,
                        level + 2
                    )

        return result

    # ============================================================
    # OUTPUT HELPER
    # ============================================================

    def set_output(
        self,
        widget,
        content
    ):

        widget.configure(
            state="normal"
        )

        widget.delete(
            "1.0",
            tk.END
        )

        widget.insert(
            "1.0",
            content
        )

        widget.configure(
            state="disabled"
        )

    # ============================================================
    # CLEAR OUTPUTS
    # ============================================================

    def clear_outputs(self):

        self.set_output(
            self.token_output,
            ""
        )

        self.set_output(
            self.ast_output,
            ""
        )

        self.set_output(
            self.error_output,
            ""
        )

    # ============================================================
    # CLEAR EVERYTHING
    # ============================================================

    def clear_editor(self):

        self.editor.delete(
            "1.0",
            tk.END
        )

        self.clear_outputs()

        self.current_file = None

        self.status.set(
            "Ready"
        )

    # ============================================================
    # LOAD SAMPLE PROGRAM
    # ============================================================

    def load_sample(self):

        sample = """int x;
float y;

x = 5;
y = 3.14;

if (x > 2) {
    int z;
    z = x + 5;
}

while (x < 10) {
    x = x + 1;
}
"""

        self.editor.delete(
            "1.0",
            tk.END
        )

        self.editor.insert(
            "1.0",
            sample
        )

        self.current_file = None

        self.clear_outputs()

        self.status.set(
            "Sample program loaded"
        )


# ================================================================
# RUN APPLICATION
# ================================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CodeGuardUI(
        root
    )

    root.mainloop()
