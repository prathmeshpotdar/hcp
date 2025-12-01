import React, { useState } from "react";

function normalizeSentiment(raw) {
  // Accept many shapes: "positive", "Positive", "POS", "Observed: positive",
  // or { sentiment: "positive" }, or arrays etc.
  if (!raw && raw !== 0) return null;

  // If object with sentiment key
  if (typeof raw === "object") {
    if (raw.sentiment) raw = raw.sentiment;
    else {
      // try first value
      const vals = Object.values(raw).filter(Boolean);
      raw = vals.length ? vals[0] : null;
    }
  }

  if (!raw) return null;
  const s = String(raw).trim().toLowerCase();

  if (s.includes("pos")) return "Positive";
  if (s.includes("neg")) return "Negative";
  if (s.includes("neu")) return "Neutral";

  // fallback: exact matches
  if (s === "positive") return "Positive";
  if (s === "negative") return "Negative";
  if (s === "neutral") return "Neutral";

  return null;
}

export default function LogInteraction() {
  // FORM STATE
  const [hcpName, setHcpName] = useState("");
  const [interactionType, setInteractionType] = useState("Meeting");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [topics, setTopics] = useState("");
  const [materials, setMaterials] = useState("No materials added.");
  const [sentiment, setSentiment] = useState("");
  const [summary, setSummary] = useState("");

  // CHAT STATE
  const [messages, setMessages] = useState([
    {
      type: "info",
      text:
        'Log interaction details here (e.g., "Met Dr. Smith, discussed Product-X efficacy, positive sentiment, shared brochure") or ask for help.'
    }
  ]);

  const [input, setInput] = useState("");

  // HANDLE CHAT → BACKEND → APPLY TO FORM
  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { type: "user", text: input }]);

    try {
      const res = await fetch("http://localhost:8000/api/interactions/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input })
      });

      const data = await res.json();

      // Add assistant message
      setMessages((prev) => [...prev, { type: "ai", text: data.message }]);

      const extracted = data.data || {};
      // DEBUG: show raw extracted in console and chat log (helps see shapes)
      console.log("AI extracted:", extracted);
      setMessages((prev) => [
        ...prev,
        {
          type: "info",
          text: "DEBUG extracted: " + JSON.stringify(extracted)
        }
      ]);

      // --------------------------
      // APPLY EXTRACTED DATA
      // --------------------------
      if (extracted.hcp_name) setHcpName(extracted.hcp_name);
      if (extracted.date) setDate(extracted.date);
      if (extracted.time) setTime(extracted.time);
      if (extracted.topics_discussed) setTopics(extracted.topics_discussed);

      if (extracted.materials_shared?.length > 0) {
        setMaterials(extracted.materials_shared.join(", "));
      }

      // SENTIMENT: robust normalization
      const candidate =
        extracted.sentiment ??
        (typeof extracted === "object" && extracted?.sentiment) ??
        null;

      const normalized = normalizeSentiment(candidate);
      if (normalized) {
        setSentiment(normalized);
      } else {
        // fallback: try scanning raw text keys for sentiment-like values
        if (typeof extracted === "string") {
          const s2 = normalizeSentiment(extracted);
          if (s2) setSentiment(s2);
        }
      }

      // SUMMARY
      if (extracted.summary) {
        setSummary(extracted.summary);
      }
    } catch (err) {
      console.error("sendMessage error:", err);
      setMessages((prev) => [
        ...prev,
        { type: "ai", text: "Failed to call server." }
      ]);
    }

    setInput("");
  };

  return (
    <div className="layout" style={{ display: "flex", gap: 24 }}>
      {/* LEFT FORM */}
      <div className="form-section" style={{ flex: 1, minWidth: 360 }}>
        <h2>Log HCP Interaction</h2>

        <label>HCP Name</label>
        <input
          className="input"
          placeholder="Search or select HCP..."
          value={hcpName}
          onChange={(e) => setHcpName(e.target.value)}
        />

        <label>Interaction Type</label>
        <select
          className="input"
          value={interactionType}
          onChange={(e) => setInteractionType(e.target.value)}
        >
          <option>Meeting</option>
          <option>Call</option>
          <option>Email</option>
        </select>

        <div className="row" style={{ display: "flex", gap: 12 }}>
          <div className="col" style={{ flex: 1 }}>
            <label>Date</label>
            <input
              type="date"
              className="input"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>

          <div className="col" style={{ flex: 1 }}>
            <label>Time</label>
            <input
              type="time"
              className="input"
              value={time}
              onChange={(e) => setTime(e.target.value)}
            />
          </div>
        </div>

        <label>Topics Discussed</label>
        <textarea
          className="textarea"
          placeholder="Enter key discussion points..."
          value={topics}
          onChange={(e) => setTopics(e.target.value)}
        />

        <label>Materials Shared</label>
        <div className="materials-box">{materials}</div>

        <label>Observed/Inferred HCP Sentiment</label>
        <div className="sentiment-row" style={{ display: "flex", gap: 12 }}>
          <label className="sent-option">
            <input
              type="radio"
              name="sent"
              value="Positive"
              checked={sentiment === "Positive"}
              onChange={(e) => setSentiment(e.target.value)}
            />
            🙂 Positive
          </label>

          <label className="sent-option">
            <input
              type="radio"
              name="sent"
              value="Neutral"
              checked={sentiment === "Neutral"}
              onChange={(e) => setSentiment(e.target.value)}
            />
            😐 Neutral
          </label>

          <label className="sent-option">
            <input
              type="radio"
              name="sent"
              value="Negative"
              checked={sentiment === "Negative"}
              onChange={(e) => setSentiment(e.target.value)}
            />
            🙁 Negative
          </label>
        </div>

        {/* SUMMARY BOX */}
        <label>Summary (AI Generated)</label>
        <textarea
          className="textarea summary-box"
          value={summary}
          readOnly
          placeholder="AI summary will appear here..."
        />
      </div>

      {/* RIGHT CHAT PANEL */}
      <div className="chat-section" style={{ width: 420 }}>
        <h3>🤖 AI Assistant</h3>

        <div
          className="chat-box"
          style={{
            height: 420,
            overflowY: "auto",
            border: "1px solid #eee",
            padding: 12,
            borderRadius: 8,
            marginBottom: 12
          }}
        >
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                marginBottom: 8,
                padding: "8px 10px",
                borderRadius: 8,
                background:
                  msg.type === "user"
                    ? "#dbeafe"
                    : msg.type === "ai"
                    ? "#eef2ff"
                    : "#f3f4f6",
                alignSelf: msg.type === "user" ? "flex-end" : "flex-start"
              }}
            >
              <div style={{ fontSize: 13 }}>{msg.text}</div>
            </div>
          ))}
        </div>

        <div className="chat-input-box" style={{ display: "flex", gap: 8 }}>
          <input
            className="chat-input"
            placeholder="Describe interaction..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={{ flex: 1, padding: 8 }}
          />
          <button className="log-btn" onClick={sendMessage} style={{ padding: "8px 12px" }}>
            Log
          </button>
        </div>
      </div>
    </div>
  );
}
