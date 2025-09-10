import { plans } from "@/data/TiersInfo";

function TierSelect({ onSelect }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4">
      <h1 className="text-2xl font-semibold mb-6">Choose Your Plan</h1>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-4xl">
        {plans.map((plan) => (
          <div
            key={plan.key}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition"
          >
            <h2 className="text-lg font-semibold">{plan.name}</h2>
            <p className="text-gray-600 mb-2">{plan.description}</p>
            <p className="text-xl font-bold mb-4">{plan.price}</p>
            <button
              onClick={() => onSelect(plan.key)}
              className="bg-[#32a220] text-white px-4 py-2 rounded hover:bg-[#27891a]"
            >
              Select {plan.name}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TierSelect;
