import { Star } from "lucide-react";
import { useState } from "react";

export function WatchlistStarButton({
  symbol,
  isWatched,
  onToggle,
  size = "sm",
  disabled = false,
}) {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (disabled || isLoading) return;

    setIsLoading(true);
    try {
      await onToggle(symbol);
    } finally {
      setIsLoading(false);
    }
  };

  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isLoading}
      className="p-1 hover:bg-muted rounded transition-colors"
      aria-label={`${isWatched ? "Remove from" : "Add to"} watchlist`}
    >
      <Star
        data-testid="lucide-star"
        className={`${sizeClasses[size]} transition-all duration-200 ${
          isLoading ? "animate-pulse" : ""
        } ${
          isWatched
            ? "text-yellow-400 fill-yellow-400"
            : "text-muted-foreground hover:text-yellow-400"
        }`}
      />
    </button>
  );
}
