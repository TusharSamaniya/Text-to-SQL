import { useState } from "react";
import "./App.css";

// The URL of our Flask backend (Vite proxies /api -> 127.0.0.1:5000).
const API_URL = "/api/ask";

// A single message in the chat.
function Message({ msg, onChoice }) {
  // --- A multiple-choice clarification dialog ---
  if (msg.type === "clarify") {
    return (
      <div className="msg clarify">
        <div className="balloon">
          <p className="clarify-label">{msg.label}</p>
          {msg.options.map((opt, i) => (
            <button key={i} className="option" onClick={() => onChoice(i, opt)}>
              {opt}
            </button>
          ))}
        </div>
      </div>
    );
  }

  // --- An answer: table of rows (or "no data") + the generated SQL ---
  if (msg.type === "answer") {
    const headers = msg.headers || [];
    const hasRows = msg.rows && msg.rows.length > 0;
    return (
      <div className="msg answer">
        <div className="balloon">
          {hasRows ? (
            <table className="results">
              {headers.length > 0 && (
                <thead>
                  <tr>
                    {headers.map((h, i) => (
                      <th key={i}>{h}</th>
                    ))}
                  </tr>
                </thead>
              )}
              <tbody>
                {msg.rows.map((row, i) => (
                  <tr key={i}>
                    {row.map((cell, j) => (
                      <td key={j}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="empty">No data found for that question.</p>
          )}

          {/* Explainability: let the user inspect the exact SQL we ran */}
          {msg.sql && (
            <details className="sql-box">
              <summary>🔍 Show the generated SQL</summary>
              <pre>{msg.sql}</pre>
            </details>
          )}
        </div>
      </div>
    );
  }

  // --- Plain user / info / error messages ---
  return (
    <div className={`msg ${msg.type}`}>
      <div className="balloon">
        {msg.type === "error" ? <span className="error">⚠️ {msg.text}</span> : msg.text}
      </div>
    </div>
  );
}

function App() {
  const [messages, setMessages] = useState([
    {
      type: "info",
      text: 'Ask me about your company data, e.g. "Show me last month\'s best customers"',
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  // One session id per page load — sent with every request so the
  // server remembers this conversation (pending clarifications).
  const [sessionId] = useState(() => crypto.randomUUID());

  // Handle one API response: error, clarification, or answer rows.
  function addResponse(data) {
    if (data.error) {
      setMessages((prev) => [...prev, { type: "error", text: data.error }]);
    } else if (data.needs_clarification) {
      setMessages((prev) => [
        ...prev,
        {
          type: "clarify",
          label: data.clarification.question,
          options: data.clarification.options,
        },
      ]);
    } else {
      setMessages((prev) => [
        ...prev,
        {
          type: "answer",
          rows: data.rows,
          headers: data.columns || [],
          sql: data.sql || "",
        },
      ]);
    }
  }

  // Send a new question typed by the user.
  async function sendQuestion(e) {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { type: "user", text: q }]);
    setLoading(true);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, question: q }),
      });
      addResponse(await res.json());
    } catch {
      setMessages((prev) => [
        ...prev,
        { type: "error", text: "Could not reach the server. Is Flask running?" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Send the user's choice in the clarification dialog.
  async function sendChoice(i, opt) {
    if (loading) return;
    setMessages((prev) => [...prev, { type: "user", text: opt }]);
    setLoading(true);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, choice: i }),
      });
      addResponse(await res.json());
    } catch {
      setMessages((prev) => [
        ...prev,
        { type: "error", text: "Could not reach the server." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🗄️ Text-to-SQL</h1>
        <p>Ask a question, get an answer from your database.</p>
      </header>

      <main className="chat">
        {messages.map((m, i) => (
          <Message key={i} msg={m} onChoice={sendChoice} />
        ))}
        {loading && (
          <div className="msg info">
            <div className="balloon">Thinking…</div>
          </div>
        )}
      </main>

      <form className="composer" onSubmit={sendQuestion}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a question…"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
}

export default App;