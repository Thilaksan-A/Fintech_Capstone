import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import InvestorProfile from "../../../components/ProfileEdit/InvestorProfile";

import Questions from "@/data/QUESTIONS";

describe("InvestorProfile", () => {
  const mockOnSubmit = jest.fn();

  const sampleData = {
    investor_type: "Conservative",
    raw_responses: {
      stress_response: "Not knowing what to do when the market drops",
      emotional_reaction: "Calm",
      risk_perception: "Moderate",
      income_vs_investment_balance: "Balanced",
      debt_situation: "None",
      investment_experience: "Intermediate",
      investment_motivation: "Growth",
      knowledge_level: "Advanced",
      investment_personality: "Cautious",
    },
  };

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  test("renders profile type from data", () => {
    render(<InvestorProfile data={sampleData} onSubmit={mockOnSubmit} />);
    expect(screen.getByText(/You are a/i)).toBeInTheDocument();
    expect(screen.getByText(sampleData.investor_type)).toBeInTheDocument();
  });

  test("renders all questions with select inputs", () => {
    render(<InvestorProfile data={sampleData} onSubmit={mockOnSubmit} />);
    Questions.forEach((q) => {
      expect(screen.getByText(q.question)).toBeInTheDocument();
      const select = screen.getByLabelText(q.question);
      expect(select).toBeInTheDocument();
      expect(select.tagName).toBe("SELECT");
      expect(screen.getAllByRole("option").length).toBeGreaterThanOrEqual(q.options.length + 1);
    });
  });

  test("selecting an option updates response state", () => {
    render(<InvestorProfile data={sampleData} onSubmit={mockOnSubmit} />);

    const firstQuestion = Questions[0];
    const select = screen.getByLabelText(firstQuestion.question);

    expect(select.value).toBe(sampleData.raw_responses["stress_response"]);

    fireEvent.change(select, { target: { value: firstQuestion.options[0] } });
    expect(select.value).toBe(firstQuestion.options[0]);
  });

  test("clicking save button calls onSubmit with mapped payload", () => {
    render(<InvestorProfile data={sampleData} onSubmit={mockOnSubmit} />);

    const saveBtn = screen.getByRole("button", { name: /save profile/i });
    fireEvent.click(saveBtn);

    expect(mockOnSubmit).toHaveBeenCalledTimes(1);

    const calledArg = mockOnSubmit.mock.calls[0][0];
    Object.entries(sampleData.raw_responses).forEach(([key, value]) => {
      expect(calledArg[key]).toBe(value);
    });
  });

  test("renders 'Unknown' profile type and empty selects if no data", () => {
    render(<InvestorProfile data={null} onSubmit={mockOnSubmit} />);
    expect(screen.getByText(/You are a/i)).toBeInTheDocument();
    expect(screen.getByText("Unknown")).toBeInTheDocument();

    Questions.forEach((q) => {
      const select = screen.getByLabelText(q.question);
      expect(select.value).toBe("");
    });
  });
});

describe('handleChange', () => {
  let setResponses;

  beforeEach(() => {
    setResponses = jest.fn();
  });

  const handleChange = (id, value, multiple = false) => {
    setResponses((prev) => {
      if (multiple) {
        const existing = Array.isArray(prev[id]) ? prev[id] : [];
        const updated = existing.includes(value)
          ? existing.filter((v) => v !== value)
          : [...existing, value];
        return { ...prev, [id]: updated };
      }
      return { ...prev, [id]: value };
    });
  };

  test('should set a single value when multiple is false', () => {
    handleChange('q1', 'yes');
    
    const updater = setResponses.mock.calls[0][0];
    const newState = updater({ q1: 'no' });
    
    expect(newState).toEqual({ q1: 'yes' });
  });

  test('should add a value to array when multiple is true and value not present', () => {
    handleChange('q2', 'a', true);
    
    const updater = setResponses.mock.calls[0][0];
    const newState = updater({ q2: ['b'] });
    
    expect(newState).toEqual({ q2: ['b', 'a'] });
  });

  test('should remove a value from array when multiple is true and value already present', () => {
    handleChange('q2', 'a', true);
    
    const updater = setResponses.mock.calls[0][0];
    const newState = updater({ q2: ['a', 'b'] });
    
    expect(newState).toEqual({ q2: ['b'] });
  });

  test('should initialize array if previous value is not an array when multiple is true', () => {
    handleChange('q2', 'a', true);
    
    const updater = setResponses.mock.calls[0][0];
    const newState = updater({ q2: 'not-an-array' });
    
    expect(newState).toEqual({ q2: ['a'] });
  });

  test('should initialize array if no previous value when multiple is true', () => {
    handleChange('q2', 'a', true);
    
    const updater = setResponses.mock.calls[0][0];
    const newState = updater({});
    
    expect(newState).toEqual({ q2: ['a'] });
  });
});
