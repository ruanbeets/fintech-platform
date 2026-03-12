import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet
} from "react-router-dom";

import Sidebar from "./components/layout/Sidebar";
import ProtectedRoute from "./components/layout/ProtectedRoute";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import AccountsPage from "./pages/AccountsPage";
import AccountDetailPage from "./pages/AccountDetailPage";
import SettingsPage from "./pages/SettingsPage";

function AppLayout() {

  return (

    <div className="min-h-screen bg-gray-950 text-gray-100 flex">

      <Sidebar />

      <div className="flex-1 p-10 overflow-y-auto">

        <Outlet />

      </div>

    </div>

  );

}

function App() {

  return (

    <BrowserRouter>

      <Routes>

        {/* Login */}

        <Route path="/" element={<LoginPage />} />

        {/* Protected Routes */}

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >

          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/accounts"
            element={<AccountsPage />}
          />

          <Route
            path="/accounts/:id"
            element={<AccountDetailPage />}
          />

          <Route
            path="/settings"
            element={<SettingsPage />}
          />

        </Route>

        {/* Catch-all redirect */}

        <Route
          path="*"
          element={<Navigate to="/" />}
        />

      </Routes>

    </BrowserRouter>

  );

}

export default App;