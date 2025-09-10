import { render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import React from "react";

import NewsHub from "../../components/NewsHub";
import { API_BASE_URL } from "../../config";

// Mock axios to avoid actual HTTP requests
jest.mock('axios');

// Mock the API_BASE_URL to a mock URL
jest.mock('../../config', () => ({
  API_BASE_URL: "https://mock-api.com",
}));

describe("NewsHub component", () => {

  test("shows loading state initially", () => {
    render(<NewsHub cryptoSymbol="btc" />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  test("displays error message if news fetch fails", async () => {
    axios.get.mockRejectedValue(new Error("Error fetching news"));

    render(<NewsHub cryptoSymbol="btc" />);
    
    await waitFor(() => expect(screen.getByText("Error fetching news")).toBeInTheDocument());
  });

  test("displays news articles when data is fetched", async () => {
    const mockNewsData = [
      {
        title: "Bitcoin hits new high",
        description: "Bitcoin has reached a new all-time high",
        urlToImage: "https://example.com/bitcoin.jpg",
        url: "https://example.com/bitcoin-news"
      },
      {
        title: "Ethereum's new upgrade",
        description: "Ethereum 2.0 is now live",
        urlToImage: "https://example.com/eth.jpg",
        url: "https://example.com/eth-news"
      }
    ];
  
    axios.get.mockResolvedValue({
      data: mockNewsData,
    });
  
    render(<NewsHub cryptoSymbol="btc" />);
  
    await waitFor(() => expect(screen.getByText("NewsHub for BTC")).toBeInTheDocument());
  
    // Check that news articles are rendered
    expect(screen.getByText("Bitcoin hits new high")).toBeInTheDocument();
    expect(screen.getByText("Ethereum's new upgrade")).toBeInTheDocument();
  
    // Check that the "Read more" link exists for each article
    const readMoreLinks = screen.getAllByRole('link', { name: /Read more/i });
    expect(readMoreLinks).toHaveLength(2); // Check that two "Read more" links are present
  });

  test("displays 'No news articles available' when no news is returned", async () => {
    axios.get.mockResolvedValue({
      data: [],
    });

    render(<NewsHub cryptoSymbol="btc" />);
    
    await waitFor(() => expect(screen.getByText("No news articles available.")).toBeInTheDocument());
  });

  test("displays the image if urlToImage is available", async () => {
    const mockNewsData = [
      {
        title: "Bitcoin hits new high",
        description: "Bitcoin has reached a new all-time high",
        urlToImage: "https://example.com/bitcoin.jpg",
        url: "https://example.com/bitcoin-news"
      }
    ];

    axios.get.mockResolvedValue({
      data: mockNewsData,
    });

    render(<NewsHub cryptoSymbol="btc" />);
    
    await waitFor(() => expect(screen.getByAltText("Bitcoin hits new high")).toBeInTheDocument());
    expect(screen.getByRole("img")).toHaveAttribute("src", "https://example.com/bitcoin.jpg");
  });

  test("displays correct title with symbol", async () => {
    const mockNewsData = [
      {
        title: "Bitcoin hits new high",
        description: "Bitcoin has reached a new all-time high",
        urlToImage: "https://example.com/bitcoin.jpg",
        url: "https://example.com/bitcoin-news"
      }
    ];

    axios.get.mockResolvedValue({
      data: mockNewsData,
    });

    render(<NewsHub cryptoSymbol="btc" />);
    
    await waitFor(() => expect(screen.getByText("NewsHub for BTC")).toBeInTheDocument());
  });
});
