# Wikipedia Search Summary

A small Python program that looks up a word or phrase in Wikipedia and displays
a short introductory summary. Use the command-line version (`main.py`) for a
message-box result, or the graphical version (`gui.py`) for a desktop window.
The project is intended as a beginner-friendly example of Python functions,
command-line arguments, HTTP requests, JSON, GUI programming, error handling,
and GitHub documentation.

> This program searches Wikipedia, not Google. It shows the best matching
> Wikipedia article it receives; it does not search the whole web or generate
> an AI explanation.

## What it does

1. Gets a search term from the command line or a text field in the GUI.
2. Sends the term to the English Wikipedia API.
3. Requests the introduction (up to three sentences) of the best matching
   article.
4. Displays the article title and summary in a message box or GUI window.
5. Shows a helpful message if there is no summary, the network request fails,
   or a desktop GUI is unavailable.

An internet connection is needed to contact Wikipedia. The script uses only
Python's standard library; there are no third-party Python packages to install.

## Requirements

- Python 3.10 or later. The script uses modern type-hint syntax such as
  `Sequence[str] | None`.
- A working internet connection.
- Tkinter for the message box. It is usually included with the standard Python
  installer on Windows. Some Linux distributions package it separately.

To check that Python is available, run:

```text
python --version
```

On Windows, if `python` is not recognized, try `py --version`.

## Run the program

To get a copy from GitHub, open a terminal and run:

```text
git clone https://github.com/spatel1983/Thurs22.git
cd Thurs22
```

Then run a command below from that folder.

Run the command-line version, which prompts for a search term and displays the
summary in a message box:

```text
python main.py
```

Or provide it as a command-line argument:

```text
python main.py "climate change"
```

On Windows, you can also use the Python launcher:

```text
py main.py "Python programming"
```

Run the graphical version:

```text
python gui.py
```

Enter a word or phrase in the window and click **Search** or press **Enter**.
The GUI remains responsive while the lookup is in progress. The GUI version
does not require a terminal prompt.

An empty search term is rejected. The command-line version exits with status
`0` on success and `1` when it cannot complete the lookup or display a found
summary.

## How the code works

The command-line application and shared Wikipedia lookup are in `main.py`; the
desktop interface is in `gui.py`.

- **Imports** bring in Python's built-in tools: `argparse` reads command-line
  arguments, `urllib` makes the web request and encodes its parameters, `json`
  reads Wikipedia's response, and `tkinter` creates message boxes.
- **`build_parser()`** defines an optional positional argument named
  `search_term`. If it is omitted, the program asks for it interactively.
- **`fetch_wikipedia_summary(search_term)`** builds a request to Wikipedia's
  MediaWiki API. It asks for one search result, plain-text introductory content,
  and up to three sentences. It returns `(title, summary)` when a summary is
  available, or `None` when no suitable result is found. Network and malformed
  response errors are allowed to reach `main()` for handling.
- **`show_message(title, message, is_error=False)`** creates a hidden Tkinter
  root window and displays either an information dialog or an error dialog.
  It closes the root window afterward. It returns `False` if Tkinter cannot
  display the dialog.
- **`main(argv=None)`** connects the steps: it reads and validates the term,
  fetches the summary, handles expected errors, and displays the result. The
  optional `argv` parameter also makes the function easier to test.
- **`gui.py`** provides a window with a search field, Search button, status
  message, QA logo, and scrollable summary area. It reuses the lookup function
  from `main.py`.
- **`lookup_in_background()`** runs the network request on a worker thread.
  A queue carries results back so Tkinter widgets are only updated on the GUI
  thread; this keeps the window responsive during the request.
- **The `if __name__ == "__main__"` block** runs the program when `main.py` is
  launched directly and passes its exit status back to the operating system.

The request uses a 10-second timeout and identifies the program with a
User-Agent header. Only the search term is sent to Wikipedia; no credentials
are required.

## Troubleshooting

### No GUI or message box appears

Tkinter needs a working desktop session. On Linux, install the Tkinter package
provided by your distribution (often named `python3-tk`) and run the program
in a desktop session. The command-line version falls back to terminal output
if it cannot open a message box.

On Windows, the program uses Tcl/Tk resources bundled with the selected Python
installation when Python does not discover them automatically. If the
`init.tcl` error persists, repair or reinstall Python with Tcl/Tk included.

### The lookup fails

Check your internet connection and try again. Wikipedia may be temporarily
unavailable, or a firewall or network proxy may block the request. The program
does not retry automatically.

### No summary is found

The search did not return an article with introductory text. Try a different
spelling or a more specific term.

## Learning references

### Python

- [The Python Tutorial](https://docs.python.org/3/tutorial/)
- [`argparse` — command-line argument parsing](https://docs.python.org/3/library/argparse.html)
- [`urllib.request` — opening URLs](https://docs.python.org/3/library/urllib.request.html)
- [`urllib.parse` — parsing and encoding URLs](https://docs.python.org/3/library/urllib.parse.html)
- [`json` — working with JSON data](https://docs.python.org/3/library/json.html)
- [`tkinter` — Python's interface to Tcl/Tk](https://docs.python.org/3/library/tkinter.html)
- [Tkinter threading model](https://docs.python.org/3/library/tkinter.html#threading-model)
- [`threading` — thread-based parallelism](https://docs.python.org/3/library/threading.html)
- [`queue` — synchronized queues](https://docs.python.org/3/library/queue.html)
- [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)

### Wikipedia API

- [MediaWiki API documentation](https://www.mediawiki.org/wiki/API:Main_page)
- [Search API parameters](https://www.mediawiki.org/wiki/API:Search)
- [TextExtracts API](https://www.mediawiki.org/wiki/Extension:TextExtracts)
- [Wikipedia reuse and attribution guidance](https://en.wikipedia.org/wiki/Wikipedia:Reusing_Wikipedia_content)

The summary text comes from Wikipedia. This program displays the article title
as attribution; consult Wikipedia's reuse guidance when redistributing or
adapting its content.

### Git and GitHub

- [GitHub's introduction to Git](https://docs.github.com/en/get-started/using-git/about-git)
- [GitHub's guide to Markdown](https://docs.github.com/en/get-started/writing-on-github)
- [GitHub Docs](https://docs.github.com/)

## Project files

```text
.
├── main.py       # Command-line application and shared Wikipedia lookup
├── gui.py        # Desktop graphical interface
├── assets/       # QA wordmark and window icon used by the GUI
├── README.md     # Project overview, usage, and learning references
└── .gitignore    # Local files Git should not track
```

The QA logo assets are sourced from [qa.com](https://www.qa.com/).
