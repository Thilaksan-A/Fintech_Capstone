import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import AccountConfirm from "../../pages/AccountConfirm";

function HomePage() {
  return <div data-testid="homepage">Homepage</div>;
}

beforeEach(() => {
  localStorage.setItem("investor", "Aggressive");
});

afterEach(() => {
  localStorage.clear();
});

test("redirects to homepage after delay", async () => {
  render(
    <MemoryRouter initialEntries={["/confirm"]}>
      <Routes>
        <Route path="/confirm" element={<AccountConfirm />} />
        <Route path="/" element={<HomePage />} />
      </Routes>
    </MemoryRouter>
  );

  expect(
    screen.getByText(/Profile has successfully been created!/i)
  ).toBeInTheDocument();
  expect(screen.getByText(/Your investor type is/i)).toBeInTheDocument();
  expect(screen.getByText(/Aggressive/i)).toBeInTheDocument();

  await waitFor(
    () => {
      expect(screen.getByTestId("homepage")).toBeInTheDocument();
    },
    { timeout: 4000 }
  );
});
