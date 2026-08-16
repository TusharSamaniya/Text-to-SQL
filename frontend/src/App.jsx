import { useState } from "react";
import "./App.css";

// The URL of our Flask backend. Vite proxies /api -> 127.0.0.1:5000
// (see vite.config.js), so the browser never needs the full URL here.
const API_URL = "/api/ask";

// A single message in the chat.
function Message({ msg }) {
  // If there are result rows, render them as a table.
  if (msg.type === "answer" && msg.rows && msg.rows.length > 0) {
    const headers = msg.headers || [];
    return (
      <div className="msg answer">
        <div className="balloon">
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
        </div>
      </div>
    );
  }

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
      text: "Ask me about your company data, e.g. \"How many new customers signed up last month?\"",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

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
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();

      if (data.error) {
        setMessages((prev) => [...prev, { type: "error", text: data.error }]);
      } else {
        setMessages((prev) => [
          ...prev,
          { type: "answer", rows: data.rows, headers: data.columns || [] },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { type: "error", text: "Could not reach the server. Is Flask running?" },
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

      <main className="chat" ref={(el) => el && el.scrollIntoView({ behavior: "smooth" })}>
        {messages.map((m, i) => (
          <Message key={i} msg={m} />
        ))}
        {loading && <div className="msg info"><div className="balloon">Thinking…</div></div>}
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