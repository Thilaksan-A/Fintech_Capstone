import {
  Activity,
  BarChart3,
  Brain,
  ChevronDown,
  ChevronUp,
  DollarSign,
  Minus,
  Target,
  TrendingDown,
  TrendingUp,
  Volume2,
} from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";

// Stat configuration with icons and descriptions
const STAT_CONFIG = {
  marketCap: {
    icon: DollarSign,
    label: "Market Cap",
    description: "Total market value of all coins in circulation.",
    format: (value) => `$${(value / 1e9).toFixed(2)}B`,
    color: "text-blue-600",
  },
  volume: {
    icon: Volume2,
    label: "24h Volume",
    description: "Total trading volume in the last 24 hours.",
    format: (value) => `$${(value / 1e6).toFixed(2)}M`,
    color: "text-purple-600",
  },
  macd: {
    icon: BarChart3,
    label: "MACD",
    description: "Trend momentum indicator showing market direction.",
    format: (value) => parseFloat(value).toFixed(4),
    color: "text-orange-600",
    getIndicator: (value) => {
      const num = parseFloat(value);
      if (num > 0)
        return {
          variant: "default",
          className: "bg-green-100 text-green-800",
          icon: TrendingUp,
          text: "Bullish",
        };
      if (num < 0)
        return {
          variant: "destructive",
          className: "bg-red-100 text-red-800",
          icon: TrendingDown,
          text: "Bearish",
        };
      return {
        variant: "secondary",
        className: "bg-gray-100 text-gray-800",
        icon: Minus,
        text: "Neutral",
      };
    },
  },
  ema: {
    icon: Activity,
    label: "EMA",
    description:
      "Exponential moving average giving more weight to recent prices.",
    format: (value) => `$${parseFloat(value).toFixed(2)}`,
    color: "text-green-600",
  },
  rsi: {
    icon: Target,
    label: "RSI",
    description: "Measures if the asset is overbought (>70) or oversold (<30).",
    format: (value) => parseFloat(value).toFixed(1),
    color: "text-red-600",
    getIndicator: (value) => {
      const num = parseFloat(value);
      if (num >= 70)
        return { text: "Overbought", className: "bg-red-100 text-red-800" };
      if (num <= 30)
        return { text: "Oversold", className: "bg-blue-100 text-blue-800" };
      return { text: "Neutral", className: "bg-gray-100 text-gray-800" };
    },
    showProgress: true,
    progressMax: 100,
  },
  sentiment: {
    icon: Brain,
    label: "Sentiment",
    description: "Market sentiment score from 0 (bearish) to 100 (bullish).",
    format: (value) => parseFloat(value).toFixed(2),
    color: "text-indigo-600",
    getIndicator: (value) => {
      const num = parseFloat(value);
      if (num >= 60)
        return { text: "Bullish", className: "bg-green-100 text-green-800" };
      if (num <= 40)
        return { text: "Bearish", className: "bg-red-100 text-red-800" };
      return { text: "Neutral", className: "bg-yellow-100 text-yellow-800" };
    },
    showProgress: true,
    progressMax: 100,
  },
};

const StatItem = ({ value, config }) => {
  const IconComponent = config.icon;
  const formattedValue = config.format(value);
  const indicator = config.getIndicator ? config.getIndicator(value) : null;

  return (
    <div
      className={`p-4 border-l-4 border-l-current ${config.color} bg-muted/20 rounded-r-lg`}
    >
      <div className="flex items-center gap-3 mb-2">
        <IconComponent className={`h-5 w-5 ${config.color}`} />
        <div className="flex-1">
          <div className="text-sm font-medium text-muted-foreground">
            {config.label}
          </div>
          <div className="text-xl font-bold text-foreground mt-1">
            {formattedValue}
          </div>
        </div>
      </div>

      {/* Simple description */}
      <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
        {config.description}
      </p>

      {/* Progress bar for RSI and Sentiment */}
      {config.showProgress && (
        <div className="mb-3 space-y-2">
          <Progress
            value={
              config.progressMax === 1
                ? parseFloat(value) * 100
                : parseFloat(value)
            }
            className="h-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0</span>
            <span className="font-medium">
              {parseFloat(value).toFixed(2)}/{config.progressMax}
            </span>
            <span>{config.progressMax}</span>
          </div>
        </div>
      )}

      {/* Indicator Badge */}
      {indicator && (
        <div className="flex items-center gap-2">
          {indicator.icon && <indicator.icon className="h-4 w-4" />}
          <Badge
            data-testid={`${config.label.toLowerCase()}-indicator`}
            variant={indicator.variant || "secondary"}
            className={indicator.className || ""}
          >
            {indicator.text}
          </Badge>
        </div>
      )}
    </div>
  );
};

const StatsCard = ({ crypto }) => {
  const [showAllIndicators, setShowAllIndicators] = useState(false);

  if (!crypto?.stats) {
    return (
      <div className="mx-4 mt-6">
        <Card>
          <CardContent className="pt-6 text-center">
            <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-semibold mb-2">No statistics available</h3>
            <p className="text-sm text-muted-foreground">
              Statistics data is not available for this cryptocurrency.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const stats = crypto.stats;

  // Define which stats to show by default
  const primaryStats = ["marketCap", "volume"];
  const technicalStats = ["macd", "ema", "rsi", "sentiment"];
  const visibleTechnicalStats = showAllIndicators
    ? technicalStats
    : technicalStats.slice(0, 2);

  return (
    <div className="mx-4 mt-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Market Statistics
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Key technical indicators and market metrics
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Market Metrics Section */}
          <div className="space-y-4">
            <h4 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
              Market Metrics
            </h4>
            <div className="space-y-3">
              {primaryStats.map((statKey) => (
                <StatItem
                  key={statKey}
                  value={stats[statKey]}
                  config={STAT_CONFIG[statKey]}
                />
              ))}
            </div>
          </div>

          <Separator />

          {/* Technical Indicators Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
                Technical Indicators
              </h4>
              {technicalStats.length > 2 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAllIndicators(!showAllIndicators)}
                  className="text-xs"
                >
                  {showAllIndicators ? "Show Less" : "Show More"}
                  {showAllIndicators ? (
                    <ChevronUp className="h-3 w-3 ml-1" />
                  ) : (
                    <ChevronDown className="h-3 w-3 ml-1" />
                  )}
                </Button>
              )}
            </div>

            <div className="space-y-3">
              {visibleTechnicalStats.map((statKey) => (
                <StatItem
                  key={statKey}
                  value={stats[statKey]}
                  config={STAT_CONFIG[statKey]}
                />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default StatsCard;
