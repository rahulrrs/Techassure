import React from "react";
import ReactDOM from "react-dom/client";

import "./index.css";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Layout>
      <Dashboard />
    </Layout>
  </React.StrictMode>
);
