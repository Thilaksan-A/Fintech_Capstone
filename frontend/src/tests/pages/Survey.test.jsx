import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import axios from "axios";

import Survey from "../../pages/Survey";

jest.mock("axios");
jest.mock('../../config', () => ({
  API_BASE_URL: 'http://mock-api',
}));

jest.useFakeTimers();

axios.post.mockImplementation(() => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: { investor_type: "Aggressive" } });
    }, 100);
  });
});

const questionsMock = [
  {
    question: "Question 1?",
    options: ["A1", "B1", "C1"],
  },
  {
    question: "Question 2?",
    options: ["A2", "B2", "C2"],
  },
  {
    question: "Question 3?",
    options: ["A3", "B3", "C3"],
  },
];

const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key]),
    setItem: jest.fn((key, value) => {
      store[key] = value;
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();
Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

describe("Survey component", () => {
  beforeEach(() => {
    localStorageMock.clear();
    localStorageMock.getItem.mockReturnValue("fake-token");
    axios.post.mockResolvedValue({ data: { investor_type: "Aggressive" } });
  });

  test("renders first question and options", () => {
    render(<Survey questions={questionsMock} onComplete={jest.fn()} />);
    expect(screen.getByText("Question 1?")).toBeInTheDocument();
    questionsMock[0].options.forEach((option) => {
      expect(screen.getByText(option)).toBeInTheDocument();
    });
    expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
  });

  test("selecting an option moves to next question and resets selection", () => {
    render(<Survey questions={questionsMock} onComplete={jest.fn()} />);
    fireEvent.click(screen.getByText("B1"));

    expect(screen.getByText("Question 2?")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /previous/i })).toBeEnabled();
  });

  test("clicking previous goes back a question", () => {
    render(<Survey questions={questionsMock} onComplete={jest.fn()} />);
    fireEvent.click(screen.getByText("B1"));
    fireEvent.click(screen.getByRole("button", { name: /previous/i }));

    expect(screen.getByText("Question 1?")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
  });

  test("submits survey on last question and calls onComplete", async () => {
    const onCompleteMock = jest.fn();

    render(<Survey questions={questionsMock} onComplete={onCompleteMock} />);

    fireEvent.click(screen.getByText("A1"));
    fireEvent.click(screen.getByText("A2"));

    expect(screen.getByText("Question 3?")).toBeInTheDocument();

    fireEvent.click(screen.getByText("A3"));

    jest.advanceTimersByTime(50);
    const spinner = await screen.findByText(/submitting your answers/i);
    expect(spinner).toBeInTheDocument();
    jest.advanceTimersByTime(100);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining("/api/user/survey"),
        expect.any(Object),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: expect.stringContaining("Bearer"),
          }),
        })
      );
      expect(localStorage.setItem).toHaveBeenCalledWith("investor", "Aggressive");
      expect(onCompleteMock).toHaveBeenCalled();
    });
  });

  test("displays nothing if no question available", () => {
    const { container } = render(<Survey questions={[]} onComplete={jest.fn()} />);
    expect(container.firstChild).toBeNull();
  });
});
