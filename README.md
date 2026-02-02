# DorkScript

**Version control for search strategies.**  
A good search query is knowledge worth preserving. Stop losing yours.

> [!TIP]
> One Python file. No install. No dependencies. Queries in a file, opened in your browser.

## Table of Contents

- [Quick Start](#quick-start)
- [The .dork Format](#the-dork-format)
- [Usage](#usage)
- [Self Test](#self-test)
- [Philosophy](#philosophy)
- [Examples](#examples)
- [Why Not Just Use Bookmarks?](#why-not-just-use-bookmarks)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

```bash
python dork.py search.dork
```

That's it.

---

## The .dork Format

```bash
# Comments start with #
site:example.com filetype:pdf

# Change search engine
@engine github
language:python oauth

# Variables for reusable templates
@var TARGET = example.com
site:$TARGET "admin"

# Inline comments (after whitespace)
site:example.com "sensitive"  # A query
```

---

## Usage

```bash
python dork.py search.dork           # Run all queries
python dork.py search.dork -p        # Preview only (don't open browser)
python dork.py search.dork -n 5      # Run first 5 queries
python dork.py search.dork -e ddg    # Use DuckDuckGo
python -m dork search.dork           # Run as a module
```

> [!NOTE]
> **Windows users:** Wrapper scripts are included for convenience.
>
> **Command Prompt (cmd.exe):**
>
> ```cmd
> dork search.dork
> ```
>
> **PowerShell:**
>
> ```powershell
> .\dork search.dork
> ```
>
> PowerShell doesn't run commands from the current directory without `.\` prefix.
> May also require `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` to allow scripts.

Engines: `google`, `bing`, `ddg`, `github`, `shodan`  
Run `python dork.py --engines` for the full list.

---

## Self Test

```bash
python dork.py --selftest
```

---

## Philosophy

This tool does less on purpose:

- **No scraping** - Opens queries in YOUR browser. Legal. No rate limits. No CAPTCHAs.
- **No dependencies** - Just Python 3 (you already have it).
- **No install** - Download and run.
- **No database** - Plain text files. Use git.
- **No complexity** - Read the entire source in 5 minutes.

> [!IMPORTANT]
> The value is in the .dork files themselves, not in this tool. Build a library. Share it. Collaborate.

---

## Examples

See `/examples` for starter templates:

- `academic-research.dork` - Literature review
- `comprehensive-osint.dork` - Multi-engine OSINT
- `exposed-secrets.dork` - Security research
- `full-recon.dork` - Comprehensive target recon
- `osint-person.dork` - People research
- `public-documents.dork` - OSINT / journalism

---

## Why Not Just Use Bookmarks?

Bookmarks break when URLs change. You can't parameterize them. You can't version control them. You can't share a search _strategy_.

A .dork file captures your methodology, not just the results.

---

## Contributing

Add your .dork files. That's the contribution. The tool is done.

---

## License

MIT. See `LICENSE`.
