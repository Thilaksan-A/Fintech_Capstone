import { useMemo, useState } from "react";

export const SmallNewsCard = ({ data }) => {
  const { title, description, url_image, content, source_url, timestamp } = data;
  const [isExpanded, setIsExpanded] = useState(false);

  const formattedDate = useMemo(() => {
    if (!timestamp) return "";
    const date = new Date(timestamp);
    return date.toDateString();
  }, [timestamp]);

  return (
    <div>
      <div
        onClick={() => setIsExpanded(prev => !prev)}
        className="bg-white rounded-lg shadow-xs my-2 flex flex-row cursor-pointer"
      >
        <img
          src={url_image}
          alt={title}
          className="h-24 w-30 rounded-l-lg shadow-r-sm object-cover"
        />
        <div className="ml-4 pt-2 flex flex-col space-y-4">
          <p className="text-[15px]">{title}</p>
          <div className="text-[13px] text-gray-600 bottom-0 flex flex-row">
            <span>{formattedDate}</span>
            <p className="ml-4">5 min read</p>
          </div>
        </div>
      </div>
      {isExpanded && <div>hello</div>}
    </div>
  );
};
