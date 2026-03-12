import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function AppLayout() {

  return (

    <div className="min-h-screen bg-gray-950 text-gray-100 flex">

      <Sidebar />

      <div className="flex-1 p-10 overflow-y-auto">

        <Outlet />

      </div>

    </div>

  );

}