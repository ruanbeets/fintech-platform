import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import ProtectedRoute from "./components/ProtectedRoute";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import AccountsPage from "./pages/AccountsPage";
import AccountDetailPage from "./pages/AccountDetailPage";
import SettingsPage from "./pages/SettingsPage";

function AppLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">

      <Sidebar />

      <div className="flex-1 p-10 overflow-y-auto">
        {children}
      </div>

    </div>
  );
}

function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route path="/" element={<LoginPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AppLayout>
                <DashboardPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/accounts"
          element={
            <ProtectedRoute>
              <AppLayout>
                <AccountsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/accounts/:id"
          element={
            <ProtectedRoute>
              <AppLayout>
                <AccountDetailPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <AppLayout>
                <SettingsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;