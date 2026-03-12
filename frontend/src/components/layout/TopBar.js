import { useNavigate } from "react-router-dom";

export default function TopBar() {

  const navigate = useNavigate();

  const email = localStorage.getItem("user_email");

  const handleLogout = () => {

    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");

    navigate("/");
  };

  return (

    <div className="flex justify-between items-center mb-8">

      <div></div>

      <div className="flex items-center gap-4">

        <span className="text-gray-400 text-sm">
          {email}
        </span>

        <button
          onClick={handleLogout}
          className="bg-red-600 px-4 py-1 rounded text-sm hover:bg-red-500"
        >
          Logout
        </button>

      </div>

    </div>

  );
}