import axios from "axios";
import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Globe,
  Info,
  ShoppingCart,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { CryptoCurrencyGraph } from "@/components/CryptoCurrencyGraph";
import { CryptoCurrencyHeader } from "@/components/CryptoCurrencyHeader";
import NewsHub from "@/components/NewsHub";
import { PurchasePlatformsList } from "@/components/PurchasePlatformsList";
import SentimentCard from "@/components/SentimentCard";
import StatsCard from "@/components/StatsCard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { API_BASE_URL } from "@/config";

export const ExpandableDescription = ({ description, name }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const shouldShowReadMore = description && description.length > 200;

  return (
    <div className="space-y-2">
      <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
        What is {name}?
      </h4>
      <div className="relative">
        <div
          className={`text-sm leading-relaxed text-foreground transition-all duration-300 ${
            !isExpanded && shouldShowReadMore
              ? "max-h-20 overflow-hidden"
              : "max-h-none"
          }`}
        >
          {description}
        </div>

        {/* Gradient overlay for truncated text */}
        {!isExpanded && shouldShowReadMore && (
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white to-transparent pointer-events-none" />
        )}
      </div>

      {shouldShowReadMore && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-0 h-auto font-medium text-blue-600 hover:text-blue-700 hover:bg-transparent"
        >
          {isExpanded ? (
            <span className="flex items-center gap-1">
              Read Less
              <ChevronUp className="h-3 w-3" />
            </span>
          ) : (
            <span className="flex items-center gap-1">
              Read More
              <ChevronDown className="h-3 w-3" />
            </span>
          )}
        </Button>
      )}
    </div>
  );
};

function Cryptocurrency() {
  const { id } = useParams();
  const [rsi, setRsi] = useState(0);
  const [macd, setMacd] = useState(0);
  const [ema, setEma] = useState(0);
  const [volume, setVolume] = useState(0);
  const [marketCap, setMarketCap] = useState(0);
  const [sentiment, setSentiment] = useState(null);
  const [sentimentNum, setSentimentNum] = useState(0);
  const [name, setName] = useState("");
  const [metadata, setMetadata] = useState({});
  const cryptoSymbol = id.toUpperCase();
  const [loaded, setLoaded] = useState({
    sentiment: false,
    indicators: false,
  });

  const fetchMetadata = async (symbol) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/crypto/metadata`, {
        params: {
          symbol: symbol,
        },
      });
      const data = res.data;
      setName(data.name);
      setMetadata({
        description: data.description,
        image: data.image,
        categories: data.categories,
        homepage_url: data.homepage_url,
        purchase_platforms: data.purchase_platforms,
      });
      setVolume(data.volume);
      setMarketCap(data.marketcap);
    } catch (e) {
      console.error("Unable to fetch metadata:", e);
    }
  };

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
    fetchMetadata(cryptoSymbol);
  }, []);

  const fetchSentiment = async (symbol) => {
    try {
      const { data } = await axios.get(
        `${API_BASE_URL}/api/crypto/sentiment/all`,
        {
          params: { symbol },
        }
      );

      const {
        normalised_up_percentage: positive,
        normalised_down_percentage: negative,
      } = data;

      let sentimentScore;
      if (positive > negative) sentimentScore = positive * 100;
      else sentimentScore = negative * 100;

      let sentimentLabel = "HOLD";
      if (sentimentScore >= 70) sentimentLabel = "BUY";
      else if (sentimentScore <= 40) sentimentLabel = "SELL";
      setSentimentNum(sentimentScore);
      setSentiment(sentimentLabel);
      setLoaded((l) => ({ ...l, sentiment: true }));
    } catch (err) {
      console.error("Sentiment fetch error:", err.message);
      setLoaded((l) => ({ ...l, sentiment: false }));
      setSentiment(null);
    }
  };

  useEffect(() => {
    if (cryptoSymbol) {
      fetchSentiment(cryptoSymbol);
    }
  }, [cryptoSymbol]);

  const fetchIndicators = async (cryptoSymbol) => {
    try {
      const res = await axios.get(
        `${API_BASE_URL}/api/crypto/latest_indicators`,
        {
          params: {
            symbol: cryptoSymbol,
          },
        }
      );
      setRsi(res.data.rsi);
      setMacd(res.data.macd);
      setEma(res.data.ema);
      setLoaded((l) => ({ ...l, indicators: true }));
    } catch (e) {
      console.error("Unable to fetch indicator values, ", e);
      setRsi(null);
      setMacd(null);
      setEma(null);
      setLoaded((l) => ({ ...l, indicators: false }));
    }
  };

  useEffect(() => {
    fetchIndicators(cryptoSymbol);
  }, [cryptoSymbol]);

  const crypto = {
    symbol: id?.toUpperCase() || "ETH",
    price: 19.26,
    timestamp: "2025-06-30 14:30:00+10:00",
    sentiment: sentiment,
    onWatchlist: true,
    forecast: "65% short term upward potential",
    stats: {
      marketCap: marketCap,
      volume: volume,
      rsi: rsi,
      macd: macd,
      ema: ema,
      sentiment: sentimentNum,
    },
    loaded: loaded,
  };

  const home_url = (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <a
          href={metadata.homepage_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
        >
          <Globe className="h-4 w-4" />
          Official Website
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col gap-6">
      <CryptoCurrencyHeader
        symbol={crypto.symbol}
        name={name}
        image={metadata.image}
      />

      {/* Graph Section */}
      <CryptoCurrencyGraph symbol={cryptoSymbol.toUpperCase()} />

      <SentimentCard crypto={crypto} />
      <StatsCard crypto={crypto} />

      {/* Revamped Information Section */}
      <div className="mx-4 space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-5 w-5" />
              About {name}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Description */}
            {metadata.description && (
              <ExpandableDescription
                description={metadata.description}
                name={name}
              />
            )}

            <Separator />

            {/* Links and Resources */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Links & Resources
              </h4>
              {home_url}
            </div>

            {/* Purchase Platforms */}
            {metadata.purchase_platforms &&
              metadata.purchase_platforms.length > 0 && (
                <>
                  <Separator />
                  <div className="space-y-3">
                    <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide flex items-center gap-2">
                      <ShoppingCart className="h-4 w-4" />
                      Where to Buy
                    </h4>
                    <PurchasePlatformsList
                      name={name}
                      platforms={metadata.purchase_platforms}
                    />
                  </div>
                </>
              )}
          </CardContent>
        </Card>
      </div>

      <div className="mb-17">
        <NewsHub cryptoSymbol={id} />
      </div>
    </div>
  );
}

export default Cryptocurrency;
