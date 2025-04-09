// src/pages/Login.jsx

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/auth";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const user = await loginUser({ username, password });
      localStorage.setItem("user", JSON.stringify(user));

      switch (user.role) {
        case "Waiter":
          navigate("/waiter");
          break;
        case "Chef":
          navigate("/chef");
          break;
        case "Busboy":
          navigate("/busboy");
          break;
        case "Manager":
          navigate("/manager");
          break;
        default:
          setError("Unknown role");
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-xl w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-4">J's Corner Login</h2>
        {error && <p className="text-red-500 mb-3">{error}</p>}

        <label className="block mb-2">
          Username:
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </label>

        <label className="block mb-4">
          Password:
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </label>

        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded w-full">
          Login
        </button>
      </form>
    </div>
  );
}