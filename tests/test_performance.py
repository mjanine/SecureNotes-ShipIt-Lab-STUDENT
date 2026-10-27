"""Week 16 — Performance checks on the SecureNotes front end.

These are the front-end habits that keep a page fast and stop it from
jumping around as it loads. All are checkable straight from the HTML.

INSTRUCTOR note: all of these pass against the solved index.html.
"""


# --- No render-blocking scripts -------------------------------------------
def test_scripts_are_deferred_or_async(soup):
    for s in soup.find_all("script"):
        if not s.get("src"):
            continue  # inline config scripts are fine
        assert s.has_attr("defer") or s.has_attr("async"), \
            f"<script src=\"{s.get('src')}\"> should use defer (or async) " \
            "so it doesn't block the first paint."


# --- Stylesheet in the head -----------------------------------------------
def test_stylesheet_linked_in_head(soup):
    head = soup.find("head")
    assert head is not None
    links = [l for l in head.find_all("link")
             if "stylesheet" in (l.get("rel") or [])]
    assert links, "Link the stylesheet in <head> so styles are ready at paint."


# --- Reserve space for images (Cumulative Layout Shift) -------------------
def test_images_have_width_and_height(soup):
    for img in soup.find_all("img"):
        assert img.get("width") and img.get("height"), \
            f"<img src=\"{img.get('src')}\"> needs width and height so the " \
            "browser reserves space and the page doesn't jump (CLS)."


# --- Lazy-load below-the-fold images --------------------------------------
def test_content_images_are_lazy_loaded(soup):
    main = soup.find("main")
    assert main is not None, "No <main> landmark found."
    imgs = main.find_all("img")
    assert imgs, "Expected at least one image inside <main>."
    for img in imgs:
        assert img.get("loading") == "lazy", \
            f"<img src=\"{img.get('src')}\"> inside <main> should use " \
            "loading=\"lazy\" (it's below the fold)."


# --- Responsive viewport --------------------------------------------------
def test_has_responsive_viewport_meta(soup):
    metas = soup.find_all("meta", attrs={"name": "viewport"})
    assert metas, "Add a <meta name=\"viewport\"> so the page is mobile-ready."
    assert any("width=device-width" in (m.get("content") or "") for m in metas), \
        "The viewport meta should include width=device-width."
