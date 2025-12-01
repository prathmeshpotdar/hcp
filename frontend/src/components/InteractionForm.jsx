import React from "react";

export default function InteractionForm({ extracted, setExtracted }) {
  const update = (k, v) => setExtracted((s) => ({ ...s, [k]: v }));

  const addMaterial = () => update("materials_shared", [...(extracted.materials_shared || []), "New Material"]);
  const removeMaterial = (idx) =>
    update("materials_shared", extracted.materials_shared.filter((_, i) => i !== idx));

  return (
    <div className="form-card">
      <div className="form-header">
        <h3>Interaction Details</h3>
        <div className="form-sub">Automatically populated from summary</div>
      </div>

      <div className="form-row">
        <label>HCP Name</label>
        <input value={extracted.hcp_name || ""} onChange={(e) => update("hcp_name", e.target.value)} />
      </div>

      <div className="form-row two-col">
        <div>
          <label>Date</label>
          <input type="date" value={extracted.date || ""} onChange={(e) => update("date", e.target.value)} />
        </div>
        <div>
          <label>Time</label>
          <input type="time" value={extracted.time || ""} onChange={(e) => update("time", e.target.value)} />
        </div>
      </div>

      <div className="form-row">
        <label>Sentiment</label>
        <select value={extracted.sentiment || ""} onChange={(e) => update("sentiment", e.target.value)}>
          <option value="">--</option>
          <option value="Positive">Positive</option>
          <option value="Neutral">Neutral</option>
          <option value="Negative">Negative</option>
        </select>
      </div>

      <div className="form-row">
        <label>Topics Discussed</label>
        <input value={extracted.topics_discussed || ""} onChange={(e) => update("topics_discussed", e.target.value)} />
      </div>

      <div className="form-row">
        <label>Materials Shared</label>
        <div className="materials">
          {(extracted.materials_shared || []).map((m, i) => (
            <div className="chip" key={i}>
              <span>{m}</span>
              <button onClick={() => removeMaterial(i)} type="button">✕</button>
            </div>
          ))}
          <button className="btn small ghost" type="button" onClick={addMaterial}>+ Add</button>
        </div>
      </div>

      <div className="form-row">
        <label>Samples Distributed</label>
        <input value={(extracted.samples_distributed || []).join(", ")} onChange={(e) => update("samples_distributed", e.target.value.split(",").map(s=>s.trim()))} />
      </div>

      <div className="form-row">
        <label>Follow-up Date</label>
        <input type="date" value={extracted.follow_up_date || ""} onChange={(e) => update("follow_up_date", e.target.value)} />
      </div>

      <div className="form-row">
        <label>Summary</label>
        <textarea value={extracted.summary || ""} onChange={(e) => update("summary", e.target.value)} />
      </div>

      <div className="form-actions">
        <button className="btn primary">Save</button>
        <button className="btn ghost">Cancel</button>
      </div>
    </div>
  );
}
