import { Skeleton } from "@mui/material";
import { MoveRight } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const bckup_img_url = "https://www.centralbank.net/globalassets/images/articles/crypto-par-2.png?v=1D896BD3A634800";

export const BigNewsCard = ({ data }) => {
  const { title, description, urlToImage, content, source, url, publishedAt } = data;
  const [ readTime, setReadTime ] = useState(1);
  const [isExpanded, setIsExpanded] = useState(false);

  const formattedDate = useMemo(() => {
    if (!publishedAt) return "";
    const date = new Date(publishedAt);
    return date.toDateString();
  }, [publishedAt]);

  useEffect(() => {
    const wpm = 150;
    if (content) {
      const wordCount = content.trim().split(/\s+/).length;
      setReadTime(Math.max(1, Math.floor(wordCount / wpm) + 1));
    }
  }, [content]);
  

  return (
  <div className={`relative ${title ? "bg-gray-800" : "bg-white" } my-3 rounded-3xl shadow-lg overflow-hidden`}>
    {!title && (
      <Skeleton data-testid="skeleton-loader" variant="rectangular" height={312} className="w-full rounded-3xl p-4 flex flex-col" />
    )}

    {title && (
      <>
        <div
          data-testid="news-card-bg"
          className=" absolute inset-0 bg-cover bg-center rounded-3xl
            [mask-image:linear-gradient(to_bottom,rgba(0,0,0,1)_0%,rgba(0,0,0,0.9)_60%,rgba(0,0,0,0.3)_100%)]
            [-webkit-mask-image:linear-gradient(to_bottom,rgba(0,0,0,1)_0%,rgba(0,0,0,0.9)_60%,rgba(0,0,0,0.3)_100%)]
          "
          style={{ backgroundImage: `url("${urlToImage ? urlToImage : bckup_img_url}")` }}
        />

        <div className="relative z-10 w-full h-72 p-4 flex flex-col">
          <span className="self-end bg-white/70 w-fit px-2 py-1 text-[12px] rounded-full text-black">
            {readTime} min read
          </span>
          <div className="mt-auto bg-white/70 w-fit px-2 py-1 text-[12px] rounded-full text-black">
            {formattedDate}
          </div>
          <span className="mt-1 text-shadow-md text-white font-bold text-xl">
            {title}
          </span>
          <a
            className="pt-2 pr-4 flex items-center text-[14px] text-gray-300 text-shadow-md cursor-pointer"
            href={url} target="_blank"
          >
            <p>Read more</p>
            <MoveRight className="w-5 ml-2 mt-1" />
          </a>
        </div>
      </>
    )}
  </div>
)
};
