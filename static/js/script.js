const $ = (id) => document.getElementById(id);
const JSON_HEADERS = { "Content-Type": "application/json" };

let sessionId = null;
let username = "";
let lastId = 0;          // id of the last message we have displayed
let polling = false;
let pollTimer = null;

/* ---------- Connect ---------- */
$("connect-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = $("connect-btn");
  $("connect-error").textContent = "";
  btn.disabled = true;
  btn.textContent = "Connecting...";

  try {
    const res = await fetch("/api/connect", {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({
        username: $("username").value,
        host: $("host").value,
        port: $("port").value,
      }),
    });
    const data = await res.json();

    if (!res.ok) {
      $("connect-error").textContent = data.error;
      return;
    }

    sessionId = data.session_id;
    username = data.username;
    lastId = 0;
    $("messages").innerHTML = "";
    $("profile-name").textContent = username;
    $("avatar").textContent = username[0].toUpperCase();
    $("server-address").textContent = `${data.host}:${data.port}`;
    setStatus(true);
    $("connect-screen").classList.add("hidden");
    $("message-input").focus();
    poll();
  } catch (err) {
    $("connect-error").textContent = "Cannot reach the Flask app. Is app.py running?";
  } finally {
    btn.disabled = false;
    btn.textContent = "Connect";
  }
});

/* ---------- Receive messages (polling) ---------- */
async function poll() {
  if (polling || !sessionId) return;
  polling = true;
  clearTimeout(pollTimer);
  const sid = sessionId;
  let keepGoing = true;

  try {
    const res = await fetch(`/api/messages?session_id=${sid}&since=${lastId}`);
    const data = await res.json();
    if (sid !== sessionId) { polling = false; return; }  // user left meanwhile

    if (!res.ok) {
      addSystem("Session expired. Please reconnect.", true);
      setStatus(false);
      keepGoing = false;
    } else {
      data.messages.forEach(addMessage);
      if (!data.connected) {
        setStatus(false);
        keepGoing = false;
      }
    }
  } catch (err) {
    addSystem("Lost connection to the web app.", true);
    setStatus(false);
    keepGoing = false;
  }

  polling = false;
  if (keepGoing) pollTimer = setTimeout(poll, 800);
}

/* ---------- Send ---------- */
$("message-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("message-input");
  const text = input.value.trim();
  if (!text || !sessionId) return;
  input.value = "";

  try {
    const res = await fetch("/api/send", {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({ session_id: sessionId, text }),
    });
    if (!res.ok) {
      const data = await res.json();
      addSystem(data.error, true);
      setStatus(false);
      return;
    }
    poll();  // fetch the echo from the server right away
  } catch (err) {
    addSystem("Could not send the message.", true);
    setStatus(false);
  }
});

/* ---------- Disconnect ---------- */
$("leave-btn").addEventListener("click", async () => {
  if (sessionId) {
    try {
      await fetch("/api/disconnect", {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch (err) { /* ignore: we are leaving anyway */ }
  }
  sessionId = null;
  clearTimeout(pollTimer);
  polling = false;
  $("sidebar").classList.remove("open");
  $("connect-screen").classList.remove("hidden");
});

/* ---------- Drawing messages ---------- */
function addMessage(m) {
  lastId = m.id;

  if (m.kind !== "MSG") {              // join / leave / server notices
    addSystem(m.text);
    return;
  }

  const mine = m.sender === username;
  const wrap = document.createElement("div");
  wrap.className = "msg " + (mine ? "sent" : "received");

  const meta = document.createElement("div");
  meta.className = "meta";
  const name = document.createElement("b");
  name.textContent = mine ? "You" : m.sender;
  meta.append(name, ` · ${m.time}`);

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = m.text;         // textContent = safe from HTML injection

  wrap.append(meta, bubble);
  appendToChat(wrap);
}

function addSystem(text, warn = false) {
  const div = document.createElement("div");
  div.className = "system" + (warn ? " warn" : "");
  div.textContent = text;
  appendToChat(div);
}

function appendToChat(element) {
  const box = $("messages");
  const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 120;
  box.appendChild(element);
  if (nearBottom) box.scrollTop = box.scrollHeight;
}

/* ---------- Status ---------- */
function setStatus(online) {
  $("status-dot").classList.toggle("online", online);
  $("status-text").textContent = online ? "Connected" : "Disconnected";
  $("message-input").disabled = !online;
  $("send-btn").disabled = !online;
  $("leave-btn").textContent = online ? "Disconnect" : "Back to login";
}

/* ---------- Mobile sidebar ---------- */
$("menu-btn").addEventListener("click", () => $("sidebar").classList.toggle("open"));
$("chat").addEventListener("click", () => $("sidebar").classList.remove("open"));