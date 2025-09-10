import { ExternalLink } from "lucide-react";

import { CryptoCurrencyList } from "@/components/CryptoCurrencyList";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { WatchlistSection } from "@/components/WatchlistSection";

function Dashboard() {
  return (
    <div className="w-full min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="flex flex-col items-center justify-between px-4 py-4">
        <h1 className="text-2xl font-semibold tracking-wide">SAFEGUARD</h1>
        <span className="font-sm flex flex-row">
          Powered by&nbsp;
          <a
            className="flex flex-row items-center text-custom-primary"
            target="_blank"
            href="https://www.coingecko.com/"
          >
            CoinGecko API
            <ExternalLink className="h-3" />
          </a>
        </span>
      </div>

      {/* Favourites Watchlist */}
      <div className="mx-4 mb-4">
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem
            value="watchlist"
            className="border rounded-lg bg-white shadow"
          >
            <AccordionTrigger className="px-4 py-3 font-medium text-lg hover:no-underline">
              My Watchlist
            </AccordionTrigger>
            <AccordionContent className="px-0 pb-0">
              <WatchlistSection />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>

      {/* Top 10 Cryptocurrencies */}
      <CryptoCurrencyList />
    </div>
  );
}

export default Dashboard;
