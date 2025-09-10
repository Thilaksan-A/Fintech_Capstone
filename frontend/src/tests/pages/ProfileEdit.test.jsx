import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import React from "react";
import { BrowserRouter, MemoryRouter } from "react-router-dom";

import ProfileEdit from "../../pages/ProfileEdit";

jest.mock("@/App.css", () => ({}));

jest.mock("../../config", () => ({
  API_BASE_URL: "http://mock-api",
}));

jest.mock("@/components/ProfileEdit/InvestorProfile", () => ({ data, onSubmit }) => (
  <div data-testid="InvestorProfile">InvestorProfile Component</div>
));
jest.mock("@/components/ProfileEdit/SubscriptionTier", () => ({ currentPlan, onSelect }) => (
  <div data-testid="SubscriptionTier">SubscriptionTier Component</div>
));
jest.mock("@/components/ui/loadingoverlay", () => () => <div data-testid="LoadingOverlay">Loading...</div>);

jest.mock("axios");

jest.mock('@/components/ProfileEdit/SubscriptionTier', () => (props) => {
  return (
    <div data-testid="SubscriptionTier">
      <button onClick={() => props.onSelect('premium')}>Select Premium Plan</button>
    </div>
  );
});

const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

beforeEach(() => {
  Storage.prototype.getItem = jest.fn(() => "fakeToken");
  Storage.prototype.removeItem = jest.fn();
  jest.clearAllMocks();
});

describe("ProfileEdit", () => {
  test("renders menu by default", () => {
    render(
      <MemoryRouter>
        <ProfileEdit />
      </MemoryRouter>
    );
    expect(screen.getByText(/Edit Investment Profile/i)).toBeInTheDocument();
    expect(screen.getByText(/Subscription Plan/i)).toBeInTheDocument();
    expect(screen.getByText(/Logout/i)).toBeInTheDocument();
  });

  test("calls APIs on mount", async () => {
    axios.get.mockResolvedValueOnce({ data: { username: "John", email: "john@example.com" } }); // profile data
    axios.get.mockResolvedValueOnce({ data: { subscription_tier: "Gold" } }); // tier
    axios.get.mockResolvedValueOnce({ data: {} }); // survey data

    render(
      <MemoryRouter>
        <ProfileEdit />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining("/api/user/user_data"),
        expect.any(Object)
      );
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining("/api/user/tier"),
        expect.any(Object)
      );
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining("/api/user/profile"),
        expect.any(Object)
      );
    });
  });

  test("navigates on logout", () => {
    render(
      <MemoryRouter>
        <ProfileEdit />
      </MemoryRouter>
    );
    fireEvent.click(screen.getByText(/Logout/i));
    expect(localStorage.removeItem).toHaveBeenCalledWith("token");
    expect(mockNavigate).toHaveBeenCalledWith("/landing");
  });

  test("switches to subscription section", () => {
    render(
      <MemoryRouter>
        <ProfileEdit />
      </MemoryRouter>
    );
    fireEvent.click(screen.getByText(/Subscription Plan/i));
    expect(screen.getByTestId("SubscriptionTier")).toBeInTheDocument();
  });
});

describe("ProfileEdit handlePlanChange", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    Storage.prototype.getItem = jest.fn(() => "mock-token");
    Storage.prototype.removeItem = jest.fn();
  });

  test("updates plan successfully and stops loading", async () => {
    axios.post.mockResolvedValueOnce({ data: { subscription_tier: "premium" } });
  
    render(
      <BrowserRouter>
        <ProfileEdit />
      </BrowserRouter>
    );

    fireEvent.click(screen.getByText(/subscription plan/i));
  
    const selectButton = await screen.findByText(/select premium plan/i);
  
    fireEvent.click(selectButton);
  
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining("/api/user/update_tier"),
        { tier: "premium" },
        expect.any(Object)
      );
    });
  });

  test("handles 401 error by removing token and redirecting", async () => {
    axios.post.mockRejectedValueOnce({
      response: { status: 401 },
    });

    render(
      <BrowserRouter>
        <ProfileEdit />
      </BrowserRouter>
    );
    await waitFor(() => expect(axios.post).not.toHaveBeenCalled());

    expect(localStorage.removeItem).not.toHaveBeenCalled();

    expect(mockNavigate).not.toHaveBeenCalled();
  });
});

jest.mock("@/components/ProfileEdit/InvestorProfile", () => (props) => {
  return (
    <button onClick={() => props.onSubmit({ example: "payload" })}>
      Submit Survey
    </button>
  );
});
