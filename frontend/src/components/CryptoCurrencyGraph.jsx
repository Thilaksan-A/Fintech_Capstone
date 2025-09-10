import { format, isBefore, parseISO, subHours } from "date-fns";
import { AlertCircle, BarChart3, RefreshCw, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";

import { API_BASE_URL } from "../config";
import { ExpertGraph } from "./ExpertGraph";
import { PriceGraph } from "./PriceGraph";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const TIMEFRAMES = {
  "1D": { label: "1D", days: 1, description: "Last 24 hours" },
  "1M": { label: "1M", days: 30, description: "Last month" },
  "3M": { label: "3M", days: 90, description: "Last 3 months" },
  ALL: { label: "All", days: null, description: "All available data" },
};

const GraphSkeleton = () => (
  <div data-testid="price-skeleton" className="space-y-4">
    <div className="flex justify-between items-center">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-4 w-24" />
    </div>
    <Skeleton className="h-80 w-full rounded-lg" />
    <div className="flex justify-center space-x-2">
      {[1, 2, 3, 4].map((i) => (
        <Skeleton key={i} className="h-8 w-16 rounded-full" />
      ))}
    </div>
  </div>
);

const TimeframeSelector = ({
  activeTimeframe,
  onTimeframeChange,
  isLoading,
}) => (
  <div className="flex flex-wrap justify-center gap-2 mb-6">
    {Object.entries(TIMEFRAMES).map(([key, { label, description }]) => (
      <Button
        key={key}
        variant={activeTimeframe === key ? "default" : "outline"}
        size="sm"
        onClick={() => onTimeframeChange(key)}
        disabled={isLoading}
        className="min-w-[3rem] transition-all duration-200"
        title={description}
      >
        {label}
      </Button>
    ))}
  </div>
);

const DataRangeAlert = ({ rangeText }) => (
  <Alert className="mb-4 border-amber-200 bg-amber-50">
    <AlertCircle className="h-4 w-4 text-amber-600" />
    <AlertDescription className="text-amber-700">
      <strong>Data not current:</strong> Showing data from {rangeText}
    </AlertDescription>
  </Alert>
);

const ErrorState = ({ onRetry, error }) => (
  <Card className="border-red-200 bg-red-50">
    <CardContent className="pt-6 text-center">
      <AlertCircle className="h-12 w-12 mx-auto text-red-500 mb-4" />
      <h3 className="font-semibold text-red-900 mb-2">
        Failed to load chart data
      </h3>
      <p className="text-sm text-red-700 mb-4">
        {error || "Unable to fetch price history. Please try again."}
      </p>
      <Button onClick={onRetry} variant="outline" size="sm">
        <RefreshCw className="h-4 w-4 mr-2" />
        Retry
      </Button>
    </CardContent>
  </Card>
);

export const CryptoCurrencyGraph = ({ symbol }) => {
  const [activeTimeframe, setActiveTimeframe] = useState("1D");
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [graphType, setGraphType] = useState("overview");

  const fetchData = async (timeframe) => {
    setIsLoading(true);
    setError(null);

    try {
      const url = `${API_BASE_URL}/api/crypto/price_history?symbol=${symbol}&interval=${timeframe}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status}`);
      }

      const result = await response.json();
      setData(result || []);
    } catch (err) {
      console.error("Error fetching price data:", err);
      setError(err.message);
      setData([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData(activeTimeframe);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTimeframe, symbol]);

  const handleTimeframeChange = (timeframe) => {
    setActiveTimeframe(timeframe);
  };

  const handleRetry = () => {
    fetchData(activeTimeframe);
  };

  const formatRange = (start, end) => {
    return `${format(parseISO(start), "dd/MM/yyyy HH:mm")} to ${format(
      parseISO(end),
      "dd/MM/yyyy HH:mm"
    )}`;
  };

  const formatLabel = (ts) => {
    const date = parseISO(ts);
    if (activeTimeframe === "1H") return format(date, "HH:mm");
    if (activeTimeframe === "1D") return format(date, "HH:mm");
    if (activeTimeframe === "7D") return format(date, "MMM d");
    if (activeTimeframe === "1M") return format(date, "MMM d");
    return format(date, "MMM yyyy");
  };

  // Check if data is stale
  let showRange = false;
  let rangeText = "";
  if (data.length > 0) {
    const latest = data[0].timestamp;
    const oldest = data[data.length - 1].timestamp;
    if (isBefore(parseISO(latest), subHours(new Date(), 1))) {
      showRange = true;
      rangeText = formatRange(latest, oldest);
    }
  }

  return (
    <div className="p-4 mt-20 md:mt-24 space-y-6">
      {/* Timeframe Selector */}
      <TimeframeSelector
        activeTimeframe={activeTimeframe}
        onTimeframeChange={handleTimeframeChange}
        isLoading={isLoading}
      />

      {/* Data Range Warning */}
      {showRange && <DataRangeAlert rangeText={rangeText} />}

      {/* Loading State */}
      {isLoading && <GraphSkeleton />}

      {/* Error State */}
      {error && !isLoading && (
        <ErrorState onRetry={handleRetry} error={error} />
      )}

      {/* Success State */}
      {!isLoading && !error && data.length > 0 && (
        <div className="space-y-6">
          {/* Chart Container */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  {graphType === "overview" ? (
                    <TrendingUp className="h-5 w-5" />
                  ) : (
                    <BarChart3 className="h-5 w-5" />
                  )}
                  {graphType === "overview"
                    ? "Price Overview"
                    : "Technical Analysis"}
                </CardTitle>
                <Badge variant="outline">
                  {TIMEFRAMES[activeTimeframe].description}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {/* Graph Tabs */}
              <Tabs
                value={graphType}
                onValueChange={setGraphType}
                className="w-full"
              >
                <TabsList className="grid w-full grid-cols-2 mb-6">
                  <TabsTrigger
                    value="overview"
                    className="flex items-center gap-2"
                  >
                    <TrendingUp className="h-4 w-4" />
                    Overview
                  </TabsTrigger>
                  <TabsTrigger
                    value="analysis"
                    className="flex items-center gap-2"
                  >
                    <BarChart3 className="h-4 w-4" />
                    Analysis
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="mt-0">
                  <PriceGraph
                    symbol={symbol}
                    data={data}
                    formatLabel={formatLabel}
                  />
                </TabsContent>

                <TabsContent value="analysis" className="mt-0">
                  <ExpertGraph data={data} formatLabel={formatLabel} />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && data.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center">
            <TrendingUp className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-semibold mb-2">No chart data available</h3>
            <p className="text-sm text-muted-foreground mb-4">
              No price data found for {symbol} in the selected timeframe.
            </p>
            <Button onClick={handleRetry} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
