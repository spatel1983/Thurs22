"""Fetch a short Wikipedia summary and display it in a message box."""  # Describe this script.

import argparse  # Parse command-line options.
import json  # Decode the response from Wikipedia's API.
import os  # Configure Tcl/Tk resource paths when needed.
import sys  # Locate the base Python installation.
from collections.abc import Sequence  # Type the optional command-line arguments.
from pathlib import Path  # Check for Tcl/Tk resource files.
from tkinter import Tk, TclError, TclVersion, TkVersion, messagebox  # Display desktop dialogs.
from urllib.error import URLError  # Identify network and HTTP request failures.
from urllib.parse import urlencode  # Encode API parameters safely.
from urllib.request import Request, urlopen  # Make the standard-library web request.


def create_tk_root() -> Tk:  # Create a root window with Tcl/Tk resources configured.
    """Create a Tk root, locating bundled Tcl/Tk files if automatic discovery fails."""
    tcl_library = Path(sys.base_prefix, "tcl", f"tcl{TclVersion}")
    tk_library = Path(sys.base_prefix, "tcl", f"tk{TkVersion}")
    if not os.environ.get("TCL_LIBRARY") and (tcl_library / "init.tcl").is_file():
        os.environ["TCL_LIBRARY"] = str(tcl_library)
    if not os.environ.get("TK_LIBRARY") and (tk_library / "tk.tcl").is_file():
        os.environ["TK_LIBRARY"] = str(tk_library)
    return Tk()


def build_parser() -> argparse.ArgumentParser:  # Define the command-line argument parser.
    """Create the command-line argument parser."""  # Explain the function's purpose.
    parser = argparse.ArgumentParser(  # Create the parser and its help description.
        description="Fetch a short Wikipedia summary and show it in a message box."  # Describe the command.
    )  # Finish creating the parser.
    parser.add_argument(  # Add an optional positional search term.
        "search_term",  # Name used to access the value.
        nargs="?",  # Accept zero or one value.
        help="text to look up; prompted for if omitted",  # Explain how to provide the term.
    )  # Finish adding the argument.
    return parser  # Return the configured parser.


def fetch_wikipedia_summary(search_term: str) -> tuple[str, str] | None:  # Look up a matching article.
    """Return an article title and short plain-text summary, or None if no match exists."""  # Document the result.
    parameters = urlencode(  # Encode search and extract options for the API URL.
        {  # Start the API parameter mapping.
            "action": "query",  # Ask Wikipedia to query its article index.
            "generator": "search",  # Find an article matching the supplied text.
            "gsrsearch": search_term,  # Set the search text.
            "gsrlimit": 1,  # Request only the best matching article.
            "prop": "extracts",  # Include the article's introductory text.
            "exintro": 1,  # Limit the extract to the introduction.
            "explaintext": 1,  # Return plain text instead of HTML.
            "exsentences": 3,  # Keep the summary short.
            "redirects": 1,  # Follow article redirects where applicable.
            "format": "json",  # Request a JSON response.
            "formatversion": 2,  # Use a straightforward list for returned pages.
        }  # Finish the API parameter mapping.
    )  # Finish encoding the parameters.
    request = Request(  # Build a request with a descriptive client identifier.
        f"https://en.wikipedia.org/w/api.php?{parameters}",  # Set the API endpoint and query.
        headers={"User-Agent": "PythonSearchSummary/1.0 (educational use)"},  # Identify this small client.
    )  # Finish creating the request.

    with urlopen(request, timeout=10) as response:  # Fetch the API response with a time limit.
        data = json.loads(response.read().decode("utf-8"))  # Decode the response as JSON.

    if not isinstance(data, dict):  # Check that the response root is a JSON object.
        raise ValueError("Wikipedia returned an unexpected response.")  # Report malformed API data.
    query = data.get("query")  # Get the query section from the response.
    if not isinstance(query, dict):  # Check that the API returned the expected structure.
        raise ValueError("Wikipedia returned an unexpected response.")  # Report malformed API data.
    pages = query.get("pages", [])  # Get the matching article pages, if any.
    if not isinstance(pages, list):  # Ensure the page results have the expected type.
        raise ValueError("Wikipedia returned an unexpected page list.")  # Report malformed page data.
    if not pages:  # Check whether the search found a matching article.
        return None  # Tell the caller there is no summary to display.

    page = pages[0]  # Use the best matching article.
    if not isinstance(page, dict):  # Check that the article entry is a JSON object.
        raise ValueError("Wikipedia returned an incomplete article.")  # Report malformed article data.
    title = page.get("title")  # Read the article title.
    summary = page.get("extract", "").strip()  # Read and trim the introductory text.
    if not isinstance(title, str) or not isinstance(summary, str):  # Validate the article fields.
        raise ValueError("Wikipedia returned an incomplete article.")  # Report malformed article data.
    if not summary:  # Check whether the article contains any introductory text.
        return None  # Treat an empty extract as no available summary.
    return title, summary  # Return the title and its short explanation.


def show_message(title: str, message: str, is_error: bool = False) -> bool:  # Display a desktop message box.
    """Show an information or error dialog and report whether it was displayed."""  # Describe the function.
    window = None  # Keep a reference so the hidden root window can be closed.
    try:  # Handle systems where a desktop message box cannot be created.
        window = create_tk_root()  # Create the hidden Tkinter root window.
        window.withdraw()  # Hide the empty root window.
        if is_error:  # Choose the appropriate dialog style.
            messagebox.showerror(title, message, parent=window)  # Display an error dialog.
        else:  # Use an information dialog for summaries and no-match messages.
            messagebox.showinfo(title, message, parent=window)  # Display the requested message.
        return True  # Report that the dialog was displayed.
    except TclError:  # Catch missing display or other Tkinter dialog errors.
        return False  # Let the caller report the result in the console instead.
    finally:  # Always close the hidden root window when it was created.
        if window is not None:  # Check that creating the root window succeeded.
            window.destroy()  # Release the Tkinter window resources.


def main(argv: Sequence[str] | None = None) -> int:  # Run the program and return an exit status.
    """Get a term, fetch its summary, and show the result."""  # Document the function's purpose.
    args = build_parser().parse_args(argv)  # Parse a provided argument list or the normal command line.
    search_term = args.search_term  # Get the optional term from the parsed arguments.

    if search_term is None:  # Check whether the user omitted the command-line term.
        try:  # Handle cases where interactive input may not be available.
            search_term = input("Enter text to explain: ").strip()  # Prompt and trim surrounding whitespace.
        except EOFError:  # Catch closed input streams, such as when input is redirected.
            print("\nNo text was provided.")  # Explain why the program cannot continue.
            return 1  # Return a nonzero status to indicate failure.
    else:  # A term was supplied on the command line.
        search_term = search_term.strip()  # Trim whitespace around the supplied term.

    if not search_term:  # Reject an empty string or whitespace-only input.
        print("Please enter non-empty text.")  # Tell the user what to correct.
        return 1  # Return a nonzero status to indicate invalid input.

    try:  # Handle request, response-decoding, and API-format errors.
        article = fetch_wikipedia_summary(search_term)  # Look up a short explanation for the text.
    except (URLError, TimeoutError, OSError, ValueError) as error:  # Catch expected lookup failures.
        error_message = f"Could not retrieve a Wikipedia summary: {error}"  # Prepare a clear error message.
        if not show_message("Lookup failed", error_message, is_error=True):  # Try to display the error dialog.
            print(error_message)  # Report the error if a desktop dialog is unavailable.
        return 1  # Return a nonzero status to indicate the lookup failed.

    if article is None:  # Check whether a matching article and summary were found.
        message = f"No Wikipedia summary was found for: {search_term}"  # Explain the no-result outcome.
        if not show_message("No summary found", message):  # Display the no-result message.
            print(message)  # Use the console if a desktop dialog is unavailable.
        return 0  # The lookup completed successfully even though there was no match.

    title, summary = article  # Separate the article title from its summary.
    message = f"{summary}\n\nSource: Wikipedia — {title}"  # Include the attribution with the explanation.
    if not show_message(title, message):  # Display the summary in an information dialog.
        print(message)  # Use the console if a desktop dialog is unavailable.
        return 1  # Report that the requested message box could not be shown.
    return 0  # Return zero to indicate success.


if __name__ == "__main__":  # Run this block only when the file is executed directly.
    raise SystemExit(main())  # Pass the program's return code to the operating system.
