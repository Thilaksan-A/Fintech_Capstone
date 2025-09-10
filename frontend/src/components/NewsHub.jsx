import axios from 'axios';
import { useEffect, useState } from 'react';

import { API_BASE_URL } from "../config";

const NewsHub = ({ cryptoSymbol }) => {
  const symbol = cryptoSymbol?.toUpperCase() || '';
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_BASE_URL}/api/crypto/news`, {
          params: { "query": cryptoSymbol, "refresh": false }
        });
        setNews(res.data.slice(0, 5));
      } catch (err) {
        setError('Error fetching news');
        console.error('News fetch error: ', err);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [cryptoSymbol]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }
  
  return (
    <div className='bg-blue-50 rounded-4xl'>
        <div className='mt-10 mx-10'>
            <h1 className='pt-10 pb-5 text-2xl text-center'>NewsHub for {symbol}</h1>
            <div>
                {news.length === 0 ? (
                <p>No news articles available.</p>
                ) : (
                news.map((article, index) => (
                    <div key={index} className='bg-white mb-4 p-4 rounded-lg shadow-md'>
                            {article.urlToImage && (
                            <div className="flex justify-center items-center pb-3">
                                <img
                                src={article.urlToImage}
                                alt={article.title}
                                className="max-w-full max-h-[400px] object-cover rounded-lg"
                                />
                            </div>
                            )}
                        <h3 className='text-1xl font-bold pb-2'>{article.title}</h3>
                        <p className='text-sm italic mb-4'>{article.description}</p>
                        
                        <a
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className='text-center'
                        >
                            Read more
                        </a>
                    </div>
                ))
                )}
            </div>
        </div>
    </div>
  );
};

export default NewsHub;
