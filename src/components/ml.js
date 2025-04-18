import React, { useState, useEffect } from "react";
import { Menu, X } from "react-feather";
import { useNavigate, useParams } from "react-router-dom";
import "./ml.css";
import graphData from "./graph_text_data.json";
import menuData from "./menu.json";

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

  const formatCurrentData = (data) => {
    try {
      const sanitizedData = data
        .replace(/NaN/g, "null")
        .replace(/"nan%"/g, '"N/A"');

      // Handle simple string values with currency
      if (sanitizedData.startsWith('"') && sanitizedData.endsWith('"')) {
        const value = JSON.parse(sanitizedData);
        if (value.startsWith("RM ")) {
          const numericValue = parseFloat(value.replace("RM ", ""));
          return (
            <div className="textdata-current-list">
              <div className="textdata-row">
                <span className="textdata-quantity">
                  RM{" "}
                  {numericValue.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </span>
              </div>
            </div>
          );
        }
        return (
          <div className="textdata-current-list">
            <div className="textdata-row">
              <span className="textdata-quantity">{value}</span>
            </div>
          </div>
        );
      }

      const parsedData = JSON.parse(sanitizedData);

      if (Array.isArray(parsedData)) {
        return (
          <div className="textdata-current-list">
            {parsedData.map((item, idx) => (
              <div key={idx} className="textdata-item">
                {Object.entries(item).map(([key, value]) => {
                  const formattedKey = key
                    .replace(/_/g, " ")
                    .split(" ")
                    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(" ");

                  const formattedValue =
                    value === null ||
                    (typeof value === "number" && isNaN(value))
                      ? "N/A"
                      : typeof value === "number"
                      ? value.toLocaleString()
                      : value.toString();

                  // Skip key display if it's an empty string or just whitespace
                  const showKey = key.trim().length > 0;

                  return (
                    <div key={key} className="textdata-row">
                      {showKey && (
                        <span className="textdata-name">{formattedKey}:</span>
                      )}
                      <span className="textdata-quantity">
                        {formattedValue}
                      </span>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        );
      } else if (typeof parsedData === "object") {
        return (
          <div className="textdata-current-list">
            {Object.entries(parsedData).map(([key, value], idx) => {
              const formattedKey = key
                .replace(/_/g, " ")
                .split(" ")
                .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" ");

              const formattedValue =
                value === null || (typeof value === "number" && isNaN(value))
                  ? "N/A"
                  : typeof value === "number"
                  ? value.toLocaleString()
                  : value.toString();

              // Skip key display if it's an empty string or just whitespace
              const showKey = key.trim().length > 0;

              return (
                <div key={idx} className="textdata-row">
                  {showKey && (
                    <span className="textdata-name">{formattedKey}:</span>
                  )}
                  <span className="textdata-quantity">{formattedValue}</span>
                </div>
              );
            })}
          </div>
        );
      }
    } catch (error) {
      return <div>Error parsing data</div>;
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

      <div className="ml-graphs">
        {graphData.map((graph, index) => (
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
                    {formatCurrentData(graph.current_data)}
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
          <h1>Menu</h1>
        </div>
        <div className="menu-scroll-container">
          <div className="menu-cards-row">
            {menuData.newMenu.map((item, index) => (
              <div key={index} className="newmenu-card">
                <img
                  src={`/${item.image}`}
                  alt={item.title}
                  className="menu-image"
                  onClick={() => handleImageClick(item.image)} // Handle image click
                />
                <h2 className="menu-title">{item.title}</h2>
                <div className="menu-details">
                  <p className="menu-genre">{item.genre}</p>
                  <p className="menu-price">{item.price}</p>
                </div>
              </div>
            ))}

            {menuData.existingMenu.map((item, index) => (
              <div key={index} className="menu-card">
                <img
                  src={`/${item.image}`}
                  alt={item.title}
                  className="menu-image"
                  onClick={() => handleImageClick(item.image)} // Handle image click
                />
                <h2 className="menu-title">{item.title}</h2>
                <div className="menu-details">
                  <p className="menu-genre">{item.genre}</p>
                  <p className="menu-price">{item.price}</p>
                </div>
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
