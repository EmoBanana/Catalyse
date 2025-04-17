import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import googleCalendarPlugin from "@fullcalendar/google-calendar";
import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Menu } from "react-feather";
import "./action.css";

const Action = ({ setShowNav }) => {
  const navigate = useNavigate();
  const { id } = useParams();

  const handleLogout = () => {
    const confirmLogout = window.confirm("Are you sure you want to log out?");
    if (confirmLogout) {
      navigate("/login");
    }
  };

  useEffect(() => {
    const handler = (e) => {
      const dayCell = e.target.closest(".fc-daygrid-day");
      if (!dayCell) return;

      // Look for the hidden "+ more" link
      const moreLink = dayCell.querySelector(".fc-daygrid-more-link");
      if (moreLink) moreLink.click();
    };

    document
      .querySelector(".fc-daygrid-body")
      ?.addEventListener("click", handler);

    return () => {
      document
        .querySelector(".fc-daygrid-body")
        ?.removeEventListener("click", handler);
    };
  }, []);

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
    </div>
  );
};

export default Action;
