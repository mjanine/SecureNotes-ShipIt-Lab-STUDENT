"""Shared pytest fixtures for the SecureNotes suite.

Three kinds of tests live here:
  - test_api / test_security  -> hit the running app (Weeks 13-15, carried over)
  - test_accessibility        -> parse the front-end HTML/CSS (Week 16)
  - test_performance          -> parse the front-end HTML     (Week 16)
  - test_pipeline             -> parse the CI workflow YAML    (Week 17)
"""
import os
import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from app.main import app, reset_database

# --- paths ----------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(__file__))
STATIC = os.path.join(ROOT, "app", "static")
INDEX_HTML = os.path.join(STATIC, "index.html")
STYLES_CSS = os.path.join(STATIC, "styles.css")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "ci.yml")


# --- API fixtures (Weeks 13-15) -------------------------------------------
@pytest.fixture
def client():
    """A fresh, seeded database and a TestClient for each test."""
    reset_database()
    return TestClient(app, raise_server_exceptions=False)


def login(client, username, password):
    res = client.post("/login", json={"username": username, "password": password})
    if res.status_code != 200:
        return None
    return res.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# --- front-end fixtures (Week 16) -----------------------------------------
@pytest.fixture
def html_text():
    with open(INDEX_HTML, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def soup(html_text):
    return BeautifulSoup(html_text, "html.parser")


@pytest.fixture
def css_text():
    with open(STYLES_CSS, encoding="utf-8") as f:
        return f.read()


# --- workflow fixture (Week 17) -------------------------------------------
@pytest.fixture
def workflow_text():
    with open(WORKFLOW, encoding="utf-8") as f:
        return f.read()
