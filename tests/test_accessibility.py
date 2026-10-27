"""Week 16 — Accessibility (WCAG) checks on the SecureNotes front end.

Each test encodes one WCAG success criterion as a rule a machine can check.
Automated tests catch the mechanical failures (missing alt, no label, bad
contrast); a human still checks the things a machine can't feel. Both matter.

INSTRUCTOR note: all of these pass against the solved index.html / styles.css.
"""
import re
from bs4 import BeautifulSoup


def _interactive_inputs(soup):
    """Inputs that need a label (skip hidden/submit/button/reset types)."""
    out = []
    for inp in soup.find_all("input"):
        t = (inp.get("type") or "text").lower()
        if t in ("hidden", "submit", "button", "reset"):
            continue
        out.append(inp)
    return out


# --- WCAG 3.1.1 Language of Page ------------------------------------------
def test_html_has_lang(soup):
    html = soup.find("html")
    assert html is not None and html.get("lang"), \
        "The <html> tag needs a lang attribute, e.g. <html lang=\"en\">."


# --- WCAG 2.4.2 Page Titled -----------------------------------------------
def test_page_has_title(soup):
    title = soup.find("title")
    assert title is not None and title.get_text(strip=True), \
        "The page needs a non-empty <title>."


# --- WCAG 1.3.1 / 2.4.6 Headings ------------------------------------------
def test_exactly_one_h1(soup):
    assert len(soup.find_all("h1")) == 1, \
        "There must be exactly one <h1> — the page's main heading."


def test_headings_do_not_skip_levels(soup):
    levels = [int(h.name[1]) for h in soup.find_all(re.compile(r"^h[1-6]$"))]
    assert levels, "The page has no headings at all."
    assert levels[0] == 1, "The first heading should be the <h1>."
    for prev, cur in zip(levels, levels[1:]):
        assert cur <= prev + 1, \
            f"Heading jumps from h{prev} to h{cur} — don't skip levels."


# --- WCAG 1.1.1 Non-text Content ------------------------------------------
def test_every_image_has_alt(soup):
    for img in soup.find_all("img"):
        assert img.has_attr("alt"), \
            f"<img src=\"{img.get('src')}\"> is missing an alt attribute."


# --- WCAG 1.3.1 / 3.3.2 Labels --------------------------------------------
def test_every_input_has_a_label(soup):
    label_fors = {l.get("for") for l in soup.find_all("label") if l.get("for")}
    for inp in _interactive_inputs(soup):
        iid = inp.get("id")
        assert iid and iid in label_fors, \
            f"Input name=\"{inp.get('name')}\" needs a <label for=\"{iid}\">."


# --- WCAG 4.1.2 Name, Role, Value -----------------------------------------
def test_no_clickable_divs(soup):
    for tag in soup.find_all(["div", "span"]):
        assert not tag.has_attr("onclick"), \
            "Use a real <button>, not a <div>/<span> with onclick."


def test_buttons_have_text(soup):
    for btn in soup.find_all("button"):
        has_text = btn.get_text(strip=True)
        has_label = btn.get("aria-label")
        assert has_text or has_label, "A <button> has no discernible text."


def test_links_have_href_and_text(soup):
    for a in soup.find_all("a"):
        assert a.get("href"), "Every <a> needs an href."
        assert a.get_text(strip=True) or a.get("aria-label"), \
            "A link has no discernible text."


# --- WCAG 1.3.1 Landmarks -------------------------------------------------
def test_has_main_landmark(soup):
    assert soup.find("main") is not None, \
        "The page needs a <main> landmark around its primary content."


# --- WCAG 2.4.3 Focus Order -----------------------------------------------
def test_no_positive_tabindex(soup):
    for tag in soup.find_all(attrs={"tabindex": True}):
        assert int(tag.get("tabindex")) <= 0, \
            "Avoid positive tabindex values — they break natural focus order."


# --- WCAG 1.4.3 Contrast (Minimum) ----------------------------------------
def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rel_luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(hex1, hex2):
    l1 = _rel_luminance(_hex_to_rgb(hex1))
    l2 = _rel_luminance(_hex_to_rgb(hex2))
    lo, hi = sorted((l1, l2))
    return (hi + 0.05) / (lo + 0.05)

def _var(css, name):
    m = re.search(rf"{name}\s*:\s*(#[0-9A-Fa-f]{{6}})", css)
    assert m, f"Expected a {name} color token in styles.css."
    return m.group(1)

def test_body_text_contrast_is_AA(css_text):
    ratio = contrast_ratio(_var(css_text, "--ink"), _var(css_text, "--surface"))
    assert ratio >= 4.5, \
        f"Body text contrast is {ratio:.1f}:1 — WCAG AA needs at least 4.5:1."

def test_button_text_contrast_is_AA(css_text):
    # buttons use white text on --brand
    ratio = contrast_ratio("#FFFFFF", _var(css_text, "--brand"))
    assert ratio >= 4.5, \
        f"Button text contrast is {ratio:.1f}:1 — white on --brand needs 4.5:1."
