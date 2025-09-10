import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { AlertCircle, RefreshCw, Sparkles, TrendingUp } from "lucide-react";
import { useMemo } from "react";

import { API_BASE_URL } from "../config";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";

export const fetchForecast = async (symbol) => {
  const token = localStorage.getItem("token");
  if (!token) {
    throw new Error("Authentication required");
  }

  const response = await axios.post(
    `${API_BASE_URL}/api/crypto/forecast`,
    { symbol },
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};

const SENTIMENT_CONFIG = {
  BUY: {
    emoji: "👍",
    color: "text-green-600",
    bgColor: "bg-green-50",
    borderColor: "border-green-200",
    label: "Strong Buy",
    description: "Market indicators suggest upward momentum",
  },
  SELL: {
    emoji: "👎",
    color: "text-red-600",
    bgColor: "bg-red-50",
    borderColor: "border-red-200",
    label: "Strong Sell",
    description: "Market indicators suggest downward pressure",
  },
  HOLD: {
    emoji: "🤷",
    color: "text-amber-600",
    bgColor: "bg-amber-50",
    borderColor: "border-amber-200",
    label: "Hold",
    description: "Market conditions suggest maintaining position",
  },
};

const LoadingSkeleton = () => (
  <Card>
    <CardHeader className="text-center">
      <CardTitle className="flex items-center justify-center gap-2">
        <Skeleton className="h-5 w-5 rounded" />
        <Skeleton className="h-6 w-32" />
      </CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="text-center space-y-3">
        <Skeleton className="h-16 w-16 rounded-full mx-auto" />
        <Skeleton className="h-8 w-24 mx-auto" />
        <Skeleton className="h-4 w-48 mx-auto" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-2 w-full" />
      </div>
    </CardContent>
  </Card>
);

const ErrorState = ({ error, onRetry }) => (
  <Card className="border-red-200">
    <CardContent>
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>{error}</span>
          <Button variant="outline" size="sm" onClick={onRetry}>
            <RefreshCw className="h-3 w-3 mr-1" />
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    </CardContent>
  </Card>
);

const SentimentDisplay = ({ recommendation, up5pct }) => {
  const config = SENTIMENT_CONFIG[recommendation] || SENTIMENT_CONFIG.HOLD;

  return (
    <div
      className={`${config.bgColor} ${config.borderColor} border-2 rounded-xl p-6 text-center transition-all duration-200`}
    >
      {/* Icon and Emoji */}
      <div className="flex items-center justify-center gap-3 mb-4">
        <div className="text-4xl">{config.emoji}</div>
      </div>

      {/* Recommendation */}
      <div className="space-y-2">
        <Badge
          variant="outline"
          className={`${config.color} ${config.borderColor} text-lg font-bold px-4 py-2`}
        >
          {config.label}
        </Badge>
        <p className="text-sm text-muted-foreground max-w-xs mx-auto">
          {config.description}
        </p>
      </div>

      {/* Confidence Metric */}
      {up5pct !== null && up5pct !== undefined && (
        <div className="mt-4 space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              5% Upward Movement (24h)
            </span>
            <span className="font-semibold">{up5pct.toFixed(1)}%</span>
          </div>
          <Progress
            value={up5pct}
            className="h-2"
            aria-label={`${up5pct.toFixed(1)}% probability`}
          />
          <p className="text-xs text-muted-foreground">
            Probability based on current market conditions
          </p>
        </div>
      )}
    </div>
  );
};

const ForecastReasoning = ({ reasoning }) => (
  <Collapsible>
    <CollapsibleTrigger asChild>
      <Button variant="outline" size="lg" className="w-full justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4" />
          View Forecast Analysis
        </div>
        <span className="text-xs text-muted-foreground">Click to expand</span>
      </Button>
    </CollapsibleTrigger>
    <CollapsibleContent className="mt-1">
      <Card>
        <CardContent className="pt-0">
          <div className="prose prose-sm max-w-none">
            <p data-testid="forecast-reasoning" className="text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap">
              {reasoning}
            </p>
          </div>
        </CardContent>
        <CardFooter className="justify-end">
          <span className="text-xs text-muted-foreground">
            Powered by Gemini AI
          </span>
        </CardFooter>
      </Card>
    </CollapsibleContent>
  </Collapsible>
);

const SentimentCard = ({ crypto }) => {
  const {
    data: forecast,
    isLoading,
    error,
    refetch,
    isRefetching,
  } = useQuery({
    queryKey: ["forecast", crypto?.symbol],
    queryFn: () => fetchForecast(crypto.symbol),
    enabled: !!crypto?.symbol && !!localStorage.getItem("token"),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error) => {
      // Don't retry on auth errors
      if (error.response?.status === 401 || error.response?.status === 403) {
        return false;
      }
      return failureCount < 2;
    },
    onError: (error) => {
      console.error("Forecast fetch error:", error);
    },
  });

  const sentimentData = useMemo(() => {
    if (!forecast) return null;

    return {
      recommendation: forecast.recommendation,
      up5pct: forecast.up_5pct_24h,
      reasoning: forecast.reasoning,
    };
  }, [forecast]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="px-4">
        <LoadingSkeleton />
      </div>
    );
  }

  // Show error state
  if (error) {
    const errorMessage =
      error.response?.data?.message ||
      error.message ||
      "Failed to load sentiment data";

    return (
      <div className="px-4">
        <ErrorState error={errorMessage} onRetry={() => refetch()} />
      </div>
    );
  }

  // Show empty state
  if (!sentimentData) {
    return (
      <div className="px-4">
        <Card>
          <CardContent className="pt-6 text-center">
            <AlertCircle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-semibold mb-2">No sentiment data available</h3>
            <p className="text-sm text-muted-foreground">
              Unable to generate forecast for {crypto?.symbol}
            </p>
            <Button
              variant="outline"
              onClick={() => refetch()}
              className="mt-4"
              disabled={isRefetching}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${isRefetching ? "animate-spin" : ""}`}
              />
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="px-4 space-y-4">
      {/* Main Sentiment Card */}
      <Card>
        <CardHeader className="text-center">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center justify-center gap-2 flex-1">
              <TrendingUp className="h-5 w-5" />
              Market Sentiment
            </CardTitle>
            {/* Refresh button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => refetch()}
              disabled={isRefetching}
              className="h-8 w-8 p-0"
            >
              <RefreshCw
                className={`h-4 w-4 ${isRefetching ? "animate-spin" : ""}`}
              />
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            AI-powered analysis for {crypto?.symbol}
          </p>
        </CardHeader>
        <CardContent>
          <SentimentDisplay
            recommendation={sentimentData.recommendation}
            up5pct={sentimentData.up5pct}
          />
        </CardContent>
      </Card>

      {/* Forecast Reasoning */}
      {sentimentData.reasoning && (
        <ForecastReasoning reasoning={sentimentData.reasoning} />
      )}

      {/* Disclaimer */}
      <Card className="bg-muted/30">
        <CardContent>
          <div className="text-center">
            <p className="text-xs text-muted-foreground">
              <strong>Disclaimer:</strong> This analysis is for informational
              purposes only and should not be considered as financial advice.
              Always do your own research before making investment decisions.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SentimentCard;
