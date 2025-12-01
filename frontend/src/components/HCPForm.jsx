import React from "react";
import "../styles/HCPForm.css";

export default function HCPForm({ formData, setFormData }) {
  const update = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="form-container">
      <div className="form-title">Log HCP Interaction</div>

      <div className="form-section-title">Interaction Details</div>

      <div className="form-row">
        <div className="form-col">
          <label className="form-label">HCP Name</label>
          <input
            className="text-input"
            placeholder="Search or select HCP..."
            value={formData.hcp_name}
            onChange={(e) => update("hcp_name", e.target.value)}
          />
        </div>

        <div className="form-col">
          <label className="form-label">Interaction Type</label>
          <select
            className="select-input"
            value={formData.interaction_type}
            onChange={(e) => update("interaction_type", e.target.value)}
          >
            <option>Meeting</option>
            <option>Call</option>
            <option>Virtual</option>
          </select>
        </div>
      </div>

      <div className="form-row" style={{ marginTop: 16 }}>
        <div className="form-col">
          <label className="form-label">Date</label>
          <input
            type="date"
            className="text-input"
            value={formData.date}
            onChange={(e) => update("date", e.target.value)}
          />
        </div>

        <div className="form-col">
          <label className="form-label">Time</label>
          <input
            type="time"
            className="text-input"
            value={formData.time}
            onChange={(e) => update("time", e.target.value)}
          />
        </div>
      </div>

      <label className="form-section-title" style={{ marginTop: 16 }}>
        Attendees
      </label>
      <input
        className="text-input"
        placeholder="Enter names or search..."
        value={formData.attendees}
        onChange={(e) => update("attendees", e.target.value)}
      />

      <label className="form-section-title" style={{ marginTop: 18 }}>
        Topics Discussed
      </label>
      <textarea
        className="textarea-input"
        placeholder="Enter key discussion points..."
        value={formData.topics_discussed}
        onChange={(e) => update("topics_discussed", e.target.value)}
      />

      <div className="section-divider"></div>

      <label className="form-section-title">Materials Shared</label>
      <div className="search-btn">🔍 Search/Add</div>

      <div className="small-display">
        {formData.materials_shared.length
          ? formData.materials_shared.join(", ")
          : "No materials added."}
      </div>

      <label className="form-section-title" style={{ marginTop: 18 }}>
        Samples Distributed
      </label>
      <div className="add-btn">＋ Add Sample</div>

      <div className="small-display">
        {formData.samples_distributed.length
          ? formData.samples_distributed.join(", ")
          : "No samples added."}
      </div>

      <label className="form-section-title" style={{ marginTop: 18 }}>
        Observed/Inferred HCP Sentiment
      </label>

      <div className="sentiment-row">
        <label className="sentiment-label">
          <input
            type="radio"
            name="sentiment"
            checked={formData.sentiment === "Positive"}
            onChange={() => update("sentiment", "Positive")}
          />{" "}
          😊 Positive
        </label>

        <label className="sentiment-label">
          <input
            type="radio"
            name="sentiment"
            checked={formData.sentiment === "Neutral"}
            onChange={() => update("sentiment", "Neutral")}
          />{" "}
          😐 Neutral
        </label>

        <label className="sentiment-label">
          <input
            type="radio"
            name="sentiment"
            checked={formData.sentiment === "Negative"}
            onChange={() => update("sentiment", "Negative")}
          />{" "}
          😟 Negative
        </label>
      </div>

      <label className="form-section-title" style={{ marginTop: 18 }}>
        Outcomes
      </label>
      <textarea
        className="outcomes-input"
        placeholder="Key outcomes or agreements..."
        value={formData.outcomes}
        onChange={(e) => update("outcomes", e.target.value)}
      />
    </div>
  );
}
