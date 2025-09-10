import axios from "axios";
import { useState } from "react";

import { API_BASE_URL } from "../config";

import { Button } from "@/components/ui/button";

function Survey({ questions, onComplete }) {
    const [stepIndex, setStepIndex] = useState(0);
    const [selected, setSelected] = useState(null);
    const question = questions[stepIndex];

    const [surveyData, setSurveyData] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    if (!question) return null;
  
    const handleSelect = (option) => {
      const updatedSurveyData = { ...surveyData, [stepIndex]: option };
      setSurveyData(updatedSurveyData);
      setSelected(option);
      handleNext(updatedSurveyData);
    };
  
    const handleNext = async (updatedSurveyData) => {
      if (stepIndex < questions.length - 1) {
        setStepIndex(stepIndex + 1);
        setSelected(null);
      } else {
        await handleComplete(updatedSurveyData);
        onComplete();
      }
    };

    const handlePrevious = () => {
      if (stepIndex > 0) {
        setStepIndex(stepIndex - 1);
        setSelected(null);
      }
    };
  
    const handleComplete = async (updatedSurveyData) => {
      setIsSubmitting(true);
      const mapped = {
        stress_response: updatedSurveyData[0],
        emotional_reaction: updatedSurveyData[1],
        risk_perception: updatedSurveyData[2],
        income_vs_investment_balance: updatedSurveyData[3],
        debt_situation: updatedSurveyData[4],
        investment_experience: updatedSurveyData[5],
        investment_motivation: updatedSurveyData[6],
        knowledge_level: updatedSurveyData[7],
        investment_personality: updatedSurveyData[8],
      };
      try {
        const token = localStorage.getItem("token");
        const res = await axios.post(`${API_BASE_URL}/api/user/survey`, mapped, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          }
        });
        localStorage.setItem("investor", res.data.investor_type)
      } catch (e) {
        console.err("unable to send survey data", e.response)
      } finally {
        setIsSubmitting(false);
      }
    }

    if (isSubmitting) {
      return (
        <div className="flex justify-center items-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-[#32a220] mx-auto mb-4"></div>
            <p className="text-lg font-semibold">Submitting your answers...</p>
          </div>
        </div>
      );
    }

    return (
      <div className="flex justify-center items-center h-screen flex-col">
        <div className="bg-[#D9D9D980] p-10 rounded-2xl shadow w-90 text-center max-w-md">
          <p className="text-lg font-semibold mb-4">{question.question}</p>
  
          <div className="space-y-2">
            {question.options.map((option, idx) => (
              <div
                key={idx}
                onClick={() => handleSelect(option)}
                className={`
                  cursor-pointer px-4 py-3 rounded-lg border border-[#32a220]
                  ${selected === option ? 'bg-[#3eb12c85] text-white' : 'bg-white text-black'}
                  hover:bg-blue-100
                `}
              >
                {option}
              </div>
            ))}
          </div>
  
          <Button
            onClick={handlePrevious}
            className="mt-6 bg-[#32a220] text-white px-4 py-2 rounded"
            disabled={stepIndex === 0}
          >
            Previous
          </Button>
        </div>
      </div>
    );
  }
  
  export default Survey;
