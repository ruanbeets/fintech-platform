import { NavLink } from "react-router-dom";

export default function Sidebar() {

  const linkClass = ({ isActive }) =>
    isActive
      ? "text-white font-semibold"
      : "text-gray-400 hover:text-white";

  return (

    <div className="w-64 bg-gray-900 text-gray-200 p-6 min-h-screen">

      <h2 className="text-xl font-bold mb-8">
        FinTrack
      </h2>

      <nav className="flex flex-col gap-4">

        <NavLink to="/dashboard" className={linkClass}>
          Dashboard
        </NavLink>

        <NavLink to="/accounts" className={linkClass}>
          Accounts
        </NavLink>

        <NavLink to="/settings" className={linkClass}>
          Settings
        </NavLink>

      </nav>

    </div>
  );
}