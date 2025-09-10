import { Link } from "react-router-dom";

import { useCryptoData } from "../../hooks/useCryptoData";
import { useWatchlist } from "../../hooks/useWatchlist";

import { CryptoItem } from "@/components/CryptoCurrencyList/CryptoItem";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const LoadingSkeleton = () => (
  <div className="mx-4 mb-4"
  role="status"
  aria-live="polite"
  aria-label="Loading cryptocurrencies"
  >
    <h2 className="text-lg font-medium mb-2 pl-1">All Cryptocurrencies</h2>
    <Card className="p-0">
      <CardContent className="p-0">
        {[...Array(10)].map((_, index) => (
          <div
            key={index}
            className="flex items-center justify-between py-3 px-2 border-b last:border-b-0"
          >
            <div className="flex items-center gap-3">
              <Skeleton className="h-5 w-5 rounded-full" />
              <Skeleton className="h-8 w-8 rounded-full" />
              <div className="flex flex-col gap-1">
                <Skeleton className="h-5 w-20" />
                <Skeleton className="h-4 w-30" />
              </div>
            </div>
            <div className="text-right space-y-1">
              <Skeleton className="h-5 w-20" />
              <Skeleton className="h-4 w-15" />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  </div>
);

const ErrorDisplay = ({ error, onRetry }) => (
  <div className="mx-4 mb-4">
    <Alert variant="destructive">
      <AlertTitle>Error Loading Data</AlertTitle>
      <AlertDescription className="mt-2">
        {error}
        <Button
          onClick={onRetry}
          variant="outline"
          size="sm"
          className="mt-3 ml-0"
        >
          Try Again
        </Button>
      </AlertDescription>
    </Alert>
  </div>
);

const UpgradePrompt = () => (
  <Alert className="mt-4">
    <AlertDescription>
      Want to see more cryptocurrencies?{" "}
      <Link
        to="/profile"
        className="font-medium underline hover:text-primary transition-colors"
      >
        Upgrade your plan
      </Link>
    </AlertDescription>
  </Alert>
);

export const CryptoCurrencyList = () => {
  const {
    allCrypto,
    tierLimit,
    tierLabel,
    loading: cryptoLoading,
    error: cryptoError,
    refetch: refetchCrypto,
    lastUpdated,
  } = useCryptoData();

  const {
    loading: watchlistLoading,
    toggleWatchlist,
    isWatched,
  } = useWatchlist();

  if (cryptoLoading || watchlistLoading) return <LoadingSkeleton />;

  const displayedCrypto = allCrypto.slice(0, tierLimit);
  const hasMoreCrypto = allCrypto.length > tierLimit;
  const showUpgradePrompt = tierLabel !== "PREMIUM" && hasMoreCrypto;

  return (
    <div className="mx-4 mb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-medium pl-1">All Cryptocurrencies</h2>

        <div className="flex items-center gap-3">
          {lastUpdated && (
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-xs text-muted-foreground">
                Updated {lastUpdated}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Tier Info */}
      <p className="text-sm text-muted-foreground mb-2 pl-1">
        Showing top {tierLimit} cryptocurrencies based on your{" "}
        <Badge variant="secondary">{tierLabel}</Badge> tier.
      </p>

      {/* Error State */}
      {cryptoError && (
        <ErrorDisplay error={cryptoError} onRetry={refetchCrypto} />
      )}

      {/* Crypto List */}
      {!cryptoError && (
        <>
          <Card className="p-0">
            <CardContent className="py-1 px-1">
              {displayedCrypto.length > 0 ? (
                displayedCrypto.map((coin) => (
                  <CryptoItem
                    key={coin.symbol}
                    coin={coin}
                    isWatched={isWatched(coin.symbol)}
                    onToggleWatchlist={toggleWatchlist}
                  />
                ))
              ) : (
                <div className="py-8 text-center text-muted-foreground">
                  No cryptocurrency data available
                </div>
              )}
            </CardContent>
          </Card>

          {showUpgradePrompt && <UpgradePrompt />}
        </>
      )}
    </div>
  );
};
