import { render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import React from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import AuthRedirectRoute from "../../components/AuthRedirectRoute";

jest.mock("../../config", () => ({
  API_BASE_URL: "http://mock-api",
}));

jest.mock("axios");

const mockUseLocation = jest.fn();
jest.mock("react-router-dom", () => {
  const actual = jest.requireActual("react-router-dom");
  return {
    ...actual,
    useLocation: () => mockUseLocation(),
  };
});

describe("AuthRedirectRoute", () => {
  const setup = (pathname = "/protected", token = "test-token") => {
    mockUseLocation.mockReturnValue({ pathname });

    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }

    return render(
      <MemoryRouter initialEntries={[pathname]}>
        <Routes>
          <Route
            path="*"
            element={
              <AuthRedirectRoute>
                <div>Protected Content</div>
              </AuthRedirectRoute>
            }
          />
          <Route path="/landing" element={<div>Landing Page</div>} />
          <Route path="/" element={<div>Home Page</div>} />
        </Routes>
      </MemoryRouter>
    );
  };

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test("redirects to /landing if no token is present", async () => {
    setup("/protected", null);

    await waitFor(() => {
      expect(screen.getByText("Landing Page")).toBeInTheDocument();
    });
  });

  test("redirects to / if token is valid and pathname is /login", async () => {
    axios.get.mockResolvedValue({ status: 200 });
    setup("/login", "valid-token");

    await waitFor(() => {
      expect(screen.getByText("Home Page")).toBeInTheDocument();
    });
  });

  test("renders children if token is valid and not on login/signup", async () => {
    axios.get.mockResolvedValue({ status: 200 });
    setup("/dashboard", "valid-token");

    await waitFor(() => {
      expect(screen.getByText("Protected Content")).toBeInTheDocument();
    });
  });

  test("redirects to /landing if token is invalid", async () => {
    axios.get.mockRejectedValue({ response: { status: 401 } });
    setup("/dashboard", "invalid-token");

    await waitFor(() => {
      expect(screen.getByText("Landing Page")).toBeInTheDocument();
    });
  });

  test("renders null while loading (valid === null)", () => {
    axios.get.mockImplementation(() => new Promise(() => {}));
    setup("/dashboard", "valid-token");

    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    expect(screen.queryByText("Landing Page")).not.toBeInTheDocument();
  });
});
