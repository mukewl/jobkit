"""Compile a CV template to PDF and refuse to hand back one that ran long.

    python cv/build.py --template cv/templates/master_cv.tex
    python cv/build.py --template cv/templates/master_cv.html --out out/cv.pdf
    python cv/build.py --template cv/my_cv.tex --max-pages 2

Two engines, picked from the file extension:

  .tex   -> pdflatex. Page count read from the LaTeX log.
  .html  -> headless Chromium via Playwright. Page count read from the PDF.

Exits non-zero when the result exceeds --max-pages, so an agent tailoring a CV
finds out it overflowed instead of quietly shipping two pages.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


class BuildError(RuntimeError):
    pass


# ---------------------------------------------------------------- page counting

def count_pdf_pages(pdf: Path) -> int:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf)).pages)
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader  # type: ignore
        return len(PdfReader(str(pdf)).pages)
    except ImportError:
        pass
    # last resort: count page objects in the raw file
    blob = pdf.read_bytes()
    n = len(re.findall(rb"/Type\s*/Page[^s]", blob))
    if n == 0:
        raise BuildError(
            "Could not determine the page count. Install pypdf:  pip install pypdf"
        )
    return n


# ---------------------------------------------------------------- engines

def build_latex(template: Path, out: Path) -> int:
    if not shutil.which("pdflatex"):
        raise BuildError(
            "pdflatex not found on PATH.\n"
            "  Windows: winget install MiKTeX.MiKTeX\n"
            "  macOS:   brew install --cask basictex\n"
            "  Linux:   sudo apt install texlive-latex-recommended texlive-fonts-recommended\n"
            "Then reopen your terminal. Or use an .html template instead - no LaTeX needed."
        )
    workdir = out.parent
    workdir.mkdir(parents=True, exist_ok=True)
    staged = workdir / template.name
    if staged.resolve() != template.resolve():
        shutil.copy(template, staged)

    proc = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", staged.name],
        cwd=workdir, capture_output=True, text=True,
    )
    log = (workdir / f"{staged.stem}.log")
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else proc.stdout

    m = re.search(r"Output written on .+? \((\d+) pages?", log_text)
    if not m:
        missing = re.search(r"LaTeX Error: File `([^']+)' not found", log_text)
        if missing:
            raise BuildError(
                f"LaTeX package missing: {missing.group(1)}\n"
                "MiKTeX ships a minimal set. Turn on automatic package installation:\n"
                "  initexmf --set-config-value=\"[MPM]AutoInstall=1\"\n"
                "then run this again."
            )
        tail = "\n".join(log_text.strip().splitlines()[-15:])
        raise BuildError(f"pdflatex produced no PDF.\n--- end of log ---\n{tail}")

    produced = workdir / f"{staged.stem}.pdf"
    if produced.resolve() != out.resolve():
        shutil.move(str(produced), out)
    for ext in (".aux", ".log", ".out"):
        (workdir / f"{staged.stem}{ext}").unlink(missing_ok=True)
    if staged.resolve() != template.resolve():
        staged.unlink(missing_ok=True)
    return int(m.group(1))


def build_html(template: Path, out: Path) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise BuildError(
            "Playwright not installed. Either:\n"
            "  pip install playwright && python -m playwright install chromium\n"
            "or use a .tex template with a LaTeX distribution instead."
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(template.resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(out), format="A4", print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()
    return count_pdf_pages(out)


ENGINES = {".tex": build_latex, ".html": build_html, ".htm": build_html}


# ---------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description="Build a CV template into a page-checked PDF.")
    ap.add_argument("--template", required=True, help=".tex or .html file")
    ap.add_argument("--out", help="output PDF (default: alongside the template)")
    ap.add_argument("--max-pages", type=int, default=1)
    args = ap.parse_args()

    template = Path(args.template)
    if not template.exists():
        print(f"error: template not found: {template}", file=sys.stderr)
        return 2

    engine = ENGINES.get(template.suffix.lower())
    if engine is None:
        print(f"error: don't know how to build '{template.suffix}'. "
              f"Use one of: {', '.join(sorted(ENGINES))}", file=sys.stderr)
        return 2

    out = Path(args.out) if args.out else template.with_suffix(".pdf")
    try:
        pages = engine(template, out)
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if pages > args.max_pages:
        print(f"error: {out.name} is {pages} pages, limit is {args.max_pages}.\n"
              "       Cut content and build again - do not hand this over as is.",
              file=sys.stderr)
        return 1

    print(f"OK  {out}  ({pages} page{'s' if pages != 1 else ''})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
