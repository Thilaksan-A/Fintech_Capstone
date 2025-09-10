import { Link } from "react-router-dom";

import { WatchlistStarButton } from "@/components/WatchlistStarButton";


export const Favourites = ({ favourites, watchlistState, onToggle }) => {
  if (favourites.length > 0) {
    return (
      <div className="bg-white rounded-b-lg shadow px-4 py-2">
        {favourites.map((coin) => (
          <div key={coin.symbol} className="flex items-center justify-between py-2 border-b last:border-b-0">
            <div className="flex items-center gap-2">
              <WatchlistStarButton
                symbol={coin.symbol}
                isWatched={watchlistState.has(coin.symbol)}
                onToggle={onToggle}
              />
              <img src={coin.image} alt='' className='h-6' />
              <div className="flex flex-col">
                <Link to={`/cryptocurrency/${coin.symbol.toLowerCase()}`} className="flex items-center gap-2">
                  <span className="font-semibold">{coin.symbol}</span>
                  <span className="text-sm text-gray-500">{coin.name}</span>
                </Link>
              </div>
            </div>
            <span className={coin.priceUp ? 'text-green-600' : 'text-red-600'}>
              {coin.priceUp ? `$${coin.price} ↑` : `$${coin.price} ↓`}
            </span>
          </div>
        ))}
      </div>
    )
  }
  else {
    return (
      <div className="bg-white rounded-b-lg shadow px-4 py-2">
        <p className="text-gray-500 text-center py-4">No favourites added yet.</p>
      </div>
    );
  }


}