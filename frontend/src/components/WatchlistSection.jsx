import { Star } from "lucide-react";

import { CryptoItem } from "@/components/CryptoCurrencyList/CryptoItem";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { useCryptoData } from "@/hooks/useCryptoData";
import { useWatchlist } from "@/hooks/useWatchlist";

const WatchlistSkeleton = () => (
  <div className="p-4">
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton data-testid="skeleton" className="h-8 w-8 rounded-full" />
          <div className="flex-1">
            <Skeleton className="h-4 w-20 mb-1" />
            <Skeleton className="h-3 w-32" />
          </div>
          <Skeleton className="h-6 w-16" />
        </div>
      ))}
    </div>
  </div>
);

const EmptyWatchlist = () => (
  <div className="p-8 text-center">
    <Star className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
    <h3 className="font-medium text-lg mb-2">Your watchlist is empty</h3>
    <p className="text-sm text-muted-foreground mb-4">
      Start adding cryptocurrencies to track your favorites
    </p>
    <p className="text-xs text-muted-foreground">
      Click the ⭐ icon next to any cryptocurrency to add it to your watchlist
    </p>
  </div>
);

export const WatchlistSection = () => {
  const {
    watchlist,
    loading: watchlistLoading,
    error: watchlistError,
    toggleWatchlist,
    isWatched,
  } = useWatchlist();

  const { allCrypto, loading: cryptoLoading } = useCryptoData();

  // Show loading skeleton while data loads
  if (watchlistLoading || cryptoLoading) {
    return <WatchlistSkeleton />;
  }

  // Show error state
  if (watchlistError) {
    return (
      <div className="p-4">
        <Alert variant="destructive">
          <AlertDescription>
            Failed to load watchlist: {watchlistError}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Show empty state
  if (watchlist.size === 0) {
    return <EmptyWatchlist />;
  }

  // Filter and enrich watchlist items with current price data
  const watchlistItems = allCrypto
    .filter((crypto) => watchlist.has(crypto.symbol))
    .sort((a, b) => (a.market_cap_rank || 999) - (b.market_cap_rank || 999));

  return (
    <div className="bg-white">
      {watchlistItems.length > 0 ? (
        <div className="divide-y divide-gray-100">
          {watchlistItems.map((coin) => (
            <div key={coin.symbol} className="px-2">
              <CryptoItem
                coin={coin}
                isWatched={isWatched(coin.symbol)}
                onToggleWatchlist={toggleWatchlist}
              />
            </div>
          ))}
        </div>
      ) : (
        <div className="p-8 text-center">
          <p className="text-sm text-muted-foreground">
            Your watched cryptocurrencies will appear here when price data is
            available
          </p>
        </div>
      )}
    </div>
  );
};
