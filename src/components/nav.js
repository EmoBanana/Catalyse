import { X } from "react-feather";
import "./nav.css";

const Navigation = ({ setShowNav, setShowML, setShowAction }) => {
  const chat = () => {
    setShowNav(false);
    setShowML(false);
    setShowAction(false);
  };

  return (
    <div className="navigation-overlay">
      <div className="navigation-container">
        <div className="navigation-header">
          <h1>Navigation</h1>
          <X
            size={24}
            className="back-button"
            onClick={() => {
              setShowNav(false);
            }}
          />
        </div>

        <div className="navigation-options">
          <div
            className="nav-option"
            onClick={() => {
              setShowNav(false);
              setShowAction(false);
              setShowML(true);
            }}
          >
            <h2>Analytics</h2>
            <p>View Forecasting and Sentiments Analytics</p>
          </div>
          <div className="nav-option" onClick={() => chat()}>
            <h2>Chat</h2>
            <p>Talk With Our AI Assistant</p>
          </div>
          <div
            className="nav-option"
            onClick={() => {
              setShowNav(false);
              setShowML(false);
              setShowAction(true);
            }}
          >
            <h2>Actions</h2>
            <p>Perform Business Actions</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navigation;
