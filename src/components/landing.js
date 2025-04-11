import React from "react";
import { useNavigate } from "react-router-dom";
import "./landing.css";

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="content">
      <div className="title-container">
        <h1 className="title-text">Meow Meow</h1>
      </div>

      <div className="image-container">
        <img src="/landing.png" alt="Landing" className="main-image" />
      </div>

      <button className="button" onClick={() => navigate("/login")}>
        <span className="button-text">Get Started</span>
        <span className="button-arrow">›</span>
      </button>
    </div>
  );
};

export default Landing;
