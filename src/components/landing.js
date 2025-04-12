import React from "react";
import { useNavigate } from "react-router-dom";
import { ChevronUp } from "react-feather";
import "./landing.css";

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="content">
      <div className="title-container">
        <h2 className="left-ear">
          <ChevronUp size={26}></ChevronUp>
        </h2>
        <h2 className="right-ear">
          <ChevronUp size={26}></ChevronUp>
        </h2>
        <h1 className="title-text">
          <span>Cat</span>alyse
        </h1>
        <p className="tagline">
          <span>Meow</span>-nitoring insights that drive business growth
        </p>
      </div>

      <div className="image-container">
        <img src="/landing.png" alt="Landing" className="main-image" />
      </div>

      {/* Navigate to login page */}
      <button className="button" onClick={() => navigate("/login")}>
        <span className="button-text">Get Started</span>
        <span className="button-arrow">›</span>
      </button>
    </div>
  );
};

export default Landing;
