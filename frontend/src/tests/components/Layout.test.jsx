import { render, screen } from "@testing-library/react";
import React from "react";
import { BrowserRouter as Router } from "react-router-dom";

import Layout from "../../components/Layout";

jest.mock("../../components/BottomNav", () => () => <div data-testid="bottom-nav">BottomNav</div>);

// Mock the Outlet component from react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Outlet: () => <div data-testid="outlet">Outlet content</div>, // Mocked outlet
}));

describe("Layout component", () => {

  test("renders the BottomNav component", () => {
    render(
      <Router>
        <Layout />
      </Router>
    );
    
    // Check if BottomNav (mocked) is rendered
    expect(screen.getByTestId("bottom-nav")).toBeInTheDocument();
  });

  test("renders Outlet component", () => {
    render(
      <Router>
        <Layout />
      </Router>
    );
    
    // Check if Outlet is rendered
    expect(screen.getByTestId("outlet")).toBeInTheDocument();
  });

  test("has main tag with correct classes", () => {
    render(
      <Router>
        <Layout />
      </Router>
    );
    
    const mainElement = screen.getByRole("main");
    expect(mainElement).toHaveClass("min-h-screen", "relative");
  });
});
