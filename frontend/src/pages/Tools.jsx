import React from "react";
import EMIForm from "../components/EMIForm";
import SIPForm from "../components/SIPForm";
import MFSearch from "../components/MFSearch";

export default function Tools() {
  return (
    <div className="container">
      <h1>Financial Tools</h1>
      
      <EMIForm />
      <SIPForm />
      <MFSearch />
    </div>
  );
}
