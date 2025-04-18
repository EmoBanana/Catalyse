import React, { useState, useEffect } from "react";
import { Menu, Plus, Send, X, ChevronDown } from "react-feather";
import { useNavigate, useParams } from "react-router-dom";
import "./chat.css";
import graphData from "./graph_text_data.json";
import textData from "./text_data.json";
import alertData from "./alerts.json";
import Navigation from "./nav";
import MachineLearning from "./ml";
import Action from "./action";

const Chat = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hey! Anything you would like to know?",
      sender: "bot",
      timestamp: "Today",
    },
  ]); //Welcome message for the user

  const [isChatFocused, setIsChatFocused] = useState(false);
  const [isDashboardFull, setIsDashboardFull] = useState(false);
  const [expandedCard, setExpandedCard] = useState(null);
  const [expandedGraph, setExpandedGraph] = useState(null);
  const [expandedTextData, setExpandedTextData] = useState(null);
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [language, setLanguage] = useState("English");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [showNav, setShowNav] = useState(false);
  const [showML, setShowML] = useState(false);
  const [showAction, setShowAction] = useState(false);
  const navigate = useNavigate();
  const { id } = useParams();

  // List of languages
  const languages = [
    "English",
    "Spanish",
    "French",
    "German",
    "Chinese",
    "Japanese",
    "Korean",
    "Russian",
    "Arabic",
    "Hindi",
    "Portuguese",
    "Italian",
    "Dutch",
    "Swedish",
    "Finnish",
    "Norwegian",
    "Danish",
    "Polish",
    "Turkish",
    "Greek",
    "Hebrew",
    "Thai",
    "Vietnamese",
    "Indonesian",
    "Malay",
    "Filipino",
    "Bengali",
    "Urdu",
    "Persian",
    "Swahili",
  ];

  // Filtered languages based on search term
  const filteredLanguages = languages.filter((lang) =>
    lang.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSend = async () => {
    if (!message.trim()) return;

    const newUserMessage = {
      id: Date.now(),
      text: message,
      sender: "user",
      timestamp: "Today",
    };

    setMessages((prev) => [...prev, newUserMessage]);
    const userQuery = message;
    setMessage(""); // Clear input

    try {
      const response = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: userQuery,
          merchant_id: "0c2d7",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from server");
      }

      const data = await response.json();
      const aiReply = {
        id: Date.now() + 1,
        text: data.response,
        sender: "bot",
        timestamp: "Today",
      };

      setMessages((prev) => [...prev, aiReply]);
    } catch (error) {
      console.error("Error:", error);
      const errorReply = {
        id: Date.now() + 2,
        text: "Sorry, something went wrong while getting a response.",
        sender: "bot",
        timestamp: "Today",
      };
      setMessages((prev) => [...prev, errorReply]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }; // Handle Enter key press to send message

  const handleInputAreaClick = () => {
    setIsChatFocused(true);
    if (isDashboardFull) {
      setIsDashboardFull(false);
    }
  }; //Make Dashboard Preview hidden when Chat is focused

  const handlePullTabClick = () => {
    setIsDashboardFull(!isDashboardFull);
    setIsChatFocused(false);
  }; // Toggle Dashboard to full screen by clicking the pull tab

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

  const handleTextDataClick = (index) => {
    if (expandedTextData === index) {
      setExpandedTextData(null);
    } else {
      setExpandedTextData(index);
    }
  }; //Show or hide description of the sales highlight report when clicked

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

  const handleCardClick = (index) => {
    setExpandedCard(expandedCard === index ? null : index);
  }; // Show or hide description of the sales highlight report when clicked

  const toggleDropdown = (e) => {
    e.stopPropagation();
    setDropdownOpen(!dropdownOpen);
    if (!dropdownOpen) {
      setSearchTerm("");
    }
  }; // Handle language dropdown click

  const selectLanguage = (lang) => {
    setLanguage(lang);
    setDropdownOpen(false);
    setSearchTerm("");
  }; // Handle language selection

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  }; // Handle search term change

  useEffect(() => {
    const handleClickOutside = () => {
      setDropdownOpen(false);
    };

    if (dropdownOpen) {
      document.addEventListener("click", handleClickOutside);
    }

    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, [dropdownOpen]); // Close dropdown when clicking outside

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

  const groupedMessages = messages.reduce((groups, message) => {
    const date = message.timestamp;
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(message);
    return groups;
  }, {}); // Group messages by date

  return (
    <div>
      {showNav && (
        <Navigation
          setShowNav={setShowNav}
          setShowML={setShowML}
          setShowAction={setShowAction}
        />
      )}
      {showML && <MachineLearning setShowNav={setShowNav} />}
      {showAction && <Action setShowNav={setShowNav} />}{" "}
      {!showNav && !showML && !showAction && (
        <>
          <div
            className={`chat-container ${isChatFocused ? "chat-focused" : ""} ${
              isDashboardFull ? "chat-hidden" : ""
            }`}
            onClick={handleInputAreaClick}
          >
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

            <div className="messages-container">
              {Object.entries(groupedMessages).map(([date, dateMessages]) => (
                <div key={date} className="message-date-group">
                  <div className="date-header-container">
                    <p className="date-header">{date}</p>
                  </div>
                  {dateMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`message-bubble ${
                        msg.sender === "user" ? "user-message" : "bot-message"
                      }`}
                    >
                      <p>{msg.text}</p>
                    </div>
                  ))}
                </div>
              ))}
            </div>

            <div className="input-area">
              <div className="language-dropdown-container">
                <div className="language-selector" onClick={toggleDropdown}>
                  <span>{language}</span>
                  <ChevronDown size={16} className="chevron" />
                </div>
                {dropdownOpen && (
                  <div className="language-dropdown">
                    <div className="language-search">
                      <input
                        type="text"
                        placeholder="Search language..."
                        value={searchTerm}
                        onChange={handleSearchChange}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </div>
                    <div className="language-options">
                      {filteredLanguages.slice(0, 300).map((lang, index) => (
                        <div
                          key={index}
                          className={`language-option ${
                            language === lang ? "selected" : ""
                          }`}
                          onClick={() => selectLanguage(lang)}
                        >
                          {lang}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div className="message-input-container">
                <button className="action-button">
                  <Plus size={20} />
                </button>
                <textarea
                  className="input"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={`Ask Anything in ${language}`}
                />
                <button
                  className="action-button send-button"
                  onClick={handleSend}
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
          </div>

          <div
            className={`dashboard-placeholder ${
              isDashboardFull || isChatFocused ? "hidden" : ""
            }`}
          ></div>

          <div
            className={`dashboard ${
              isDashboardFull
                ? "dashboard-full"
                : isChatFocused
                ? "dashboard-hidden"
                : "dashboard-minimized"
            }`}
          >
            {/* Dashboard that provides insights based on merchant ID */}
            {id === "0c2d7" && (
              <>
                <div className="pull-tab" onClick={handlePullTabClick}></div>
                <div className="status-widgets">
                  <div className="sales-status">
                    {textData.map((data, index) => {
                      if (
                        data.title === "Total Sales" ||
                        data.title === "Ranking"
                      ) {
                        return (
                          <div
                            key={index}
                            className={`sales-card ${
                              expandedCard === index ? "expanded" : ""
                            }`}
                            onClick={() => handleCardClick(index)}
                          >
                            <p className="status-title">
                              {formatTitle(data.title)}
                            </p>
                            <p className="status-value">
                              {formatCurrentData(data.current_data)}
                            </p>
                            {expandedCard === index && (
                              <p className="description">{data.description}</p>
                            )}
                          </div>
                        );
                      }
                      return null;
                    })}
                  </div>

                  <div>
                    {alertData &&
                      Object.entries(alertData).map(([key, value], index) => (
                        <div key={index} className="alert-card">
                          <p className="alert-title">{formatTitle(key)}</p>
                          <p className="alert-description">{value}</p>
                        </div>
                      ))}
                  </div>

                  <div className="points">
                    {textData.map((data, index) => {
                      if (
                        data.title === "Transport" ||
                        data.title === "Market Price"
                      ) {
                        return (
                          <div
                            key={index}
                            className={`status-card textdata-card ${
                              expandedTextData === index ? "expanded" : ""
                            }`}
                            onClick={() => handleTextDataClick(index)}
                          >
                            <div className="textdata-header">
                              <p className="status-title">
                                {formatTitle(data.title)}
                              </p>
                              {expandedTextData === index && (
                                <button className="textdata-close-button">
                                  <X size={16} />
                                </button>
                              )}
                            </div>

                            <div className="textdata-content">
                              <div className="textdata-current-container">
                                {formatCurrentData(data.current_data)}
                              </div>

                              {expandedTextData === index && (
                                <div className="textdata-description">
                                  <h4>Analysis:</h4>
                                  <p>{data.description}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      }
                      return null;
                    })}
                  </div>

                  <div className="graphs">
                    {graphData.map((graph, index) => (
                      <div
                        key={index}
                        className={`graph-card ${
                          expandedGraph === index ? "expanded" : ""
                        }`}
                        onClick={() => handleGraphClick(index)}
                      >
                        <div className="graph-header">
                          <p className="graph-title">
                            {formatTitle(graph.title)}
                          </p>
                          {expandedGraph === index && (
                            <button className="close-button">
                              <X size={16} />
                            </button>
                          )}
                        </div>

                        <div className="graph-content">
                          <div
                            className="graph-image"
                            onClick={(e) =>
                              handleImageClick(e, graph.image_path, index)
                            }
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
                </div>
              </>
            )}
          </div>

          {imageModalOpen && selectedImage && (
            <div className="image-modal-overlay" onClick={handleCloseModal}>
              <div
                className="image-modal-content"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  className="modal-close-button"
                  onClick={handleCloseModal}
                >
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
        </>
      )}
    </div>
  );
};

export default Chat;
