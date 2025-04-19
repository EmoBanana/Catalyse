import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import googleCalendarPlugin from "@fullcalendar/google-calendar";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Menu, X } from "react-feather";
import "./action.css";
import menuData from "./menu.json";

const Action = ({ setShowNav }) => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [selectedImage, setSelectedImage] = useState(null);

  const handleLogout = () => {
    const confirmLogout = window.confirm("Are you sure you want to log out?");
    if (confirmLogout) {
      navigate("/login");
    }
  }; // Logout function to navigate back to login page

  const handleImageClick = (image) => {
    setSelectedImage(image);
  }; // Show the image in a modal when clicked

  const closeModal = () => {
    setSelectedImage(null);
  };

  useEffect(() => {
    const handler = (e) => {
      const dayCell = e.target.closest(".fc-daygrid-day");
      if (!dayCell) return;

      const moreLink = dayCell.querySelector(".fc-daygrid-more-link");
      if (moreLink) moreLink.click();
    }; // Click handler for the calendar to open the event details

    document
      .querySelector(".fc-daygrid-body")
      ?.addEventListener("click", handler);

    return () => {
      document
        .querySelector(".fc-daygrid-body")
        ?.removeEventListener("click", handler);
    };
  }, []); // Event listener to open the event details when clicked

  return (
    <div className="action-container">
      <div className="action-header">
        <Menu
          size={28}
          className="action-nav"
          onClick={() => setShowNav(true)}
        />
        <div className="action-profile" onClick={handleLogout}>
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

      <div className="action-calendar">
        <FullCalendar
          className="calendar"
          plugins={[dayGridPlugin, googleCalendarPlugin]}
          initialView="dayGridMonth"
          googleCalendarApiKey=""
          events={{
            googleCalendarId:
              "1fcbaedeedb15f25a1c8e71ad79eded5f1a118c95cf4c32f091ce736c140e41d@group.calendar.google.com",
          }}
          headerToolbar={{
            left: "prev",
            center: "title today",
            right: "next",
          }}
          height="50vh"
          dayMaxEvents={0}
          fixedWeekCount={false}
          eventDidMount={(info) => {
            const dayCell = info.el.closest(".fc-daygrid-day");
            if (dayCell && !dayCell.classList.contains("has-event")) {
              dayCell.classList.add("has-event");

              const dot = document.createElement("div");
              dot.className = "event-dot";
              dayCell.appendChild(dot);
            }
          }}
        />
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
                  onClick={() => handleImageClick(item.image)}
                />
                <h2 className="menu-title">{item.title}</h2>
                <div className="menu-details">
                  <p className="menu-price">
                    RM {parseFloat(item.price).toFixed(2)}
                  </p>
                  <button className="menu-status">Approve</button>
                </div>
              </div>
            ))}

            {menuData.ExistingMenu.map((item, index) => (
              <div key={index} className="menu-card">
                <img
                  src={`/${item.image}`}
                  alt={item.title}
                  className="menu-image"
                  onClick={() => handleImageClick(item.image)}
                />
                <h2 className="menu-title">{item.title}</h2>
                <div className="menu-details">
                  <p className="menu-price">
                    RM {parseFloat(item.price).toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedImage && (
        <div className="action-image-modal-overlay" onClick={closeModal}>
          <div
            className="action-image-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <X
              size={24}
              className="action-modal-close-button"
              onClick={closeModal}
            />
            <img
              src={`/${selectedImage}`}
              alt="Expanded"
              className="action-modal-image"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Action;
