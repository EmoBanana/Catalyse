import React, { useState } from "react";
import { Plus, Send } from "react-feather";
import { useNavigate, useParams } from "react-router-dom";
import "./chat.css";

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
    setIsDashboardFull(false);
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
        className={`dashboard ${
          isDashboardFull ? "dashboard-full" : "dashboard-minimized"
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
                <div className="graph-card">
                  <p className="graph-title">Graphs</p>
                </div>

                <div className="graph-card">
                  <p className="graph-title">Graphs</p>
                </div>
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
                <div className="graph-card">
                  <p className="graph-title">Graphs</p>
                </div>

                <div className="graph-card">
                  <p className="graph-title">Graphs</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Chat;
