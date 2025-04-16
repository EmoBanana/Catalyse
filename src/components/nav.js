import React, { useState } from "react";
import { X } from "react-feather";
import "./nav.css";
import Action from "./action";
import MachineLearning from "./ml";

const Navigation = ({ setShowNav, setShowML, setShowAction }) => {
  const handleBack = () => {
    setShowNav(false);
  };

  return (
    <div className="navigation-overlay">
      <div className="navigation-container">
        <div className="navigation-header">
          <h1>Navigation</h1>
          <X size={24} className="back-button" onClick={handleBack} />
        </div>

        <div className="navigation-options">
          <div
            className="nav-option"
            onClick={() => {
              setShowNav(false);
              setShowML(true);
            }}
          >
            <h2>Machine Learning</h2>
            <p>View ML insights and analytics</p>
          </div>
          <div className="nav-option" onClick={() => handleBack()}>
            <h2>Chat</h2>
            <p>Talk with our AI assistant</p>
          </div>
          <div
            className="nav-option"
            onClick={() => {
              setShowNav(false);
              setShowAction(true);
            }}
          >
            <h2>Actions</h2>
            <p>Perform business actions</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navigation;
