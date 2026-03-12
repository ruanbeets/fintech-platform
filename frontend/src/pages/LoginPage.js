import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../services/api";

export default function LoginPage() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {

    e.preventDefault();

    try {

      const user = await login(email, password);

      localStorage.setItem(
        "user_id",
        user.user_id
      );

      localStorage.setItem(
        "user_email",
        user.email
      );

      navigate("/dashboard");

    } catch {

      alert("Invalid login");

    }

  };

  return (

    <div className="flex items-center justify-center min-h-screen bg-gray-950">

      <div className="bg-gray-900 p-10 rounded-xl w-96">

        <h1 className="text-2xl font-bold mb-6 text-white">

          FinTrack Login

        </h1>

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >

          <input
            className="w-full p-2 bg-gray-800 rounded"
            placeholder="Email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
          />

          <input
            type="password"
            className="w-full p-2 bg-gray-800 rounded"
            placeholder="Password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
          />

          <button className="w-full bg-blue-600 p-2 rounded">

            Login

          </button>

        </form>

      </div>

    </div>

  );

}