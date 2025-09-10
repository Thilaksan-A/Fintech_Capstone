import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { WatchlistStarButton } from "@/components/WatchlistStarButton";
import { cn } from "@/lib/utils";

const PriceDisplay = ({ coin }) => {
  const formatPrice = (price) => {
    if (typeof price !== "number") return "N/A";
    return price.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    });
  };

  if (coin.price_change_24h === undefined) {
    return (
      <div className="text-right">
        <div className="font-medium text-foreground">
          {formatPrice(coin.price)}
        </div>
      </div>
    );
  }

  const isPositive = coin.price_change_24h >= 0;

  return (
    <div className="text-right">
      <div className="font-medium text-foreground">
        {formatPrice(coin.price)}
      </div>
      <Badge
        variant="outline"
        className={cn("text-xs", {
          "text-green-500": isPositive,
          "text-red-500": !isPositive,
        })}
      >
        {isPositive ? "↗" : "↘"} {Math.abs(coin.price_change_24h).toFixed(2)}%
      </Badge>
    </div>
  );
};

export const CryptoItem = ({ coin, isWatched = false, onToggleWatchlist }) => {
  if (!coin) return null;

  const {
    symbol = "N/A",
    name = "Unknown",
    image,
    market_cap_rank: rank = 0,
  } = coin;

  const handleImageError = (e) => {
    e.target.style.display = "none";
  };

  return (
    <Link
      to={`/cryptocurrency/${symbol.toLowerCase()}`}
      className="flex items-center justify-between py-3 mx-2 border-b last:border-b-0 hover:bg-muted/50 transition-colors no-underline text-inherit gap-2"
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        {/* Rank Badge */}
        {rank > 0 && (
          <Badge
            variant="outline"
            className={cn("text-xs font-mono min-w-[2rem] justify-center", {
              "bg-yellow-50 text-yellow-700 border-yellow-200": rank <= 3,
              "bg-blue-50 text-blue-700 border-blue-200":
                rank > 3 && rank <= 10,
              "bg-gray-50 text-gray-600 border-gray-200": rank > 10,
            })}
          >
            #{rank}
          </Badge>
        )}

        {/* Crypto Image */}
        {image && (
          <img
            src={image}
            alt={`${name} logo`}
            className="h-8 w-8 rounded-full flex-shrink-0"
            onError={handleImageError}
            loading="lazy"
          />
        )}

        {/* Crypto Info */}
        <div className="flex flex-col min-w-0 flex-1">
          <span className="font-semibold text-foreground uppercase hover:text-primary transition-colors">
            {symbol}
          </span>
          <span className="text-sm text-muted-foreground truncate">{name}</span>
        </div>
      </div>

      {/* Price Display */}
      <div className="ml-4 flex-shrink-0">
        <PriceDisplay coin={coin} />
      </div>

      {/* Watchlist Button */}
      <WatchlistStarButton
        symbol={symbol}
        isWatched={isWatched}
        onToggle={onToggleWatchlist}
      />
    </Link>
  );
};
