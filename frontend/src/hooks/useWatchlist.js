import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { useCallback, useMemo } from "react";

import { API_BASE_URL } from "@/config";

// API functions
const watchlistAPI = {
  // Fetch watchlist from server
  fetchWatchlist: async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("No authentication token");
    }

    const response = await axios.get(`${API_BASE_URL}/api/watchlist/list`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return response.data.map((item) => item.symbol);
  },

  // Toggle watchlist item on server
  toggleWatchlist: async (symbol) => {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("No authentication token");
    }

    await axios.post(
      `${API_BASE_URL}/api/watchlist/toggle`,
      { symbol },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    return symbol;
  },
};

// Helper functions
const getLocalStorageWatchlist = () => {
  try {
    const saved = localStorage.getItem("crypto_favourites");
    return saved ? JSON.parse(saved) : [];
  } catch {
    console.warn("Failed to load from localStorage");
    return [];
  }
};

const saveToLocalStorage = (watchlist) => {
  try {
    localStorage.setItem("crypto_favourites", JSON.stringify([...watchlist]));
  } catch (err) {
    console.warn("Failed to save to localStorage:", err);
  }
};

export const useWatchlist = () => {
  const queryClient = useQueryClient();
  const hasToken = !!localStorage.getItem("token");

  // Query for watchlist data
  const {
    data: watchlistArray = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["watchlist"],
    queryFn: watchlistAPI.fetchWatchlist,
    enabled: hasToken, // Only run if user is authenticated
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
    onError: (err) => {
      console.error("Failed to load watchlist:", err);
      // Fallback to localStorage on error
      const localWatchlist = getLocalStorageWatchlist();
      queryClient.setQueryData(["watchlist"], localWatchlist);
    },
    // Initialize with localStorage if no token
    initialData: hasToken ? undefined : getLocalStorageWatchlist(),
  });

  const watchlistSet = useMemo(() => new Set(watchlistArray), [watchlistArray]);

  // Mutation for toggling watchlist items
  const toggleMutation = useMutation({
    mutationFn: watchlistAPI.toggleWatchlist,
    onMutate: async (symbol) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["watchlist"] });

      // Snapshot the previous value
      const previousWatchlist = queryClient.getQueryData(["watchlist"]) || [];

      // Optimistically update
      const newWatchlist = previousWatchlist.includes(symbol)
        ? previousWatchlist.filter((s) => s !== symbol)
        : [...previousWatchlist, symbol];

      queryClient.setQueryData(["watchlist"], newWatchlist);

      // Update localStorage
      saveToLocalStorage(new Set(newWatchlist));

      return { previousWatchlist };
    },
    onError: (err, symbol, context) => {
      console.error("Failed to toggle watchlist:", err);

      // Revert to previous state
      if (context?.previousWatchlist) {
        queryClient.setQueryData(["watchlist"], context.previousWatchlist);
        saveToLocalStorage(new Set(context.previousWatchlist));
      }
    },
    onSettled: () => {
      // Always refetch after error or success to ensure we have the latest data
      queryClient.invalidateQueries({ queryKey: ["watchlist"] });
    },
  });

  // Toggle function
  const toggleWatchlist = useCallback(
    async (symbol) => {
      if (!symbol) return false;

      try {
        await toggleMutation.mutateAsync(symbol);
        return true;
      } catch (err) {
        console.error("Toggle watchlist failed:", err);
        return false;
      }
    },
    [toggleMutation]
  );

  const isWatched = useCallback(
    (symbol) => watchlistSet.has(symbol),
    [watchlistSet]
  );

  return {
    watchlist: watchlistSet,
    watchlistArray, // Also provide array version if needed
    loading: isLoading,
    error: error?.message || null,
    isToggling: toggleMutation.isPending,
    toggleWatchlist,
    refetch,
    isWatched,
  };
};
