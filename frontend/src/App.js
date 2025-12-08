import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

import Home from "./pages/Home";
import EMI from "./pages/EMI";
import SIP from "./pages/SIP";
import MutualFunds from "./pages/MutualFunds";
import Chatbot from "./pages/Chatbot";

function App() {
  return (
    <Router>
      <Navbar />

      <div className="content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/emi" element={<EMI />} />
          <Route path="/sip" element={<SIP />} />
          <Route path="/funds" element={<MutualFunds />} />
          <Route path="/chat" element={<Chatbot />} />
        </Routes>
      </div>

      <Footer />
    </Router>
  );
}

export default App;
