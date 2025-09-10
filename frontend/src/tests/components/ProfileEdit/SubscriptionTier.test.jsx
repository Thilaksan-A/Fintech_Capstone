import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import SubscriptionTier from "../../../components/ProfileEdit/SubscriptionTier";

import { plans } from "@/data/TiersInfo";

jest.mock('@/data/TiersInfo', () => ({
  plans: [
    { key: 'basic', name: 'Basic', description: 'Basic plan description', price: '$10' },
    { key: 'premium', name: 'Premium', description: 'Premium plan description', price: '$20' },
  ],
}));

describe("SubscriptionTier", () => {
  const currentPlan = "basic";
  const onSelect = jest.fn();

  beforeEach(() => {
    onSelect.mockClear();
  });

  test("renders current plan name and description", () => {
    render(<SubscriptionTier currentPlan={currentPlan} onSelect={onSelect} />);

    // Current plan name
    expect(screen.getByText(currentPlan)).toBeInTheDocument();

    // Current plan description from plans data
    const planData = plans.find((p) => p.key === currentPlan);
    expect(planData).toBeDefined(); // sanity check
    if(planData) {
      expect(screen.getByText(planData.description)).toBeInTheDocument();
    }
  });

  test("renders all other plans except current plan", () => {
    render(<SubscriptionTier currentPlan={currentPlan} onSelect={onSelect} />);

    plans
      .filter((p) => p.key !== currentPlan)
      .forEach((plan) => {
        expect(screen.getByText(plan.name)).toBeInTheDocument();
        expect(screen.getByText(plan.description)).toBeInTheDocument();
        expect(screen.getByText(plan.price)).toBeInTheDocument();
        expect(
          screen.getByRole("button", { name: `Switch to ${plan.name}` })
        ).toBeInTheDocument();
      });

    // The current plan should not be rendered as an option
    expect(
      screen.queryByRole("button", { name: `Switch to ${currentPlan}` })
    ).not.toBeInTheDocument();
  });

  test("calls onSelect with correct plan key when clicking switch button", () => {
    render(<SubscriptionTier currentPlan={currentPlan} onSelect={onSelect} />);

    const otherPlan = plans.find((p) => p.key !== currentPlan);
    const button = screen.getByRole("button", { name: `Switch to ${otherPlan.name}` });

    fireEvent.click(button);

    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenCalledWith(otherPlan.key);
  });

  test("shows fallback description if current plan description not found", () => {
    // Pass a currentPlan that does not exist in plans
    const unknownPlan = "nonexistent";
    render(<SubscriptionTier currentPlan={unknownPlan} onSelect={onSelect} />);

    expect(screen.getByText(unknownPlan)).toBeInTheDocument();
    expect(screen.getByText("No description available")).toBeInTheDocument();
  });
});
