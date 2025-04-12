import React, { useState, useEffect } from "react";
import { Plus, Send, X } from "react-feather";
import { useNavigate, useParams } from "react-router-dom";
import "./chat.css";
import graphData from "./graph_text_data.json";
import textData from "./text_data.json";

const Chat = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hey! Anything you would like to know?",
      sender: "bot",
      timestamp: "Today",
    },
  ]);

  const [isChatFocused, setIsChatFocused] = useState(false);
  const [isDashboardFull, setIsDashboardFull] = useState(false);
  const [expandedGraph, setExpandedGraph] = useState(null);
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const navigate = useNavigate();
  const { id } = useParams();

  const handleSend = () => {
    if (message.trim()) {
      setMessages([
        ...messages,
        {
          id: Date.now(),
          text: message,
          sender: "user",
          timestamp: "Today",
        },
      ]);
      setMessage("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputAreaClick = () => {
    setIsChatFocused(true);
    if (isDashboardFull) {
      setIsDashboardFull(false);
    }
  };

  const handlePullTabClick = () => {
    setIsDashboardFull(!isDashboardFull);
    setIsChatFocused(false);
  };

  const handleLogout = () => {
    const confirmLogout = window.confirm("Are you sure you want to log out?");
    if (confirmLogout) {
      navigate("/login");
    }
  };

  const handleGraphClick = (index) => {
    if (expandedGraph === index) {
      setExpandedGraph(null);
    } else {
      setExpandedGraph(index);
    }
  };

  const handleImageClick = (e, imagePath, index) => {
    if (expandedGraph === index) {
      setSelectedImage(imagePath);
      setImageModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setImageModalOpen(false);
    setSelectedImage(null);
  };

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
    if (data === "null") return "No current data available";

    try {
      const parsedData = JSON.parse(data);

      if (Array.isArray(parsedData)) {
        return (
          <div className="current-data-list">
            {parsedData.map((item, idx) => (
              <div key={idx} className="data-item">
                <span className="item-name">{item.item_name}:</span>
                <span className="item-quantity">
                  {item.monthly_quantity.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        );
      } else if (typeof parsedData === "object") {
        return Object.entries(parsedData).map(([key, value], idx) => (
          <div key={idx} className="data-item">
            <span className="item-name">{key.replace(/_/g, " ")}:</span>
            <span className="item-quantity">{value.toLocaleString()}</span>
          </div>
        ));
      }

      return JSON.stringify(parsedData);
    } catch (error) {
      return data;
    }
  };

  const groupedMessages = messages.reduce((groups, message) => {
    const date = message.timestamp;
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(message);
    return groups;
  }, {});

  return (
    <div>
      <div
        className={`chat-container ${isChatFocused ? "chat-focused" : ""} ${
          isDashboardFull ? "chat-hidden" : ""
        }`}
        onClick={handleInputAreaClick}
      >
        <div className="header">
          <button className="back-button">
            <h1 className="back-arrow">‹</h1>
            <span>Chats</span>
          </button>
          <div className="profile" onClick={handleLogout}>
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
          <div className="message-input-container">
            <button className="action-button">
              <Plus size={20} />
            </button>
            <textarea
              className="input"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Anything"
            />
            <button className="action-button send-button" onClick={handleSend}>
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
        {id === "0c2d7" && (
          <>
            <div className="pull-tab" onClick={handlePullTabClick}></div>
            <div className="status-widgets">
              <div className="sales-status">
                <div className="sales-card">
                  <p className="status-title">Total Sales</p>
                  <p className="status-value">RM6000</p>
                </div>

                <div className="sales-card">
                  <p className="status-title">Best Selling Item</p>
                  <p className="status-value">Fried Chicken</p>
                </div>
              </div>

              <div className="points">
                <div className="status-card">
                  <p className="status-title">Critical Issues: Lorem Ipsum</p>
                </div>

                <div className="status-card">
                  <p className="status-title">
                    Improvement Suggestions: Lorem Ipsum
                  </p>
                </div>
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
        {id === "3b7f0" && (
          <>
            <div className="pull-tab" onClick={handlePullTabClick}></div>
            <div className="status-widgets">
              <div className="sales-status">
                <div className="sales-card">
                  <p className="status-title">Total Sales</p>
                  <p className="status-value">RM4500</p>
                </div>

                <div className="sales-card">
                  <p className="status-title">Best Selling Item</p>
                  <p className="status-value">Donuts</p>
                </div>
              </div>

              <div className="points">
                <div className="status-card">
                  <p className="status-title">Critical Issues: Lorem Ipsum</p>
                </div>

                <div className="status-card">
                  <p className="status-title">
                    Improvement Suggestions: Lorem Ipsum
                  </p>
                </div>
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
                      <p className="graph-title">{formatTitle(graph.title)}</p>
                      {expandedGraph === index && (
                        <button className="close-button">
                          <X size={16} />
                        </button>
                      )}
                    </div>

                    <div className="graph-content">
                      <div className="graph-image">
                        <img
                          src={`/${graph.image_path}`}
                          alt={graph.title}
                          onClick={(e) =>
                            handleImageClick(e, graph.image_path, index)
                          }
                        />
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
