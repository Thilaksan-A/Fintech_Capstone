import { useEffect, useState } from "react";

import Questions from "@/data/QUESTIONS";


export default function InvestorProfile({ data, onSubmit }) {
  const [responses, setResponses] = useState({});
  const [profileType, setProfileType] = useState("Unknown");

  const responseKeyMap = {
  1: "stress_response",
  2: "emotional_reaction",
  3: "risk_perception",
  4: "income_vs_investment_balance",
  5: "debt_situation",
  6: "investment_experience",
  7: "investment_motivation",
  8: "knowledge_level",
  9: "investment_personality"
};

  useEffect(() => {
    if (!data) return;
    setProfileType(data.investor_type);
    const responses = mapResponses(data.raw_responses);
    setResponses(responses);
  }, [data]);

  const mapResponses = (rawResponses) => {
    const mapped = {};

    Questions.forEach((q) => {
      const backendKey = responseKeyMap[q.id];
      if (!backendKey) return;

      mapped[q.id] = q.questionType === "multiple"
        ? rawResponses[backendKey] || []
        : rawResponses[backendKey];
    });

    return mapped;
  };

  const handleChange = (id, value, multiple = false) => {
    setResponses((prev) => {
      if (multiple) {
        const existing = Array.isArray(prev[id]) ? prev[id] : [];
        const updated = existing.includes(value)
          ? existing.filter((v) => v !== value)
          : [...existing, value];
        return { ...prev, [id]: updated };
      }
      return { ...prev, [id]: value };
    });
  };
  
  const handleSubmit = () => {
    console.log("Submitting profile data:", responses);
    
    const payload = Object.fromEntries(
      Object.entries(responses).map(
        ([key, value]) => [responseKeyMap[key], value]
      )
    );
    console.log("Mapped payload for submission:", payload);
    onSubmit(payload);
  };

  return (
    <div className="max-w-3xl mx-auto px-2 pt-3">
      <h2 className="text-lg text-gray-600 mb-6">You are a <span className="text-green-600 font-semibold">{profileType}</span></h2>

      <div className="space-y-6">
        {Questions.map((q) => (
          <div key={q.id} className="bg-white border border-gray-200 rounded-lg shadow-sm p-4">
            <label htmlFor={`question-${q.id}`} className="block font-medium text-gray-800 mb-2">{q.question}</label>
            <select
              id={`question-${q.id}`}
              value={(responses[q.id] || "")}
              onChange={(e) => handleChange(q.id, e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            >
              <option value="" disabled>
                Select an answer...
              </option>
              {q.options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
      <div className="mt-5 flex justify-between items-center">
        <button
          onClick={handleSubmit}
          className="bg-custom-primary text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Save Profile
        </button>
      </div>

    </div>
  );
}
