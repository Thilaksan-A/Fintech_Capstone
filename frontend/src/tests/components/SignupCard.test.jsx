import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import React from "react";
import { MemoryRouter } from "react-router-dom";

import SignupCard from "../../components/SignupCard";

jest.mock("axios");
jest.mock("../../config", () => ({
  API_BASE_URL: "http://mock-api",
}));

describe("SignupCard", () => {
  const onSuccessMock = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test("renders inputs and buttons", () => {
    render(
      <MemoryRouter>
        <SignupCard onSuccess={onSuccessMock} />
      </MemoryRouter>
    );    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /next/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /already got an account/i })).toBeInTheDocument();
  });

  test("updates input fields on change", () => {
    render(
      <MemoryRouter>
        <SignupCard onSuccess={onSuccessMock} />
      </MemoryRouter>
    );       
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: "testuser" } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "test@example.com" } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "password123" } });

    expect(screen.getByLabelText(/username/i)).toHaveValue("testuser");
    expect(screen.getByLabelText(/email/i)).toHaveValue("test@example.com");
    expect(screen.getByLabelText(/password/i)).toHaveValue("password123");
  });

  test("shows validation error if form data is invalid", async () => {
    render(
      <MemoryRouter>
        <SignupCard onSuccess={jest.fn()} />
      </MemoryRouter>
    );   
   
    fireEvent.submit(screen.getByRole("form"));
    
    await waitFor(() => {
      expect(screen.getByTestId("signup-error")).toBeInTheDocument();
      expect(screen.getByTestId("signup-error")).toHaveTextContent(/error creating account please check inputs/i);
    });
    expect(onSuccessMock).not.toHaveBeenCalled();
  });

  test("submits valid form and calls onSuccess, sets token in localStorage", async () => {
    axios.post.mockResolvedValueOnce({ data: { access_token: "fake-jwt-token" } });

    render(
      <MemoryRouter>
        <SignupCard onSuccess={onSuccessMock} />
      </MemoryRouter>
    );    
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: "testuser" } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "test@example.com" } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "password123" } });

    fireEvent.click(screen.getByRole("button", { name: /next/i }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining("/api/user/"),
        {
          username: "testuser",
          email: "test@example.com",
          password_hash: "password123",
        }
      );
    });

    expect(localStorage.getItem("token")).toBe("fake-jwt-token");
    expect(onSuccessMock).toHaveBeenCalled();
    expect(screen.queryByText(/error creating account/i)).not.toBeInTheDocument();
  });

  test("shows error message on failed submission", async () => {
    axios.post.mockRejectedValueOnce({
      response: { data: { detail: "User already exists" } },
    });

    render(
      <MemoryRouter>
        <SignupCard onSuccess={onSuccessMock} />
      </MemoryRouter>
    );    
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: "testuser" } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "test@example.com" } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "password123" } });

    fireEvent.click(screen.getByRole("button", { name: /next/i }));

    await waitFor(() => {
      expect(screen.getByText(/error creating account/i)).toBeInTheDocument();
    });

    expect(onSuccessMock).not.toHaveBeenCalled();
    expect(localStorage.getItem("token")).toBeNull();
  });
});
