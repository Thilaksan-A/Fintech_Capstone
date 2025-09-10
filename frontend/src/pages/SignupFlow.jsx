import axios from "axios";
import { useState } from "react";

import AccountConfirm from "./AccountConfirm";
import Signup from "./Signup";
import Survey from "./Survey";
import TierSelect from "./TierSelect";

import { API_BASE_URL } from "@/config";
import Questions from "@/data/QUESTIONS";

function SignupFlow() {
  const [step, setStep] = useState("form");

  const handleTierSelect = (tier) => {
    localStorage.setItem("userTier", tier);
    updateTier();
    setStep("survey");
  };

  const updateTier = async () => {
    let token = localStorage.getItem("token");
    try {
      await axios.post(
        `${API_BASE_URL}/api/user/update_tier`,
        {
          tier: localStorage.getItem("userTier"),
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
    } catch (e) {
      console.error("Unable to update tier level", e);
    }
  };

  return (
    <>
      {step === "form" && <Signup onSuccess={() => setStep("tier")} />}
      {step === "tier" && <TierSelect onSelect={handleTierSelect} />}
      {step === "survey" && (
        <Survey questions={Questions} onComplete={() => setStep("confirmed")} />
      )}
      {step === "confirmed" && <AccountConfirm />}
    </>
  );
}

export default SignupFlow;
