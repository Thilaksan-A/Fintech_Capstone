import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import "@testing-library/jest-dom";
import { SmallNewsCard } from "../../components/SmallNewsCard";

describe("SmallNewsCard", () => {
  const baseData = {
    title: "Test News Title",
    description: "Test description",
    url_image: "https://example.com/image.jpg",
    content: "Full content",
    source_url: "https://example.com",
    timestamp: "2025-08-12T10:00:00Z"
  };

  test("renders title, image, and formatted date", () => {
    render(<SmallNewsCard data={baseData} />);

    // Title
    expect(screen.getByText("Test News Title")).toBeInTheDocument();

    // Image with alt text
    const img = screen.getByRole("img", { name: /test news title/i });
    expect(img).toHaveAttribute("src", baseData.url_image);

    // Formatted date
    const expectedDate = new Date(baseData.timestamp).toDateString();
    expect(screen.getByText(expectedDate)).toBeInTheDocument();
  });

  test("toggles expansion when clicked", () => {
    render(<SmallNewsCard data={baseData} />);

    const card = screen.getByRole("img", { name: /test news title/i }).closest("div");
    expect(screen.queryByText("hello")).not.toBeInTheDocument();

    fireEvent.click(card);
    expect(screen.getByText("hello")).toBeInTheDocument();

    fireEvent.click(card);
    expect(screen.queryByText("hello")).not.toBeInTheDocument();
  });

  test("renders empty date when timestamp is missing", () => {
    const noTimestampData = { ...baseData, timestamp: null };
    render(<SmallNewsCard data={noTimestampData} />);
  
    const dateElement = screen.getByText((content, element) => {
      return element.tagName.toLowerCase() === "span" && content === "";
    });
  
    expect(dateElement).toBeInTheDocument();
    expect(dateElement).toBeEmptyDOMElement();
  
  });
});
