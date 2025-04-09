import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import WaiterDashboard from "./pages/WaiterDashboard";
import ChefDashboard from "./pages/ChefDashboard";
import BusboyDashboard from "./pages/BusboyDashboard";
import ManagerDashboard from "./pages/ManagerDashboard";

export default function App() {
  const user = JSON.parse(localStorage.getItem("user"));

  const ProtectedRoute = ({ role, children }) => {
    if (!user || user.role !== role) {
      return <Navigate to="/login" replace />;
    }
    return children;
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          path="/waiter"
          element={
            <ProtectedRoute role="Waiter">
              <WaiterDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/chef"
          element={
            <ProtectedRoute role="Chef">
              <ChefDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/busboy"
          element={
            <ProtectedRoute role="Busboy">
              <BusboyDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/manager"
          element={
            <ProtectedRoute role="Manager">
              <ManagerDashboard />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}
