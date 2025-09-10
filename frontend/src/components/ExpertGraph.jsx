import { Activity, BarChart3, Brain, Target } from "lucide-react";
import { useState } from "react";
import {
  Area,
  Bar,
  Brush,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export const ExpertGraph = (props) => {
  const { data, formatLabel } = props;
  const [showRSI, setShowRSI] = useState(false);
  const [showEMA, setShowEMA] = useState(false);
  const [showMACD, setShowMACD] = useState(false);
  const [showSentiment, setShowSentiment] = useState(false);

  const getSigFig = (val) => {
    if (val) {
      return val.toPrecision(4);
    }
    return null;
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length > 0) {
      const data = payload[0]["payload"];
      return (
        <Card data-testid="custom-tooltip" className="shadow-lg border-2">
          <CardContent className="p-3 space-y-1">
            <p className="font-medium text-sm">
              {formatLabel(data["timestamp"])}
            </p>
            <p className="text-sm">
              Price: <span className="font-semibold">${data["price"]}</span>
            </p>
            {showEMA && (
              <p data-testid="formatted-ema" className="text-sm text-red-600">
                EMA:{" "}
                <span className="font-semibold">${getSigFig(data["ema"])}</span>
              </p>
            )}
            {showRSI && (
              <p data-testid="formatted-rsi" className="text-sm text-blue-600">
                RSI:{" "}
                <span className="font-semibold">{getSigFig(data["rsi"])}</span>
              </p>
            )}
            {showMACD && (
              <p data-testid="formatted-macd" className="text-sm text-amber-600">
                MACD:{" "}
                <span className="font-semibold">{getSigFig(data["macd"])}</span>
              </p>
            )}
            {showSentiment && (
              <p data-testid="formatted-sentiment" className="text-sm text-green-600">
                Sentiment:{" "}
                <span className="font-semibold">
                  {getSigFig(data["sentiment"])}%
                </span>
              </p>
            )}
          </CardContent>
        </Card>
      );
    }
  };

  // Indicator configuration
  const indicators = [
    {
      key: "rsi",
      label: "RSI",
      icon: Target,
      isActive: showRSI,
      toggle: () => setShowRSI((prev) => !prev),
      color: "text-blue-600",
      bgColor: "bg-blue-100",
      description: "Relative Strength Index",
    },
    {
      key: "ema",
      label: "EMA",
      icon: Activity,
      isActive: showEMA,
      toggle: () => setShowEMA((prev) => !prev),
      color: "text-red-600",
      bgColor: "bg-red-100",
      description: "Exponential Moving Average",
    },
    {
      key: "macd",
      label: "MACD",
      icon: BarChart3,
      isActive: showMACD,
      toggle: () => setShowMACD((prev) => !prev),
      color: "text-amber-600",
      bgColor: "bg-amber-100",
      description: "Moving Average Convergence Divergence",
    },
    {
      key: "sentiment",
      label: "Sentiment",
      icon: Brain,
      isActive: showSentiment,
      toggle: () => setShowSentiment((prev) => !prev),
      color: "text-green-600",
      bgColor: "bg-green-100",
      description: "Market Sentiment",
    },
  ];

  const activeCount = indicators.filter(
    (indicator) => indicator.isActive
  ).length;

  return (
    <div className="space-y-4">
      {/* Chart Container */}
      <Card data-testid="custom-tooltip" className="overflow-hidden">
        <CardContent className="p-4">
          <ResponsiveContainer
            width="100%"
            height={350}
          >
            <ComposedChart data={data}>
              <defs>
                <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8884d8" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#8884d8" stopOpacity={0.1} />
                </linearGradient>
              </defs>

              <CartesianGrid vertical={false} horizontal={true} />
              <XAxis
                xAxisId={1}
                dataKey="timestamp"
                tickFormatter={formatLabel}
                tickLine={false}
              />
              <XAxis xAxisId={2} dataKey="timestamp" hide={true} />
              <YAxis
                yAxisId="price"
                domain={["auto", "auto"]}
                width={30}
                tickLine={false}
                axisLine={false}
                mirror={true}
                padding={{ bottom: 6 }}
                style={{ fontSize: "12px" }}
                orientation="right"
              />

              {/* Price data */}
              <Area
                yAxisId="price"
                xAxisId={1}
                type="monotone"
                dataKey="price"
                stroke="#8884d8"
                fill="url(#area)"
                activeDot={false}
              />

              {/* EMA data */}
              {showEMA && (
                <Line
                  yAxisId="price"
                  xAxisId={1}
                  type="monotone"
                  dataKey="ema"
                  stroke="red"
                  dot={false}
                />
              )}

              {/* MACD data */}
              {showMACD && (
                <YAxis yAxisId="macd" domain={["auto", "auto"]} hide={true} />
              )}
              {showMACD && (
                <Line
                  yAxisId="macd"
                  xAxisId={1}
                  type="monotone"
                  dataKey="macd"
                  stroke="brown"
                  dot={false}
                />
              )}

              {/* RSI data */}
              {showRSI && <YAxis yAxisId="rsi" domain={[0, 100]} hide={true} />}
              {showRSI && (
                <Line
                  yAxisId="rsi"
                  xAxisId={1}
                  type="monotone"
                  dataKey="rsi"
                  stroke="#3b82f6"
                  dot={false}
                />
              )}

              {/* Sentiment data */}
              {showSentiment && (
                <YAxis
                  yAxisId="sentiment"
                  width={30}
                  padding={{ top: 125, bottom: 4 }}
                  domain={[0, 100]}
                  axisLine={false}
                  tickLine={false}
                  mirror={true}
                  style={{ fontSize: "12px" }}
                  tickCount={3}
                />
              )}
              {showSentiment && (
                <Bar
                  yAxisId="sentiment"
                  xAxisId={2}
                  type="monotone"
                  dataKey="sentiment"
                  fill="green"
                  fillOpacity={0.25}
                />
              )}

              <Legend />
              <Tooltip content={CustomTooltip} />
              <Brush
                dataKey="timestamp"
                height={30}
                stroke="#8884d8"
                margin={{ top: 10 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Indicators Control Panel */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">
              Technical Indicators
            </CardTitle>
            <Badge variant="outline" className="text-xs">
              {activeCount} active
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Indicator Toggle Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {indicators.map((indicator) => {
              const IconComponent = indicator.icon;
              return (
                <Button
                  key={indicator.key}
                  variant={indicator.isActive ? "default" : "outline"}
                  size="sm"
                  onClick={indicator.toggle}
                  className={`h-auto p-3 flex flex-col gap-1 transition-all duration-200 ${
                    indicator.isActive
                      ? `${indicator.bgColor} ${indicator.color} border-current hover:${indicator.bgColor}`
                      : "hover:bg-muted"
                  }`}
                >
                  <IconComponent className="h-4 w-4" />
                  <span className="font-medium text-xs">{indicator.label}</span>
                </Button>
              );
            })}
          </div>

          {/* Active Indicators Summary */}
          {activeCount > 0 && (
            <>
              <Separator />
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground font-medium">
                  Active Indicators:
                </p>
                <div className="flex flex-wrap gap-1">
                  {indicators
                    .filter((indicator) => indicator.isActive)
                    .map((indicator) => (
                      <Badge
                        key={indicator.key}
                        variant="secondary"
                        className={`text-xs ${indicator.color} ${indicator.bgColor}`}
                      >
                        {indicator.description}
                      </Badge>
                    ))}
                </div>
              </div>
            </>
          )}

          {/* Help Text */}
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-xs text-muted-foreground">
              <strong>Tip:</strong> Click the indicators above to overlay them
              on the chart. Multiple indicators can be active simultaneously for
              comprehensive analysis.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
