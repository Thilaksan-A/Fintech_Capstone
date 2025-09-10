import { Outlet } from "react-router-dom";

import BottomNav from "./BottomNav";

function Layout() {
  return (
    <main className="min-h-screen relative">
      <Outlet />
      <BottomNav />
    </main>
  );
}

export default Layout;
