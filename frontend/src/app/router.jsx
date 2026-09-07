// src/app/router.jsx

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "../core/authStore";

// Pages (create these files)
import LoginPage from "../pages/LoginPage";
import DashboardPage from "../pages/DashboardPage";
import AccountsPage from "../pages/AccountsPage";
import TransactionsPage from "../pages/TransactionsPage";
import AnalyticsPage from "../pages/AnalyticsPage";
import UploadPage from "../pages/UploadPage";
import SettingsPage from "../pages/SettingsPage";

// Protect routes
const PrivateRoute = ({ children }) => {
  const token = useAuthStore((state) => state.token);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

const EntryRoute = () => {
  const token = useAuthStore((state) => state.token);
  return token ? <DashboardPage /> : <UploadPage />;
};

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/demo" element={<DashboardPage demo />} />
        <Route path="/demo/trends" element={<AnalyticsPage demo />} />
        <Route path="/import" element={<UploadPage />} />
        <Route path="/workspace" element={<DashboardPage imported />} />
        <Route path="/workspace/trends" element={<AnalyticsPage imported />} />
        <Route path="/trends" element={<PrivateRoute><AnalyticsPage /></PrivateRoute>} />

        {/* Protected */}
        <Route
          path="/app"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        />

        <Route path="/" element={<EntryRoute />} />

        <Route
          path="/accounts"
          element={
            <PrivateRoute>
              <AccountsPage />
            </PrivateRoute>
          }
        />

        <Route
          path="/transactions"
          element={
            <PrivateRoute>
              <TransactionsPage />
            </PrivateRoute>
          }
        />

        <Route
          path="/analytics"
          element={
            <PrivateRoute>
              <AnalyticsPage />
            </PrivateRoute>
          }
        />

        <Route
          path="/upload"
          element={
            <PrivateRoute>
              <UploadPage />
            </PrivateRoute>
          }
        />

        <Route
          path="/settings"
          element={
            <PrivateRoute>
              <SettingsPage />
            </PrivateRoute>
          }
        />

        {/* fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};
