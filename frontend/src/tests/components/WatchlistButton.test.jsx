// WatchlistStarButton.test.jsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import { WatchlistStarButton } from "../../components/WatchlistStarButton";

describe("WatchlistStarButton", () => {
  const mockToggle = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders with correct aria-label when unwatched", () => {
    render(
      <WatchlistStarButton
        symbol="BTC"
        isWatched={false}
        onToggle={mockToggle}
      />
    );
    expect(screen.getByRole("button")).toHaveAttribute(
      "aria-label",
      "Add to watchlist"
    );
  });

  test("renders with correct aria-label when watched", () => {
    render(
      <WatchlistStarButton
        symbol="BTC"
        isWatched={true}
        onToggle={mockToggle}
      />
    );
    expect(screen.getByRole("button")).toHaveAttribute(
      "aria-label",
      "Remove from watchlist"
    );
  });

  test("calls onToggle with symbol when clicked", async () => {
    render(
      <WatchlistStarButton
        symbol="BTC"
        isWatched={false}
        onToggle={mockToggle}
      />
    );
    fireEvent.click(screen.getByRole("button"));
    await waitFor(() => {
      expect(mockToggle).toHaveBeenCalledWith("BTC");
    });
  });

  test("sets loading state and disables button while toggling", async () => {
    mockToggle.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 50))
    );
    render(
      <WatchlistStarButton
        symbol="BTC"
        isWatched={false}
        onToggle={mockToggle}
      />
    );

    const btn = screen.getByRole("button");
    fireEvent.click(btn);

    // should disable while loading
    expect(btn).toBeDisabled();

    await waitFor(() => expect(btn).not.toBeDisabled());
  });

  test("does not call onToggle when disabled prop is true", () => {
    render(
      <WatchlistStarButton
        symbol="BTC"
        isWatched={false}
        onToggle={mockToggle}
        disabled={true}
      />
    );
    fireEvent.click(screen.getByRole("button"));
    expect(mockToggle).not.toHaveBeenCalled();
  });

  test("applies correct size classes based on size prop", () => {
    const { rerender } = render(
      <WatchlistStarButton
        symbol="BTC"
        isWatched={false}
        onToggle={mockToggle}
        size="sm"
      />
    );
    expect(screen.getByTestId("lucide-star")).toHaveClass("h-4 w-4");

    rerender(
      <WatchlistStarButton
        symbol="BTC"
        isWatched={false}
        onToggle={mockToggle}
        size="md"
      />
    );
    expect(screen.getByTestId("lucide-star")).toHaveClass("h-5 w-5");

    rerender(
      <WatchlistStarButton
        symbol="BTC"
        isWatched={false}
        onToggle={mockToggle}
        size="lg"
      />
    );
    expect(screen.getByTestId("lucide-star")).toHaveClass("h-6 w-6");
  });
});
