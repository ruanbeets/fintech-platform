import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="w-64 bg-gray-900 text-gray-200 p-6 min-h-screen">

      <h2 className="text-xl font-bold mb-8">
        Fintech
      </h2>

      <nav className="flex flex-col gap-4">

        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            isActive
              ? "text-white font-semibold"
              : "text-gray-400 hover:text-white"
          }
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/accounts"
          className={({ isActive }) =>
            isActive
              ? "text-white font-semibold"
              : "text-gray-400 hover:text-white"
          }
        >
          Accounts
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            isActive
              ? "text-white font-semibold"
              : "text-gray-400 hover:text-white"
          }
        >
          Settings
        </NavLink>

      </nav>

    </div>
  );
}