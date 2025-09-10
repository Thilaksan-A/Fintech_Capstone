import { ExternalLink, ShoppingCart } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

export const PurchasePlatformsList = ({ name, platforms }) => {
  const [parsedPlatforms, setParsedPlatforms] = useState([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (platforms) {
      // Handle both string and array formats
      if (typeof platforms === "string") {
        setParsedPlatforms(platforms.split(", ").filter(Boolean));
      } else if (Array.isArray(platforms)) {
        setParsedPlatforms(platforms);
      }
    }
  }, [platforms]);

  if (!parsedPlatforms || parsedPlatforms.length === 0) {
    return (
      <div className="text-center py-4 bg-muted/50 rounded-lg">
        <ShoppingCart className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
        <p className="text-sm text-muted-foreground">
          No purchase platforms available for {name}
        </p>
      </div>
    );
  }

  const PlatformCard = ({ platform, index }) => (
    <div className="group relative">
      <Button
        variant="outline"
        size="sm"
        className="w-full justify-between h-auto p-4 hover:shadow-md transition-all duration-200"
        asChild
      >
        <a
          href={`https://www.google.com/search?q=${encodeURIComponent(
            platform
          )} crypto exchange`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-between w-full"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
              {platform.charAt(0).toUpperCase()}
            </div>
            <div className="text-left">
              <span className="font-medium text-foreground">{platform}</span>
              <p className="text-xs text-muted-foreground">
                Search for {platform} exchange
              </p>
            </div>
          </div>
          <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
        </a>
      </Button>
    </div>
  );

  return (
    <div className="space-y-3">
      {/* Inline display for small number of platforms */}
      {parsedPlatforms.length <= 3 ? (
        <>
          <p className="text-sm text-muted-foreground">
            You can purchase {name} on the following platforms:
          </p>
          <div className="grid grid-cols-1 gap-2">
            {parsedPlatforms.map((platform, index) => (
              <PlatformCard key={index} platform={platform} index={index} />
            ))}
          </div>
        </>
      ) : (
        <>
          {/* Show first 2 platforms + "View All" button for many platforms */}
          <p className="text-sm text-muted-foreground">
            You can purchase {name} on {parsedPlatforms.length} platforms:
          </p>
          <div className="space-y-2">
            {parsedPlatforms.slice(0, 2).map((platform, index) => (
              <PlatformCard key={index} platform={platform} index={index} />
            ))}
          </div>

          {/* Modal for all platforms */}
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="w-full">
                <ShoppingCart className="h-4 w-4 mr-2" />
                View All {parsedPlatforms.length} Platforms
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <ShoppingCart className="h-5 w-5" />
                  Where to Buy {name}
                </DialogTitle>
                <DialogDescription>
                  {name} is available on {parsedPlatforms.length} different
                  platforms. Click on any platform to search for it.
                </DialogDescription>
              </DialogHeader>

              <Separator />

              <ScrollArea className="max-h-96 pr-4">
                <div className="space-y-2">
                  {parsedPlatforms.map((platform, index) => (
                    <PlatformCard
                      key={index}
                      platform={platform}
                      index={index}
                    />
                  ))}
                </div>
              </ScrollArea>

              <Separator />

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                <p className="text-xs text-amber-800">
                  <strong>Disclaimer:</strong> Always verify the authenticity of
                  trading platforms and conduct your own research before making
                  any purchases.
                </p>
              </div>
            </DialogContent>
          </Dialog>
        </>
      )}

      {/* Always show disclaimer */}
      <div className="bg-muted/50 rounded-lg p-3">
        <p className="text-xs text-muted-foreground">
          <strong>Note:</strong> Links will search for the platform. Always
          verify authenticity and conduct your own research before making
          purchases.
        </p>
      </div>
    </div>
  );
};
