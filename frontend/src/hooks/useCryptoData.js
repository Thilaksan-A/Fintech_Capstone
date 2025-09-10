import axios from "axios";
import { useCallback, useEffect, useState } from "react";

import { API_BASE_URL } from "@/config";

export const useCryptoData = () => {
  const [allCrypto, setAllCrypto] = useState([]);
  const [tierLimit, setTierLimit] = useState(3);
  const [tierLabel, setTierLabel] = useState("FREE");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Helper function to calculate time ago
  const getTimeAgo = (timestamp) => {
    if (!timestamp) return "Unknown";

    const now = new Date();
    const past = new Date(timestamp);
    const diffInSeconds = Math.floor((now - past) / 1000);

    if (diffInSeconds < 60) {
      return `${diffInSeconds}s ago`;
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes}m ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days}d ago`;
    }
  };

  // Calculate last updated text from crypto data
  const calculateLastUpdated = (cryptoData) => {
    if (!Array.isArray(cryptoData) || cryptoData.length === 0) {
      return "No data";
    }

    // Find the most recent timestamp from all crypto data
    const timestamps = cryptoData
      .map((crypto) => crypto.timestamp)
      .filter((timestamp) => timestamp)
      .map((timestamp) => new Date(timestamp));

    if (timestamps.length === 0) {
      return "No timestamp data";
    }

    const mostRecent = new Date(Math.max(...timestamps));
    return getTimeAgo(mostRecent);
  };

  const fetchTopRanked = async (ranking) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/crypto/top_ranking`, {
        params: { ranking },
      });

      const cryptoData = res.data;
      setAllCrypto(cryptoData);

      // Calculate and set last updated text
      const lastUpdatedText = calculateLastUpdated(cryptoData);
      setLastUpdated(lastUpdatedText);
    } catch (e) {
      console.error("Unable to fetch cryptocurrency data:", e.response || e);
      throw e;
    }
  };

  const getTierInfo = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.warn("No authentication token found");
      return;
    }

    try {
      const res = await axios.get(`${API_BASE_URL}/api/user/tier`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTierLimit(res.data.limit);
      setTierLabel(res.data.subscription_tier?.toUpperCase() || "FREE");
    } catch (e) {
      console.error("Unable to fetch tier information:", e);
      // Don't throw - use defaults if tier info fails
    }
  };

  const initializeData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await Promise.all([getTierInfo(), fetchTopRanked(50)]); // Fetch more data, filter by tierLimit in component
    } catch {
      setError("Failed to load data. Please try again.");
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    initializeData();
  }, [initializeData]);

  // Update last updated text every 30 seconds
  useEffect(() => {
    if (!allCrypto.length) return;

    const interval = setInterval(() => {
      const lastUpdatedText = calculateLastUpdated(allCrypto);
      setLastUpdated(lastUpdatedText);
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allCrypto]);

  return {
    allCrypto,
    tierLimit,
    tierLabel,
    loading,
    error,
    lastUpdated,
    refetch: initializeData,
  };
};
