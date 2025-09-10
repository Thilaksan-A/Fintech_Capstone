import Skeleton from "@mui/material/Skeleton";
import { ArrowLeft } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { WatchlistStarButton } from "./WatchlistStarButton";

import { useWatchlist } from "@/hooks/useWatchlist";

export const CryptoCurrencyHeader = ({ symbol, name, image }) => {
  const [price, setPrice] = useState(0);
  const socketRef = useRef(null);
  const navigate = useNavigate();
  const {
    loading: watchlistLoading,
    toggleWatchlist,
    isWatched,
  } = useWatchlist();

  useEffect(() => {
    if (socketRef.current) {
      socketRef.current.onmessage = null;
      socketRef.current.close();
      socketRef.current = null;
    }

    const ws = new WebSocket(
      `wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}usdt@kline_1s`
    );
    socketRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected for", symbol);
    };

    ws.onmessage = (event) => {
      try {
        const {
          k: { c },
        } = JSON.parse(event.data);
        const price = parseFloat(c);
        let formattedPrice;
        if (price < 0.01) {
          formattedPrice = price.toFixed(8);
        } else {
          formattedPrice = price.toFixed(2);
        }
        setPrice(formattedPrice);
      } catch (err) {
        console.error("Failed to parse message", err);
      }
    };

    ws.onerror = (err) => console.error("WebSocket error", err);

    ws.onclose = (event) => {
      console.log(`WebSocket closed for ${symbol}`, event);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [symbol]);

  return (
    <div className="fixed top-0 w-full z-50 bg-white shadow-md flex items-center justify-between h-20 md:h-24 px-6 md:px-4 pt-2 pb-2 md:pb-4 rounded-b-3xl">
      <button className="cursor-pointer" onClick={() => navigate("/")}>
        <ArrowLeft />
      </button>
      {(!image || price == 0) && (
        <div className="flex flex-col items-center">
          <span className="text-lg font-medium tracking-widest flex flex-row items-center">
            <Skeleton
              data-testid="price-skeleton"
              variant="circular"
              className="mr-1"
              width={32}
              height={32}
            />
            <Skeleton data-testid="price-skeleton" className="w-10 h-90" />
          </span>
          <Skeleton data-testid="price-skeleton" className="w-40 py-2" />
        </div>
      )}
      {image && price != 0 && (
        <div className="flex flex-col items-center">
          <span className="text-lg font-medium tracking-widest flex flex-row items-center">
            <img src={image} alt={`${name} logo`} className="h-8 mr-1" />
            {symbol}
          </span>
          <span className="text-3xl font-bold">${price}</span>
        </div>
      )}
      <WatchlistStarButton
        loading={watchlistLoading}
        symbol={symbol}
        onToggle={toggleWatchlist}
        isWatched={isWatched(symbol)}
        size="lg"
      />
    </div>
  );
};
