import { fireEvent, render, screen } from "@testing-library/react";

import SignupFlow from "../../pages/SignupFlow";

jest.mock("../../pages/Signup", () => (props) => (
  <div>
    Signup Form
    <button onClick={props.onSuccess}>Mock Signup Success</button>
  </div>
));
jest.mock("../../pages/TierSelect", () => (props) => (
  <div>
    Tier Select
    <button onClick={() => props.onSelect("Gold")}>Select Gold Tier</button>
  </div>
));
jest.mock("../../config", () => ({
  API_BASE_URL: "http://mock-api",
}));
jest.mock("../../pages/Survey", () => (props) => (
  <div data-testid="survey">
    Survey
    <button onClick={props.onComplete}>Complete Survey</button>
  </div>
));
jest.mock("../../pages/AccountConfirm", () => () => <div>Account Confirmed</div>);

describe("SignupFlow", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("starts on Signup form", () => {
    render(<SignupFlow />);
    expect(screen.getByText(/Signup Form/i)).toBeInTheDocument();
  });

  test("moves to TierSelect after signup success", () => {
    render(<SignupFlow />);
    fireEvent.click(screen.getByText(/Mock Signup Success/i));
    expect(screen.getByText(/Tier Select/i)).toBeInTheDocument();
  });

  test("saves tier and moves to Survey after tier selection", () => {
    render(<SignupFlow />);
    fireEvent.click(screen.getByText(/Mock Signup Success/i));
    fireEvent.click(screen.getByText(/Select Gold Tier/i));

    expect(localStorage.getItem("userTier")).toBe("Gold");
    expect(screen.getByTestId("survey")).toBeInTheDocument();  
  });

  test("moves to AccountConfirm after survey complete", () => {
    render(<SignupFlow />);
    fireEvent.click(screen.getByText(/Mock Signup Success/i));
    fireEvent.click(screen.getByText(/Select Gold Tier/i));
    fireEvent.click(screen.getByText(/Complete Survey/i));

    expect(screen.getByText(/Account Confirmed/i)).toBeInTheDocument();
  });
});
