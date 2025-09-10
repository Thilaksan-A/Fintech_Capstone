import { render, screen } from "@testing-library/react";
import React from "react";

import { BigNewsCard } from "../../components/BigNewsCard";
import '@testing-library/jest-dom';

describe("BigNewsCard", () => {
  const baseData = {
    title: "Test News Title",
    description: "Some description",
    urlToImage: "https://example.com/image.jpg",
    content: "This is a sample content that should be long enough to estimate read time.",
    source: { name: "Example" },
    url: "https://example.com/news",
    publishedAt: "2023-08-10T12:34:56Z"
  };

  test("renders skeleton when no title is provided", () => {
    const dataWithoutTitle = { ...baseData, title: undefined };
    render(<BigNewsCard data={dataWithoutTitle} />);
    
    expect(screen.getByTestId("skeleton-loader")).toBeInTheDocument();
  });

  test("renders content when title is present", () => {
    render(<BigNewsCard data={baseData} />);
    
    const expectedDate = new Date(baseData.publishedAt).toDateString();
    expect(screen.getByText(expectedDate)).toBeInTheDocument();
  });

  test("renders backup image when urlToImage is missing", () => {
    const dataWithoutImage = { ...baseData, urlToImage: null };
    render(<BigNewsCard data={dataWithoutImage} />);
  
    const bgDiv = screen.getByTestId("news-card-bg");
    expect(bgDiv).toBeInTheDocument();
    expect(bgDiv.style.backgroundImage).toContain(
      "https://www.centralbank.net/globalassets/images/articles/crypto-par-2.png"
    );
  });

  test("renders custom image when urlToImage is provided", () => {
    const { container } = render(<BigNewsCard data={baseData} />);
    
    const bgDiv = container.querySelector("div[style]");
  
    expect(bgDiv).toBeInTheDocument();
    expect(bgDiv.style.backgroundImage).toContain(baseData.urlToImage);
  });

  test("calculates read time correctly", () => {
    const content = Array(300).fill("word").join(" ");
    const dataWithLongContent = { ...baseData, content };
    
    render(<BigNewsCard data={dataWithLongContent} />);
    expect(screen.getByText(/3 min read/)).toBeInTheDocument();
  });

  test("renders the external link correctly", () => {
    render(<BigNewsCard data={baseData} />);
    const link = screen.getByRole("link", { name: /read more/i });
    expect(link).toHaveAttribute("href", baseData.url);
    expect(link).toHaveAttribute("target", "_blank");
  });
});
