import { fireEvent, render, screen } from "@testing-library/react";

import TierSelect from "../../pages/TierSelect";

describe("TierSelect component", () => {
  test("renders all plans with correct details", () => {
    render(<TierSelect onSelect={() => {}} />);
    
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Choose Your Plan");
    
    expect(screen.getByText("Basic")).toBeInTheDocument();
    expect(screen.getByText("Top 3 cryptos only")).toBeInTheDocument();
    expect(screen.getByText("$0")).toBeInTheDocument();
    
    expect(screen.getByText("Medium")).toBeInTheDocument();
    expect(screen.getByText("Top 10 cryptos only")).toBeInTheDocument();
    expect(screen.getByText("$5/month")).toBeInTheDocument();
    
    expect(screen.getByText("Premium")).toBeInTheDocument();
    expect(screen.getByText("Full access to everything")).toBeInTheDocument();
    expect(screen.getByText("$15/month")).toBeInTheDocument();
  });

  test("calls onSelect with correct key when a plan is selected", () => {
    const onSelectMock = jest.fn();
    render(<TierSelect onSelect={onSelectMock} />);

    fireEvent.click(screen.getByRole("button", { name: /select basic/i }));
    expect(onSelectMock).toHaveBeenCalledWith("Free");

    fireEvent.click(screen.getByRole("button", { name: /select medium/i }));
    expect(onSelectMock).toHaveBeenCalledWith("Medium");

    fireEvent.click(screen.getByRole("button", { name: /select premium/i }));
    expect(onSelectMock).toHaveBeenCalledWith("Premium");

    expect(onSelectMock).toHaveBeenCalledTimes(3);
  });
});
