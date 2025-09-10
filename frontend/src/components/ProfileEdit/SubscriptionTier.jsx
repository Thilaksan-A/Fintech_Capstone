import React from "react";

import { plans } from "@/data/TiersInfo";

function SubscriptionTier({ currentPlan, onSelect }) {
  return (
    <div className="max-w-3xl mx-auto px-2 pt-7">
      <div className="mb-6 border p-4 rounded bg-gray-50">
        <p className="text-lg font-semibold">{currentPlan}</p>
        <p className="text-sm text-gray-600">
          {
            plans.find((plan) => plan.key === currentPlan)?.description ??
            "No description available"
          }
        </p>
      </div>

      <h3 className="text-xl font-semibold mb-2">Change Your Plan</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {plans
          .filter((plan) => plan.key !== currentPlan)
          .map((plan) => (
            <div
              key={plan.key}
              className="border rounded p-4 bg-gray-100 hover:bg-gray-200 transition"
            >
              <h4 className="text-lg font-semibold">{plan.name}</h4>
              <p className="text-sm text-gray-600 mb-2">{plan.description}</p>
              <p className="text-base font-bold mb-3">{plan.price}</p>
              <button
                onClick={() => onSelect(plan.key)}
                className="bg-custom-primary text-white px-4 py-2 rounded hover:bg-green-700"
              >
                Switch to {plan.name}
              </button>
            </div>
          ))}
      </div>
    </div>
  );
}

export default SubscriptionTier;
