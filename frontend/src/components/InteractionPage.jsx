import React, { useState } from "react";
import HCPForm from "./HCPForm";
import ChatAgent from "./ChatAgent";
import "../styles/InteractionPage.css";

export default function InteractionPage() {
  const [formData, setFormData] = useState({
    hcp_name: "",
    interaction_type: "Meeting",
    date: "",
    time: "",
    attendees: "",
    topics_discussed: "",
    materials_shared: [],
    samples_distributed: [],
    sentiment: "",
    outcomes: ""
  });

  return (
    <div className="interaction-layout">
      <div className="left-panel">
        <HCPForm formData={formData} setFormData={setFormData} />
      </div>

      <div className="right-panel">
        <ChatAgent
          onExtract={(extracted) => {
            setFormData((prev) => ({
              ...prev,
              ...extracted
            }));
          }}
        />
      </div>
    </div>
  );
}
