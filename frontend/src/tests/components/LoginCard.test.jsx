import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import { MemoryRouter } from "react-router-dom";

import LoginCard from "../../components/LoginCard";


const mockNavigate = jest.fn();

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

jest.mock("axios");
jest.mock('../../config', () => ({
  API_BASE_URL: 'http://mock-api',
}));

describe("LoginCard", () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();

    Object.defineProperty(window, 'localStorage', {
      value: {
        setItem: jest.fn(),
        getItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });
  });

  test("renders login form", () => {
    render(
      <MemoryRouter>
        <LoginCard />
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /login/i })).toBeInTheDocument();
  });

  test("shows validation error on invalid input", async () => {
    render(
      <MemoryRouter>
        <LoginCard />
      </MemoryRouter>
    );

    fireEvent.submit(document.querySelector("form"));    
    await waitFor(() => {
      expect(screen.getByText(/unable to login/i)).toBeInTheDocument();
    });
  });

  test("submits form with valid input and navigates on success", async () => {
    axios.post.mockResolvedValue({
      data: { access_token: "fake-jwt" },
    });

    render(
      <MemoryRouter>
        <LoginCard />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "password123" },
    });

    fireEvent.click(screen.getByRole("button", { name: /login/i }));

    await waitFor(() => {
      expect(localStorage.setItem).toHaveBeenCalledWith("token", "fake-jwt");
      expect(mockNavigate).toHaveBeenCalledWith("/");
    });
  });

  test("shows error message on failed login", async () => {
    axios.post.mockRejectedValue({
      response: {
        data: { errors: ["Invalid credentials"] },
      },
    });

    render(
      <MemoryRouter>
        <LoginCard />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "wrongpass" },
    });

    fireEvent.click(screen.getByRole("button", { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });
});
