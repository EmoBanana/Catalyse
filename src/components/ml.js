import React, { useState, useEffect } from "react";
import { Menu, X } from "react-feather";
import { useNavigate, useParams } from "react-router-dom";
import "./ml.css";
import mlData from "./machine_learning_data.json";

const Chat = ({ setShowNav }) => {
  const [expandedGraph, setExpandedGraph] = useState(null);
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const navigate = useNavigate();
  const { id } = useParams();

  const handleLogout = () => {
    const confirmLogout = window.confirm("Are you sure you want to log out?");
    if (confirmLogout) {
      navigate("/login");
    }
  }; // Logout function to navigate back to login page

  const handleGraphClick = (index) => {
    if (expandedGraph === index) {
      setExpandedGraph(null);
    } else {
      setExpandedGraph(index);
    }
  }; //Show or hide description of the graph when clicked

  const handleImageClick = (e, imagePath, index) => {
    if (expandedGraph === index) {
      setSelectedImage(imagePath);
      setImageModalOpen(true);
    }
  }; //Show graphs sideways when clicked for maximum visibility

  const handleCloseModal = () => {
    setImageModalOpen(false);
    setSelectedImage(null);
  }; //Close the image modal when clicked outside of the image

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && imageModalOpen) {
        handleCloseModal();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [imageModalOpen]);

  const formatTitle = (title) => {
    return title
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatCurrentData = (data, title) => {
    try {
      // Check if it's JSON format
      if (data.startsWith("{")) {
        const parsed = JSON.parse(data);

        // Add RM prefix only for "monthly_income"
        if (title === "monthly_income" && parsed.yhat) {
          return `RM ${parseFloat(parsed.yhat).toFixed(2)}`;
        }

        // Return parsed yhat value without RM prefix for other cases
        if (parsed.yhat) {
          return `${parseFloat(parsed.yhat).toFixed(2)}`;
        }

        return data;
      }

      // Check if it's already in RM format
      else if (data.startsWith("RM")) {
        const value = parseFloat(data.replace("RM ", ""));
        return `RM ${value.toFixed(2)}`;
      }

      return data;
    } catch (e) {
      return data;
    }
  };

  return (
    <div className="ml-container">
      <div className="header">
        <Menu
          size={28}
          className="back-button"
          onClick={() => setShowNav(true)}
        />
        <div className="profile" onClick={handleLogout}>
          {/* Profile picture and merchant name based on the merchant ID */}
          {id === "0c2d7" && (
            <>
              <h2>Fried Chicken Express</h2>
              <img
                src="/profile1.jpg"
                alt="Profile"
                className="profile-picture"
              />
            </>
          )}
          {id === "3b7f0" && (
            <>
              <h2>Donut Palace</h2>
              <img
                src="/profile2.jpg"
                alt="Profile"
                className="profile-picture"
              />
            </>
          )}
        </div>
      </div>

      <div className="ml-header-container">
        <h1 className="ml-header">Forecasting Analytics</h1>
      </div>

      <div className="ml-graphs">
        {mlData.MachineLearning.map((graph, index) => (
          <div
            key={index}
            className={`graph-card ${
              expandedGraph === index ? "expanded" : ""
            }`}
            onClick={() => handleGraphClick(index)}
          >
            <div className="graph-header">
              <p className="graph-title">{formatTitle(graph.title)}</p>
              {expandedGraph === index && (
                <button className="close-button">
                  <X size={16} />
                </button>
              )}
            </div>

            <div className="graph-content">
              <div
                className="graph-image"
                onClick={(e) => handleImageClick(e, graph.image_path, index)}
              >
                <img
                  src={`/${graph.image_path}`}
                  alt={graph.title}
                  className="clickable-image"
                />
                {expandedGraph === index && (
                  <div className="image-overlay">
                    <span>Click to enlarge</span>
                  </div>
                )}
              </div>

              {expandedGraph === index && (
                <div className="graph-details">
                  <div className="current-data">
                    <h4>Current Status:</h4>
                    {formatCurrentData(graph.current_data, graph.title)}
                  </div>
                  <div className="graph-description">
                    <h4>Analysis:</h4>
                    <p>{graph.description}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="action-menu">
        <div className="menu-header">
          <h1>Sentiments Analytics</h1>
        </div>
        <div className="menu-scroll-container">
          <div className="menu-cards-row">
            {mlData.TextAnalytics.map((item, index) => (
              <div key={index} className="menu-card">
                <h2 className="ml-menu-title">{item.title}</h2>
                <img
                  src={`/${item.image}`}
                  alt={item.title}
                  className="ml-menu-image"
                  onClick={() => handleImageClick(item.image)} // Handle image click
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {imageModalOpen && selectedImage && (
        <div className="image-modal-overlay" onClick={handleCloseModal}>
          <div
            className="image-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <button className="modal-close-button" onClick={handleCloseModal}>
              <X size={24} />
            </button>
            <img
              src={`/${selectedImage}`}
              alt="Enlarged graph"
              className="modal-image"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
