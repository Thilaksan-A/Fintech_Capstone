import axios from "axios";
import { useEffect, useState } from "react";

import { API_BASE_URL } from "../config";

import { BigNewsCard } from "@/components/BigNewsCard";

function News() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/crypto/news`, {
          params: { query: "cryptocurrency", refresh: false },
        });
        setData(res.data.slice(0, 15));
      } catch (err) {
        console.error("News fetch error: ", err);
      }
    };

    window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
    fetchNews();
  }, []);

  return (
    <div>
      <div className="flex flex-col h-full bg-custom-white p-6 mb-16">
        <span className="bg-gray-300/60 w-fit px-2 py-1 my-3 text-[12px] text-gray-700 rounded-full text-black self-center">
          Latest Articles
        </span>
        <div className="text-[34px]/12 text-center px-10 mb-3">
          Discover the latest news
        </div>
        <div className="text-center text-[14px] px-4 mb-4">
          Welcome to your fast pass to crypto. Here are the latest and greatest
          updates in the cryptoverse. Jump in, get informed, stay ahead.
        </div>
        {data.length > 0 &&
          data.map((article, index) => (
            <BigNewsCard key={index} data={article} />
          ))}
        {data.length === 0 &&
          [...Array(2).keys()].map((key) => (
            <BigNewsCard key={key} data={{}} />
          ))}
      </div>
    </div>
  );
}
export default News;
