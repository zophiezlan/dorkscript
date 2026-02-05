#!/usr/bin/env python3
"""
DorkScript - Version control for search strategies.
A dead simple tool: queries in a file, opened in your browser.

Usage:
    python dork.py search.dork                    # Run all queries
    python dork.py search.dork -n 3               # Run first 3 queries
    python dork.py search.dork -p                 # Preview with full URLs
    python dork.py search.dork -e bing            # Use Bing instead of Google
    python dork.py search.dork TARGET=real.com    # Override variables
    python dork.py search.dork -o urls.txt        # Export URLs to file
    python dork.py search.dork -u                 # Just URLs (for piping)

That's it. No install. No dependencies. No complexity.
"""

import sys
import webbrowser
import urllib.parse
import time
import re
from pathlib import Path

__version__ = "2.1.0"
__license__ = "MIT"

# =============================================================================
# SEARCH ENGINES - 100+ engines organized by category
# =============================================================================

ENGINES = {
    # -------------------------------------------------------------------------
    # General Search Engines
    # -------------------------------------------------------------------------
    "google": "https://www.google.com/search?q=",
    "bing": "https://www.bing.com/search?q=",
    "ddg": "https://duckduckgo.com/?q=",
    "duckduckgo": "https://duckduckgo.com/?q=",
    "yandex": "https://yandex.com/search/?text=",
    "baidu": "https://www.baidu.com/s?wd=",
    "yahoo": "https://search.yahoo.com/search?p=",
    "brave": "https://search.brave.com/search?q=",
    "startpage": "https://www.startpage.com/do/search?q=",
    "qwant": "https://www.qwant.com/?q=",
    "ecosia": "https://www.ecosia.org/search?q=",
    "mojeek": "https://www.mojeek.com/search?q=",
    "swisscows": "https://swisscows.com/web?query=",
    "searx": "https://searx.be/search?q=",  # Public instance
    "metager": "https://metager.org/meta/meta.ger3?eingabe=",
    "dogpile": "https://www.dogpile.com/serp?q=",
    "aol": "https://search.aol.com/aol/search?q=",
    "ask": "https://www.ask.com/web?q=",
    "lycos": "https://search.lycos.com/web/?q=",
    "webcrawler": "https://www.webcrawler.com/serp?q=",
    "exalead": "https://www.exalead.com/search/web/results/?q=",
    "millionshort": "https://millionshort.com/search?keywords=",
    "carrot2": "https://search.carrot2.org/#/search/web/",
    "marginalia": "https://search.marginalia.nu/search?query=",
    "wiby": "https://wiby.me/?q=",
    # Regional
    "naver": "https://search.naver.com/search.naver?query=",  # Korea
    "sogou": "https://www.sogou.com/web?query=",  # China
    "seznam": "https://search.seznam.cz/?q=",  # Czechia
    "coccoc": "https://coccoc.com/search?query=",  # Vietnam
    # -------------------------------------------------------------------------
    # Google Operator Shortcuts (prepend operator to query)
    # -------------------------------------------------------------------------
    "google-site": "https://www.google.com/search?q=site:",  # site:example.com
    "google-filetype": "https://www.google.com/search?q=filetype:",  # filetype:pdf
    "google-ext": "https://www.google.com/search?q=ext:",  # ext:pdf
    "google-intitle": "https://www.google.com/search?q=intitle:",  # intitle:keyword
    "google-inurl": "https://www.google.com/search?q=inurl:",  # inurl:admin
    "google-intext": "https://www.google.com/search?q=intext:",  # intext:password
    "google-related": "https://www.google.com/search?q=related:",  # related:example.com
    "google-define": "https://www.google.com/search?q=define:",  # define:word
    "google-weather": "https://www.google.com/search?q=weather:",  # weather:city
    "google-stocks": "https://www.google.com/search?q=stocks:",  # stocks:AAPL
    "google-movie": "https://www.google.com/search?q=movie:",  # movie:title
    "google-map": "https://www.google.com/search?q=map:",  # map:location
    # Date filters (append to other queries)
    "google-recent": "https://www.google.com/search?tbs=qdr:m&q=",  # Past month
    "google-year": "https://www.google.com/search?tbs=qdr:y&q=",  # Past year
    "google-verbatim": "https://www.google.com/search?tbs=li:1&q=",  # Exact match
    # -------------------------------------------------------------------------
    # Bing Operator Shortcuts
    # -------------------------------------------------------------------------
    "bing-site": "https://www.bing.com/search?q=site:",
    "bing-filetype": "https://www.bing.com/search?q=filetype:",
    "bing-intitle": "https://www.bing.com/search?q=intitle:",
    "bing-inurl": "https://www.bing.com/search?q=inurl:",
    "bing-inbody": "https://www.bing.com/search?q=inbody:",
    # -------------------------------------------------------------------------
    # DuckDuckGo Operator Shortcuts
    # -------------------------------------------------------------------------
    "ddg-site": "https://duckduckgo.com/?q=site:",
    "ddg-filetype": "https://duckduckgo.com/?q=filetype:",
    "ddg-intitle": "https://duckduckgo.com/?q=intitle:",
    "ddg-inurl": "https://duckduckgo.com/?q=inurl:",
    # -------------------------------------------------------------------------
    # Code & Developer
    # -------------------------------------------------------------------------
    "github": "https://github.com/search?q=",
    "github-code": "https://github.com/search?type=code&q=",
    "gitlab": "https://gitlab.com/search?search=",
    "bitbucket": "https://bitbucket.org/repo/all?name=",
    "searchcode": "https://searchcode.com/?q=",
    "sourcegraph": "https://sourcegraph.com/search?q=",
    "npm": "https://www.npmjs.com/search?q=",
    "pypi": "https://pypi.org/search/?q=",
    "crates": "https://crates.io/search?q=",  # Rust
    "packagist": "https://packagist.org/?query=",  # PHP
    "rubygems": "https://rubygems.org/search?query=",
    "dockerhub": "https://hub.docker.com/search?q=",
    "stackoverflow": "https://stackoverflow.com/search?q=",
    "gist": "https://gist.github.com/search?q=",
    # -------------------------------------------------------------------------
    # Security & OSINT
    # -------------------------------------------------------------------------
    "shodan": "https://www.shodan.io/search?query=",
    "censys": "https://search.censys.io/search?resource=hosts&q=",
    "zoomeye": "https://www.zoomeye.org/searchResult?q=",
    "fofa": "https://en.fofa.info/result?qbase64=",  # Base64 encoded
    "binaryedge": "https://app.binaryedge.io/services/query?query=",
    "greynoise": "https://viz.greynoise.io/query?gnql=",
    "onyphe": "https://www.onyphe.io/search?q=",
    "hunter": "https://hunter.io/search/",
    "intelx": "https://intelx.io/?s=",
    "leakix": "https://leakix.net/search?scope=leak&q=",
    "pulsedive": "https://pulsedive.com/indicator/?ioc=",
    "threatcrowd": "https://www.threatcrowd.org/searchApi/v2/domain/report/?domain=",
    "virustotal": "https://www.virustotal.com/gui/search/",
    "urlscan": "https://urlscan.io/search/#",
    "crtsh": "https://crt.sh/?q=",  # Certificate transparency
    "dnsdumpster": "https://dnsdumpster.com/?search=",
    "securitytrails": "https://securitytrails.com/domain/",
    "fullhunt": "https://fullhunt.io/search?query=",
    "netlas": "https://app.netlas.io/responses/?q=",
    "publicwww": "https://publicwww.com/websites/",  # Source code search
    "spyonweb": "https://spyonweb.com/",
    # -------------------------------------------------------------------------
    # Social Media
    # -------------------------------------------------------------------------
    "twitter": "https://twitter.com/search?q=",
    "x": "https://twitter.com/search?q=",
    "reddit": "https://www.reddit.com/search/?q=",
    "linkedin": "https://www.linkedin.com/search/results/all/?keywords=",
    "facebook": "https://www.facebook.com/search/top?q=",
    "instagram": "https://www.instagram.com/explore/tags/",
    "tiktok": "https://www.tiktok.com/search?q=",
    "pinterest": "https://www.pinterest.com/search/pins/?q=",
    "tumblr": "https://www.tumblr.com/search/",
    "mastodon": "https://mastodon.social/tags/",
    "bluesky": "https://bsky.app/search?q=",
    "threads": "https://www.threads.net/search?q=",
    "quora": "https://www.quora.com/search?q=",
    "hackernews": "https://hn.algolia.com/?q=",
    "lobsters": "https://lobste.rs/search?q=",
    "discord": "https://disboard.org/search?keyword=",  # Server discovery
    "telegram": "https://t.me/s/",  # Channel search
    # -------------------------------------------------------------------------
    # Media & Video
    # -------------------------------------------------------------------------
    "youtube": "https://www.youtube.com/results?search_query=",
    "vimeo": "https://vimeo.com/search?q=",
    "dailymotion": "https://www.dailymotion.com/search/",
    "twitch": "https://www.twitch.tv/search?term=",
    "rumble": "https://rumble.com/search/video?q=",
    "odysee": "https://odysee.com/$/search?q=",
    "peertube": "https://sepiasearch.org/search?search=",
    "bitchute": "https://www.bitchute.com/search/?query=",
    "google-videos": "https://www.google.com/search?tbm=vid&q=",
    "bing-videos": "https://www.bing.com/videos/search?q=",
    # -------------------------------------------------------------------------
    # Images
    # -------------------------------------------------------------------------
    "google-images": "https://www.google.com/search?tbm=isch&q=",
    "bing-images": "https://www.bing.com/images/search?q=",
    "yandex-images": "https://yandex.com/images/search?text=",
    "flickr": "https://www.flickr.com/search/?text=",
    "unsplash": "https://unsplash.com/s/photos/",
    "pexels": "https://www.pexels.com/search/",
    "pixabay": "https://pixabay.com/images/search/",
    "tineye": "https://tineye.com/search?url=",  # Reverse image
    "imgur": "https://imgur.com/search?q=",
    "giphy": "https://giphy.com/search/",
    "deviantart": "https://www.deviantart.com/search?q=",
    "artstation": "https://www.artstation.com/search?q=",
    "wikimedia": "https://commons.wikimedia.org/w/index.php?search=",
    # -------------------------------------------------------------------------
    # Academic & Research
    # -------------------------------------------------------------------------
    "scholar": "https://scholar.google.com/scholar?q=",
    "semantic-scholar": "https://www.semanticscholar.org/search?q=",
    "pubmed": "https://pubmed.ncbi.nlm.nih.gov/?term=",
    "arxiv": "https://arxiv.org/search/?query=",
    "base": "https://www.base-search.net/Search/Results?lookfor=",
    "core": "https://core.ac.uk/search?q=",
    "scilit": "https://www.scilit.net/articles/search?q=",
    "dimensions": "https://app.dimensions.ai/discover/publication?search_text=",
    "researchgate": "https://www.researchgate.net/search/publication?q=",
    "jstor": "https://www.jstor.org/action/doBasicSearch?Query=",
    "ieee": "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=",
    "acm": "https://dl.acm.org/action/doSearch?AllField=",
    "worldcat": "https://www.worldcat.org/search?q=",
    "openlibrary": "https://openlibrary.org/search?q=",
    "gutenberg": "https://www.gutenberg.org/ebooks/search/?query=",
    # -------------------------------------------------------------------------
    # Documents & Files
    # -------------------------------------------------------------------------
    "scribd": "https://www.scribd.com/search?query=",
    "slideshare": "https://www.slideshare.net/search?q=",
    "issuu": "https://issuu.com/search?q=",
    "pdfdrive": "https://www.pdfdrive.com/search?q=",
    "zlibrary": "https://z-lib.io/s/",
    "libgen": "https://libgen.is/search.php?req=",
    "prezi": "https://prezi.com/explore/search/#search=",
    "google-books": "https://www.google.com/search?tbm=bks&q=",
    "hathitrust": "https://babel.hathitrust.org/cgi/ls?q1=",
    "docplayer": "https://docplayer.net/search/?q=",
    # -------------------------------------------------------------------------
    # News
    # -------------------------------------------------------------------------
    "google-news": "https://news.google.com/search?q=",
    "bing-news": "https://www.bing.com/news/search?q=",
    "yahoo-news": "https://news.search.yahoo.com/search?p=",
    "reuters": "https://www.reuters.com/site-search/?query=",
    "bbc": "https://www.bbc.co.uk/search?q=",
    "cnn": "https://www.cnn.com/search?q=",
    "nytimes": "https://www.nytimes.com/search?query=",
    "guardian": "https://www.theguardian.com/search?q=",
    "apnews": "https://apnews.com/search?q=",
    # -------------------------------------------------------------------------
    # Business & Corporate
    # -------------------------------------------------------------------------
    "crunchbase": "https://www.crunchbase.com/textsearch?q=",
    "opencorporates": "https://opencorporates.com/companies?q=",
    "dnb": "https://www.dnb.com/business-directory/company-search.html?term=",
    "bloomberg": "https://www.bloomberg.com/search?query=",
    "zoominfo": "https://www.zoominfo.com/c/search?q=",
    "glassdoor": "https://www.glassdoor.com/Search/results.htm?keyword=",
    "indeed": "https://www.indeed.com/jobs?q=",
    # -------------------------------------------------------------------------
    # Archives & Wayback
    # -------------------------------------------------------------------------
    "archive": "https://web.archive.org/web/*/",
    "archive-search": "https://web.archive.org/cdx/search/cdx?url=",
    "archive-today": "https://archive.today/search/?q=",
    "cachedview": "https://cachedview.nl/",
    "google-cache": "https://webcache.googleusercontent.com/search?q=cache:",
    # -------------------------------------------------------------------------
    # Pastebins & Leaks
    # -------------------------------------------------------------------------
    "pastebin": "https://pastebin.com/search?q=",
    "paste-search": "https://psbdmp.ws/search/",
    "dehashed": "https://dehashed.com/search?query=",
    "haveibeenpwned": "https://haveibeenpwned.com/unifiedsearch/",
    "leakcheck": "https://leakcheck.io/search?query=",
    "snusbase": "https://snusbase.com/search?q=",
    # -------------------------------------------------------------------------
    # Dark Web (Clearnet interfaces)
    # -------------------------------------------------------------------------
    "ahmia": "https://ahmia.fi/search/?q=",
    "torch": "https://torchsearch.net/search?query=",
    "onionland": "https://onionlandsearchengine.net/search?q=",
    # -------------------------------------------------------------------------
    # Encyclopedias & Knowledge
    # -------------------------------------------------------------------------
    "wikipedia": "https://en.wikipedia.org/w/index.php?search=",
    "wikidata": "https://www.wikidata.org/w/index.php?search=",
    "wikihow": "https://www.wikihow.com/wikiHowTo?search=",
    "britannica": "https://www.britannica.com/search?query=",
    "wolfram": "https://www.wolframalpha.com/input?i=",
    # -------------------------------------------------------------------------
    # Maps & Geolocation
    # -------------------------------------------------------------------------
    "google-maps": "https://www.google.com/maps/search/",
    "openstreetmap": "https://www.openstreetmap.org/search?query=",
    "bing-maps": "https://www.bing.com/maps?q=",
    "yandex-maps": "https://yandex.com/maps/?text=",
    # -------------------------------------------------------------------------
    # Transportation & Tracking
    # -------------------------------------------------------------------------
    "flightradar": "https://www.flightradar24.com/",
    "flightaware": "https://flightaware.com/live/flight/",
    "marinetraffic": "https://www.marinetraffic.com/en/ais/details/ships/",
    "vesselfinder": "https://www.vesselfinder.com/?name=",
    # -------------------------------------------------------------------------
    # Government & Legal
    # -------------------------------------------------------------------------
    "courtlistener": "https://www.courtlistener.com/?q=",
    "pacer": "https://pcl.uscourts.gov/pcl/pages/search/results.xhtml?q=",
    "sec-edgar": "https://www.sec.gov/cgi-bin/srch-ia?text=",
    "regulations-gov": "https://www.regulations.gov/search?filter=",
    "offshoreleaks": "https://offshoreleaks.icij.org/search?q=",
    "aleph-occrp": "https://aleph.occrp.org/search?q=",
    "littlesis": "https://littlesis.org/search?q=",
    "wikileaks": "https://search.wikileaks.org/?q=",
    # -------------------------------------------------------------------------
    # E-Commerce & Products
    # -------------------------------------------------------------------------
    "amazon": "https://www.amazon.com/s?k=",
    "ebay": "https://www.ebay.com/sch/i.html?_nkw=",
    "aliexpress": "https://www.aliexpress.com/wholesale?SearchText=",
    "etsy": "https://www.etsy.com/search?q=",
    "producthunt": "https://www.producthunt.com/search?q=",
    # -------------------------------------------------------------------------
    # Miscellaneous
    # -------------------------------------------------------------------------
    "whois": "https://who.is/whois/",
    "domaintools": "https://whois.domaintools.com/",
    "builtwith": "https://builtwith.com/",
    "wappalyzer": "https://www.wappalyzer.com/lookup/",
    "archive-org": "https://archive.org/search?query=",
    "internetarchive": "https://archive.org/search?query=",
    "snopes": "https://www.snopes.com/?s=",
    "factcheck": "https://www.factcheck.org/?s=",
}


def parse_dork_file(filepath, variables=None, _included_files=None):
    """
    Parse a .dork file. Dead simple format:

    - Lines starting with # are comments
    - Inline comments start with # after whitespace
    - Empty lines are ignored
    - @engine sets default engine for following queries
    - @var NAME = value creates a variable
    - @include path/to/file.dork includes another file
    - Everything else is a query
    - ${NAME} or $NAME in queries gets replaced with variables
    """
    if variables is None:
        variables = {}
    if _included_files is None:
        _included_files = set()

    queries = []
    current_engine = "google"

    path = Path(filepath).resolve()

    # Prevent circular includes
    if path in _included_files:
        return queries
    _included_files.add(path)

    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    base_dir = path.parent

    def strip_inline_comment(text):
        # Strip inline comments that start with # after whitespace, outside quotes.
        in_single = False
        in_double = False
        for i, ch in enumerate(text):
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "#" and not in_single and not in_double:
                if i == 0 or text[i - 1].isspace():
                    return text[:i].rstrip()
        return text

    for line_num, line in enumerate(content.splitlines(), 1):
        line = line.rstrip()
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Strip inline comments before processing
        line = strip_inline_comment(line)
        if not line:
            continue
        original_line = line

        # Engine directive: @engine google
        if line.startswith("@engine"):
            parts = line.split(None, 1)
            if len(parts) > 1:
                eng = parts[1].lower()
                if eng in ENGINES:
                    current_engine = eng
                else:
                    print(
                        f"Warning {path.name}:{line_num}: Unknown engine '{eng}', using google",
                        file=sys.stderr,
                    )
            continue

        # Variable definition: @var TARGET = example.com
        if line.startswith("@var"):
            match = re.match(r"@var\s+(\w+)\s*=\s*(.+)", line)
            if match:
                var_name = match.group(1)
                # Only set if not already overridden from CLI
                if var_name not in variables:
                    variables[var_name] = match.group(2).strip()
            continue

        # Include directive: @include other.dork
        if line.startswith("@include"):
            parts = line.split(None, 1)
            if len(parts) > 1:
                include_path = parts[1].strip().strip('"').strip("'")
                # Resolve relative to current file's directory
                if not Path(include_path).is_absolute():
                    include_path = base_dir / include_path

                included_queries = parse_dork_file(
                    include_path, variables, _included_files
                )
                queries.extend(included_queries)
            continue

        # It's a query - expand variables
        query = line
        for name, value in variables.items():
            query = query.replace(f"${{{name}}}", value)
            query = query.replace(f"${name}", value)

        # Check for unexpanded variables
        unexpanded = re.findall(r"\$\{?(\w+)\}?", query)
        if unexpanded:
            # Filter out false positives (like $1 in regex)
            real_unexpanded = [v for v in unexpanded if not v.isdigit()]
            if real_unexpanded:
                print(
                    f"Warning {path.name}:{line_num}: Undefined variable(s): {', '.join(real_unexpanded)}",
                    file=sys.stderr,
                )

        queries.append(
            {
                "query": query,
                "engine": current_engine,
                "line": line_num,
                "file": path.name,
                "original": original_line.strip(),
            }
        )

    return queries


def build_url(query, engine):
    """Build the search URL."""
    base = ENGINES.get(engine, ENGINES["google"])

    # Some engines need special handling
    if engine == "archive":
        # Archive.org uses the URL directly, not encoded
        return base + query
    if engine == "fofa":
        import base64

        encoded = base64.b64encode(query.encode("utf-8")).decode("ascii")
        return base + encoded
    if engine in {"hunter"}:
        # Hunter expects the query as a path segment.
        return base + urllib.parse.quote(query, safe="")

    return base + urllib.parse.quote(query)


def run(
    filepath,
    limit=None,
    preview=False,
    engine_override=None,
    delay=0.5,
    output_file=None,
    urls_only=False,
    variables=None,
):
    """Execute the queries."""
    queries = parse_dork_file(filepath, variables)

    if not queries:
        if not urls_only:
            print("No queries found in file.", file=sys.stderr)
        return

    if limit:
        queries = queries[:limit]

    # Collect URLs for output
    urls = []
    for q in queries:
        eng = engine_override or q["engine"]
        urls.append({**q, "engine": eng, "url": build_url(q["query"], eng)})

    # URLs-only mode (for piping)
    if urls_only:
        for u in urls:
            print(u["url"])
        return

    # Output to file
    if output_file:
        output_path = Path(output_file)
        with output_path.open("w", encoding="utf-8") as f:
            for u in urls:
                f.write(f"{u['url']}\n")
        print(f"Wrote {len(urls)} URLs to {output_file}")
        if not preview:
            # Still open in browser unless preview mode
            for i, u in enumerate(urls):
                webbrowser.open(u["url"])
                if i < len(urls) - 1:
                    time.sleep(delay)
            print(f"Opened {len(urls)} searches in your browser.")
        return

    # Normal mode - display and optionally open
    print(f"\n  DorkScript: {Path(filepath).name}")
    print(f"  {'=' * 60}")

    # Show variables if any were used
    if variables:
        print(f"  Variables: {', '.join(f'{k}={v}' for k, v in variables.items())}")

    print(f"  Queries: {len(urls)}\n")

    for i, u in enumerate(urls, 1):
        # Show query
        display_query = u["query"] if len(u["query"]) < 55 else u["query"][:52] + "..."
        print(f"  [{i}] {display_query}")
        print(f"      @{u['engine']}")

        if preview:
            # Show full URL in preview mode
            print(f"      {u['url']}")

        print()

        if not preview:
            webbrowser.open(u["url"])
            if i < len(urls):
                time.sleep(delay)

    if preview:
        print("  (Preview mode - no browsers opened)")
    else:
        print(f"  Opened {len(urls)} searches in your browser.")
    print()


def show_engines():
    """List available search engines."""
    print(f"\n  DorkScript v{__version__} - {len(ENGINES)} Search Engines")
    print("  " + "=" * 60)

    # Group by category
    categories = {
        "General Search": [
            "google",
            "bing",
            "ddg",
            "yandex",
            "baidu",
            "yahoo",
            "brave",
            "startpage",
            "qwant",
            "ecosia",
            "mojeek",
            "swisscows",
            "searx",
            "metager",
            "dogpile",
            "ask",
            "millionshort",
            "naver",
            "sogou",
        ],
        "Code & Dev": [
            "github",
            "github-code",
            "gitlab",
            "searchcode",
            "sourcegraph",
            "npm",
            "pypi",
            "dockerhub",
            "stackoverflow",
            "gist",
        ],
        "Security & OSINT": [
            "shodan",
            "censys",
            "zoomeye",
            "binaryedge",
            "greynoise",
            "hunter",
            "intelx",
            "leakix",
            "virustotal",
            "urlscan",
            "crtsh",
            "publicwww",
            "spyonweb",
            "fullhunt",
            "netlas",
        ],
        "Social Media": [
            "twitter",
            "reddit",
            "linkedin",
            "facebook",
            "instagram",
            "tiktok",
            "mastodon",
            "bluesky",
            "hackernews",
            "quora",
        ],
        "Video & Media": [
            "youtube",
            "vimeo",
            "dailymotion",
            "twitch",
            "rumble",
            "odysee",
            "peertube",
            "google-videos",
        ],
        "Images": [
            "google-images",
            "bing-images",
            "yandex-images",
            "flickr",
            "unsplash",
            "pexels",
            "tineye",
            "deviantart",
        ],
        "Academic": [
            "scholar",
            "semantic-scholar",
            "pubmed",
            "arxiv",
            "base",
            "core",
            "researchgate",
            "jstor",
            "worldcat",
            "openlibrary",
        ],
        "Documents": [
            "scribd",
            "slideshare",
            "issuu",
            "pdfdrive",
            "google-books",
            "hathitrust",
            "libgen",
        ],
        "News": [
            "google-news",
            "bing-news",
            "reuters",
            "bbc",
            "apnews",
        ],
        "Business": [
            "crunchbase",
            "opencorporates",
            "bloomberg",
            "glassdoor",
        ],
        "Archives": [
            "archive",
            "archive-today",
            "google-cache",
            "archive-org",
        ],
        "Leaks & Pastebins": [
            "pastebin",
            "paste-search",
            "dehashed",
            "haveibeenpwned",
        ],
        "Dark Web": [
            "ahmia",
            "torch",
            "onionland",
        ],
        "Knowledge": [
            "wikipedia",
            "wikidata",
            "wikihow",
            "wolfram",
            "britannica",
        ],
        "Maps": [
            "google-maps",
            "openstreetmap",
            "bing-maps",
        ],
        "Legal & Gov": [
            "courtlistener",
            "offshoreleaks",
            "aleph-occrp",
            "wikileaks",
        ],
        "Google Operators": [
            "google-site",
            "google-filetype",
            "google-intitle",
            "google-inurl",
            "google-intext",
            "google-related",
            "google-define",
            "google-weather",
            "google-stocks",
            "google-movie",
            "google-recent",
            "google-verbatim",
        ],
        "Bing/DDG Operators": [
            "bing-site",
            "bing-filetype",
            "bing-intitle",
            "ddg-site",
            "ddg-filetype",
            "ddg-intitle",
        ],
    }

    for category, engines in categories.items():
        available = [e for e in engines if e in ENGINES]
        if available:
            print(f"\n  {category}:")
            for eng in available:
                print(f"    {eng}")
    print()


def show_help():
    """Show usage."""
    help_text = f"""
  DorkScript v{__version__} - Version control for search strategies
  ================================================================
        .-.
       (o o)  dorkscript
       | O \\
        \\   \\
         `~~~'

  Usage:
      python dork.py <file.dork> [options] [VAR=value ...]
      python -m dork <file.dork> [options] [VAR=value ...]
      dork <file.dork> [options] [VAR=value ...]

  Options:
      -n, --limit N     Only run first N queries
      -p, --preview     Show queries and URLs without opening browser
      -e, --engine X    Override engine for all queries
      -d, --delay N     Seconds between queries (default: 0.5)
      -o, --output F    Write URLs to file F (still opens browser)
      -u, --urls        Output only URLs (for piping, no browser)
      --engines         List all available search engines
      --selftest        Run built-in self tests
      -h, --help        Show this help
      -v, --version     Show version

  Variable Override:
      VAR=value         Override @var defined in the file
                        Example: python dork.py recon.dork TARGET=real-site.com

  .dork File Format:
      # This is a comment
      site:example.com "sensitive"       # Inline comment after whitespace

      @engine github                     # Switch engine for following queries
      language:python oauth              # Uses github

      @engine google                     # Back to google
      @var TARGET = example.com          # Define variable
      site:$TARGET filetype:pdf          # Use variable

      @include common/recon-base.dork    # Include another file

  Examples:
      python dork.py recon.dork                       # Run all queries
      python dork.py recon.dork -n 5 -p               # Preview first 5
      python dork.py recon.dork TARGET=real.com       # Override variable
      python dork.py recon.dork -u > urls.txt         # Export URLs
      python dork.py recon.dork -u | xargs -I{{}} curl {{}}  # Pipe URLs
      python dork.py recon.dork -o results.txt -p     # Save URLs, don't open

  Engines:
      google, bing, ddg, github, shodan, youtube, reddit, twitter,
      linkedin, archive, censys, virustotal, urlscan, yandex, and more.
      Run with --engines to see full list.

  Philosophy:
      - No install required (just Python 3)
      - No dependencies (stdlib only)
      - No scraping (opens in YOUR browser)
      - No legal gray areas
      - Version control your searches with git
      - Share .dork files like code
"""
    print(help_text)


def selftest():
    """Run a small built-in test suite."""
    import base64
    import tempfile

    # Inline comments
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.dork"
        path.write_text('site:example.com "sensitive"  # comment\n', encoding="utf-8")
        queries = parse_dork_file(path)
        if len(queries) != 1 or queries[0]["query"] != 'site:example.com "sensitive"':
            print("Selftest failed: inline comments", file=sys.stderr)
            return 1

    # Include variables propagate
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        included = tmp_path / "included.dork"
        included.write_text("@var TARGET = included.com\n", encoding="utf-8")
        parent = tmp_path / "parent.dork"
        parent.write_text("@include included.dork\nsite:$TARGET\n", encoding="utf-8")
        queries = parse_dork_file(parent)
        if len(queries) != 1 or queries[0]["query"] != "site:included.com":
            print("Selftest failed: include variables", file=sys.stderr)
            return 1

    # FOFA base64
    query = "test"
    expected = base64.b64encode(query.encode("utf-8")).decode("ascii")
    url = build_url(query, "fofa")
    if url != ENGINES["fofa"] + expected:
        print("Selftest failed: fofa base64", file=sys.stderr)
        return 1

    # Hunter path
    query = "example.com"
    url = build_url(query, "hunter")
    if url != ENGINES["hunter"] + "example.com":
        print("Selftest failed: hunter path", file=sys.stderr)
        return 1

    print("Selftest ok.")
    return 0


def main():
    args = sys.argv[1:]

    if not args or "-h" in args or "--help" in args:
        show_help()
        sys.exit(0)

    if "-v" in args or "--version" in args:
        print(f"DorkScript v{__version__}")
        sys.exit(0)

    if "--selftest" in args:
        sys.exit(selftest())

    if "--engines" in args:
        show_engines()
        sys.exit(0)

    # Parse arguments (keeping it simple, no argparse needed)
    filepath = None
    limit = None
    preview = False
    engine = None
    delay = 0.5
    output_file = None
    urls_only = False
    variables = {}

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ("-n", "--limit"):
            if i + 1 >= len(args):
                print("Error: -n/--limit requires a value", file=sys.stderr)
                sys.exit(1)
            try:
                limit = int(args[i + 1])
            except ValueError:
                print("Error: -n/--limit must be an integer", file=sys.stderr)
                sys.exit(1)
            i += 2
        elif arg in ("-p", "--preview"):
            preview = True
            i += 1
        elif arg in ("-e", "--engine"):
            if i + 1 >= len(args):
                print("Error: -e/--engine requires a value", file=sys.stderr)
                sys.exit(1)
            engine = args[i + 1].lower()
            i += 2
        elif arg in ("-d", "--delay"):
            if i + 1 >= len(args):
                print("Error: -d/--delay requires a value", file=sys.stderr)
                sys.exit(1)
            try:
                delay = float(args[i + 1])
            except ValueError:
                print("Error: -d/--delay must be a number", file=sys.stderr)
                sys.exit(1)
            i += 2
        elif arg in ("-o", "--output"):
            if i + 1 >= len(args):
                print("Error: -o/--output requires a value", file=sys.stderr)
                sys.exit(1)
            output_file = args[i + 1]
            i += 2
        elif arg in ("-u", "--urls"):
            urls_only = True
            i += 1
        elif "=" in arg and not arg.startswith("-"):
            # Variable override: VAR=value
            var_name, var_value = arg.split("=", 1)
            variables[var_name] = var_value
            i += 1
        elif not arg.startswith("-"):
            filepath = arg
            i += 1
        else:
            print(f"Unknown option: {arg}", file=sys.stderr)
            sys.exit(1)

    if not filepath:
        print("Error: No .dork file specified", file=sys.stderr)
        show_help()
        sys.exit(1)
    if engine and engine not in ENGINES:
        print(f"Error: Unknown engine '{engine}'", file=sys.stderr)
        print("Run with --engines to see available options.", file=sys.stderr)
        sys.exit(1)

    run(
        filepath,
        limit=limit,
        preview=preview,
        engine_override=engine,
        delay=delay,
        output_file=output_file,
        urls_only=urls_only,
        variables=variables if variables else None,
    )


if __name__ == "__main__":
    main()
