import React from "react";
import ReactDOM from "react-dom/client";

import "./index.css";
import App from "./App";

import {
  Chart as ChartJS,
  ArcElement,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(
  ArcElement,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
);

const root = ReactDOM.createRoot(
  document.getElementById("root")
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);