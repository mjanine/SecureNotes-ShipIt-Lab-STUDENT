// SecureNotes front end — talks to the FastAPI backend.
// Loaded with `defer`, so this runs after the HTML is parsed. No framework,
// on purpose: Part A is about the HTML/CSS, not the JavaScript.

const API = ""; // same origin — the API is served next to this page

const form = document.getElementById("login-form");
const statusEl = document.getElementById("status");
const noteList = document.getElementById("note-list");

let token = null;

function setStatus(msg) { statusEl.textContent = msg; }

async function loadNotes() {
  const res = await fetch(API + "/notes", {
    headers: { Authorization: "Bearer " + token },
  });
  if (!res.ok) { setStatus("Could not load notes."); return; }
  const notes = await res.json();
  noteList.innerHTML = "";
  if (notes.length === 0) {
    const li = document.createElement("li");
    li.className = "empty";
    li.textContent = "No notes yet.";
    noteList.appendChild(li);
    return;
  }
  for (const n of notes) {
    const li = document.createElement("li");
    li.textContent = n.title + " — " + n.body;
    noteList.appendChild(li);
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  setStatus("Logging in…");
  const res = await fetch(API + "/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: document.getElementById("username").value,
      password: document.getElementById("password").value,
    }),
  });
  if (!res.ok) { setStatus("Invalid username or password."); return; }
  token = (await res.json()).access_token;
  setStatus("Logged in. Loading your notes…");
  loadNotes();
});
