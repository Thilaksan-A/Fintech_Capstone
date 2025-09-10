// LandingPage.test.jsx
import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";
import { useNavigate } from "react-router-dom";

import LandingPage from "../../pages/LandingPage";

// Mock useNavigate from react-router-dom
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: jest.fn(),
}));

describe("LandingPage", () => {
  let mockNavigate;

  beforeEach(() => {
    mockNavigate = jest.fn();
    useNavigate.mockReturnValue(mockNavigate);
  });

  test("renders the logo, title, and main heading", () => {
    render(<LandingPage />);

    // Logo
    expect(screen.getByRole("img")).toHaveAttribute("src", "/logo.png");

    // Title text in header
    expect(screen.getByText(/SafeGuard/i)).toBeInTheDocument();

    // Main heading
    expect(
      screen.getByRole("heading", { name: /Trade Crypto/i })
    ).toBeInTheDocument();

    // Subheading text
    expect(
      screen.getByText(/Generating actionable, scenario-based recommendations/i)
    ).toBeInTheDocument();
  });

  test("navigates to /login when Login button is clicked", () => {
    render(<LandingPage />);
    const loginButton = screen.getByRole("button", { name: /Login/i });
    fireEvent.click(loginButton);

    expect(mockNavigate).toHaveBeenCalledWith("/login");
  });

  test("navigates to /signup when Get Started button is clicked", () => {
    render(<LandingPage />);
    const getStartedButton = screen.getByRole("button", {
      name: /Get Started/i,
    });
    fireEvent.click(getStartedButton);

    expect(mockNavigate).toHaveBeenCalledWith("/signup");
  });

  test("has correct styling on the Login button", () => {
    render(<LandingPage />);
    const loginButton = screen.getByRole("button", { name: /Login/i });
    expect(loginButton).toHaveStyle({ backgroundColor: "#b8d4d1" });
  });

  test("has correct styling on the Get Started button", () => {
    render(<LandingPage />);
    const getStartedButton = screen.getByRole("button", {
      name: /Get Started/i,
    });
    expect(getStartedButton).toHaveStyle({
      backgroundColor: "#b8d4d1",
      border: "1px solid #b8d4d1",
    });
  });
});
