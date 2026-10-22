"""A graphical interface for the Wikipedia search-summary tool."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from urllib.error import URLError

from main import create_tk_root, fetch_wikipedia_summary


LookupResult = tuple[str, str, str]


def lookup_in_background(results: queue.Queue[LookupResult], search_term: str) -> None:
    """Fetch a summary on a worker thread and send the result back to the GUI."""
    try:
        article = fetch_wikipedia_summary(search_term)
    except (URLError, TimeoutError, OSError, ValueError) as error:
        results.put(("error", f"Could not retrieve a Wikipedia summary: {error}", ""))
        return

    if article is None:
        results.put(("not_found", search_term, ""))
        return

    title, summary = article
    results.put(("summary", title, summary))


class SearchSummaryApp:
    """Manage the widgets and search behavior for the desktop application."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.results: queue.Queue[LookupResult] = queue.Queue()
        self.searching = False

        root.title("Wikipedia Search Summary")
        root.minsize(480, 360)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1)

        header = tk.Frame(root)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self.window_icon = tk.PhotoImage(
            file=str(Path(__file__).parent / "assets" / "qa-logo.png")
        )
        root.iconphoto(True, self.window_icon)
        self.wordmark = tk.PhotoImage(
            file=str(Path(__file__).parent / "assets" / "qa-wordmark.png")
        ).subsample(3, 3)
        tk.Label(header, image=self.wordmark).grid(
            row=0, column=0, rowspan=2, padx=(0, 10)
        )
        tk.Label(
            header, text="Wikipedia Search Summary", font=("TkDefaultFont", 16, "bold")
        ).grid(row=0, column=1, sticky="w")
        tk.Label(header, text="Enter a word or phrase to explain:").grid(
            row=1, column=1, sticky="w", pady=(2, 0)
        )

        search_row = tk.Frame(root)
        search_row.grid(row=1, column=0, sticky="ew", padx=12)
        search_row.columnconfigure(0, weight=1)

        self.search_entry = tk.Entry(search_row)
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<Return>", self._start_search)

        self.search_button = tk.Button(
            search_row, text="Search", command=self._start_search
        )
        self.search_button.grid(row=0, column=1, padx=(8, 0))

        self.status = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status, anchor="w").grid(
            row=2, column=0, sticky="ew", padx=12, pady=8
        )

        output_frame = tk.Frame(root)
        output_frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output = tk.Text(output_frame, wrap="word", state="disabled")
        self.output.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(
            output_frame, orient="vertical", command=self.output.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output.configure(yscrollcommand=scrollbar.set)

        self.search_entry.focus_set()
        self.root.after(100, self._check_results)

    def _start_search(self, _event: object | None = None) -> None:
        """Validate the input and start a non-blocking Wikipedia lookup."""
        if self.searching:
            return

        search_term = self.search_entry.get().strip()
        if not search_term:
            self.status.set("Please enter a word or phrase.")
            self.search_entry.focus_set()
            return

        self.searching = True
        self.search_button.configure(state="disabled")
        self.status.set(f'Searching Wikipedia for "{search_term}"...')
        self._set_output("")

        worker = threading.Thread(
            target=lookup_in_background,
            args=(self.results, search_term),
            daemon=True,
        )
        worker.start()

    def _check_results(self) -> None:
        """Display completed worker results on Tkinter's main thread."""
        try:
            kind, title_or_message, summary = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.searching = False
            self.search_button.configure(state="normal")

            if kind == "summary":
                self.status.set(f"Found: {title_or_message}")
                self._set_output(
                    f"{summary}\n\nSource: Wikipedia — {title_or_message}"
                )
            elif kind == "not_found":
                self.status.set("No Wikipedia summary was found.")
                self._set_output(f"No summary found for: {title_or_message}")
            else:
                self.status.set("The search could not be completed.")
                self._set_output(title_or_message)

        self.root.after(100, self._check_results)

    def _set_output(self, text: str) -> None:
        """Replace the read-only summary text."""
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")


def main(create_root: Callable[[], tk.Tk] = create_tk_root) -> None:
    """Create and run the GUI."""
    root = create_root()
    SearchSummaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
