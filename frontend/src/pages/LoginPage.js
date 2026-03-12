import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/api";

function LoginPage() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {

      const user = await login(email, password);

      localStorage.setItem("user_id", user.user_id);
      localStorage.setItem("user_email", user.email);

      navigate("/dashboard");

    } catch (err) {
      alert("Invalid login");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-950 text-white">

      <div className="bg-gray-900 p-10 rounded-xl w-96">

        <h2 className="text-2xl mb-6 font-bold">
          FinTrack Demo Login
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">

          <input
            className="w-full p-2 rounded bg-gray-800"
            placeholder="Email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
          />

          <input
            type="password"
            className="w-full p-2 rounded bg-gray-800"
            placeholder="Password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
          />

          <button className="w-full bg-blue-600 p-2 rounded">
            Login
          </button>

        </form>

        <div className="mt-6 text-sm text-gray-400">
          Demo login:<br/>
          demo@fintrack.com / demo123
        </div>

      </div>

    </div>
  );
}

export default LoginPage;