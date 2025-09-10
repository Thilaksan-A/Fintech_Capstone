import "@/App.css";
import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import InvestorProfile from "@/components/ProfileEdit/InvestorProfile";
import SubscriptionTier from "@/components/ProfileEdit/SubscriptionTier";
import LoadingOverlay from "@/components/ui/loadingoverlay";
import { API_BASE_URL } from "@/config";

function ProfileEdit() {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState("menu"); // activeSection can be "menu", "profile", or "subscription"
  const [userInfo, setUserInfo] = useState("");
  const [currentPlan, setCurrentPlan] = useState("");
  const [loading, setLoading] = useState(false);
  const [surveyResponses, setSurveyResponses] = useState({});
  const [surveySubmitted, setSurveySubmitted] = useState(false);

  const responseKeyMap = {
    1: "stress_response",
    2: "emotional_reaction",
    3: "risk_perception",
    4: "income_vs_investment_balance",
    5: "debt_situation",
    6: "investment_experience",
    7: "investment_motivation",
    8: "knowledge_level",
    9: "investment_personality",
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("crypto_favourites");
    localStorage.removeItem("investor");
    localStorage.removeItem("userTier");
    window.location.reload(true);
    navigate("/landing");
  };

  // Get username + email
  useEffect(() => {
    getProfileData();
    getSubscriptionTier();
    getSurveyData();
  }, []);

  useEffect(() => {
    if (activeSection !== "profile") setSurveySubmitted(false);
  }, [activeSection]);

  const getProfileData = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.get(`${API_BASE_URL}/api/user/user_data`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      console.log("Profile data fetched:", res.data);
      setUserInfo(res.data);
    } catch (e) {
      if (e.response && e.response.status === 401) {
        console.warn("Unauthorized, redirecting to landing...");
        localStorage.removeItem("token");
        navigate("/landing");
      } else {
        console.error("Error fetching profile type:", e);
      }
    }
  };

  // Get subscription tier
  const getSubscriptionTier = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.get(`${API_BASE_URL}/api/user/tier`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      console.log(res);
      setCurrentPlan(res.data.subscription_tier);
    } catch (e) {
      if (e.response && e.response.status === 401) {
        console.warn("Unauthorized, redirecting to landing...");
        localStorage.removeItem("token");
        navigate("/landing");
      } else {
        console.error("Error fetching subscription tier:", e);
      }
    }
  };

  const handlePlanChange = async (plan) => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const res = await axios.post(
        `${API_BASE_URL}/api/user/update_tier`,
        { tier: plan },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCurrentPlan(res.data.subscription_tier);
      setLoading(false);
      window.location.reload(true);
    } catch (e) {
      if (e.response && e.response.status === 401) {
        console.warn("Unauthorized, redirecting to landing...");
        localStorage.removeItem("token");
        navigate("/landing");
      } else {
        console.error("Error submitting subscription tier change:", e);
      }
    }
  };

  // Get survey data
  const getSurveyData = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.get(`${API_BASE_URL}/api/user/profile`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      console.log("Profile data fetched:", res.data);
      setSurveyResponses(res.data);
    } catch (e) {
      if (e.response && e.response.status === 401) {
        console.warn("Unauthorized, redirecting to landing...");
        localStorage.removeItem("token");
        navigate("/landing");
      } else {
        console.error("Error fetching investor profile data:", e);
      }
    }
  };

  const handleSurveySubmit = async (payload) => {
    setLoading(true);
    const token = localStorage.getItem("token");
    try {
      await axios.post(`${API_BASE_URL}/api/user/survey`, payload, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (e) {
      if (e.response && e.response.status === 401) {
        console.warn("Unauthorized, redirecting to landing...");
        localStorage.removeItem("token");
        navigate("/landing");
      } else {
        console.error("Error submitting survey questions:", e);
      }
    } finally {
      await getSurveyData();
      window.scrollTo({
        top: 0,
        behavior: "auto",
      });
      setSurveySubmitted(true);
      setLoading(false);
    }
  };

  const backButton = () => {
    return (
      <button
        onClick={() => setActiveSection("menu")}
        className="absolute left-0 text-gray-800 hover:text-gray-600 px-2 py-1 transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M15 19l-7-7 7-7"
          />
        </svg>
      </button>
    );
  };

  return (
    <div className="relative max-w-2xl mx-auto px-6 pb-24 pt-10">
      {/* Header */}
      <div className="bg-white shadow rounded-xl p-6 flex flex-col items-center mb-6">
        <h2 className="text-xl font-bold">{userInfo.username}</h2>
        <p className="text-gray-500">{userInfo.email}</p>
      </div>

      {/* Menu */}
      {activeSection === "menu" && (
        <div className="grid gap-4">
          <div
            onClick={() => setActiveSection("profile")}
            className="cursor-pointer bg-white border border-gray-200 rounded-xl px-6 py-4 shadow-sm hover:shadow-md transition-all hover:bg-gray-50"
          >
            <h3 className="text-lg font-semibold text-gray-800">
              Edit Investment Profile
            </h3>
            <p className="text-sm text-gray-500">
              Update your answers and investment type.
            </p>
          </div>

          <div
            data-testid="SubscriptionTier"
            onClick={() => setActiveSection("subscription")}
            className="cursor-pointer bg-white border border-gray-200 rounded-xl px-6 py-4 shadow-sm hover:shadow-md transition-all hover:bg-gray-50"
          >
            <h3 className="text-lg font-semibold text-gray-800">
              Subscription Plan
            </h3>
            <p className="text-sm text-gray-500">
              View or change your current subscription tier.
            </p>
          </div>

          <div
            onClick={handleLogout}
            className="cursor-pointer bg-red-50 border border-red-200 rounded-xl px-6 py-4 shadow-sm hover:shadow-md transition-all hover:bg-red-100"
          >
            <h3 className="text-lg font-semibold text-red-700">Logout</h3>
            <p className="text-sm text-red-500">Sign out of your account.</p>
          </div>
        </div>
      )}

      {/* Investment Profile Section */}
      {activeSection === "profile" && (
        <div>
          <div className="relative flex items-center justify-center py-4">
            {backButton()}
            <h1 className="text-3xl font-bold text-gray-900">Edit Profile</h1>
          </div>
          {surveySubmitted && (
            <p className="mt-4 text-custom-secondary font-medium">
              Profile updated successfully!
            </p>
          )}
          <InvestorProfile
            data={surveyResponses}
            onSubmit={handleSurveySubmit}
          />
        </div>
      )}

      {/* Subscription Tier Section */}
      {activeSection === "subscription" && (
        <div>
          <div className="relative flex items-center justify-center py-4">
            {backButton()}
            <h1 className="text-3xl font-bold text-gray-900">Choose a Plan</h1>
          </div>
          <SubscriptionTier
            currentPlan={currentPlan}
            onSelect={handlePlanChange}
          />
        </div>
      )}

      {loading && <LoadingOverlay />}
    </div>
  );
}

export default ProfileEdit;
