# 😼Catalyse
*Meow-nitoring insights that drive business growth*

**Cat? Analyse?** That's right — **Catalyse** is a playful yet powerful analytics platform designed to deliver real-time business insights through an intuitive chat interface and dynamic dashboards. Whether you're a merchant looking to grow or a manager tracking market trends, Catalyse helps you *pounce* on opportunities faster than ever.

With Catalyse, you don’t just *analyse* — you **catalyse** your business growth.

## Links

**Canva:** https://www.canva.com/design/DAGk3sSgKpw/cBoxU5iOzEzptho0Gp9Pgg/edit

**Documentation:** https://drive.google.com/file/d/16ycshubPMgF7WbU9xgI-NLAambmdA3JR/view?usp=sharing

**Figma:** https://www.figma.com/design/ndrCJ23P9zEKPsanOMRhmd/UM-Hackathon?node-id=0-1&p=f&t=3juOFlnDM8khRVQx-0

## Features

- **Chat Interface**: 
  - Engage in a conversational experience to ask business-related questions.
  - Receive AI-generated insights tailored to your queries.
  - Messages are neatly grouped by date for enhanced readability.

- **Dynamic Dashboard**:
  - Displays key metrics including:
      - Total Sales
      - Product Rankings
      - Transport & Logistic Data
      - Market Prices
  - Includes alerts highlighting bottlenecks and growth opportunities.
  - Interactive graphs and expandable data cards let you explore details on demand.

- **Merchant-Specific Insights**:
  - Each merchant has a personalised dashboard reflecting their business data.
  - Supports focused decision-making with precise, relevant insights.
 
- **Actions Page**
  - Integrated with Google Calendar to track business-related events.
  Merchants can ask the chatbot to generate event plans (e.g., a one-week timeline for a product launch), which will be automatically added to the calendar.
  - Includes a menu section that displays current menu items; new items suggested by the chatbot appear first and await merchant approval

- **Analytics Page**
  - View forecasting graphs powered by Prophet for predictive, data-driven decisions.
  - Dive into sentiment analytics with:
    - A distribution chart of positive, neutral, and negative reviews
    - Word clouds highlighting key terms from positive and negative feedback

- **Responsive Design**:
  - Enjoy a smooth experience across devices — from mobile to desktop.
  - Seamless transitions between chat and dashboard views.

## Basic Troubleshooting

**Issue:** `ModuleNotFoundError` or missing packages  
**Solution:**  
Run `npm install` or `pip install -r requirements.txt`.  
Ensure you’re in the correct directory.

**Issue:** App fails to connect to API/backend  
**Solution:**  
Create a `.env` file with the required keys. Check `.env.example` for reference.  
Ensure variables like `API_KEY`, `BACKEND_URL`, or `OPENAI_API_KEY` are defined.

**Issue:** AI Model is not generating responses  
**Solution:**  
- Check your internet connection.  
- Make sure your API key is valid and not rate-limited.  

**Issue:** Chat window not responding or stuck  
**Solution:**  
- Refresh the app 

## Powered by Machine Learning

Catalyse leverages a custom ML model trained on a synthetic business dataset to deliver smart recommendations and adaptive insights. 
- **Meta Prophet** powers our forecasting capabilities, providing accurate trend predictions through detailed graphs, enabling merchants to make proactive, data-backed decisions.
- Sentiment analysis transforms customer reviews into actionable insights with distribution charts and keyword-focused word clouds

The system evolves with usage, continuously learning and fine-tuning its responses to better align with each merchant's unique operations.

## Supported by **Model Context Protocol (MCP)**

Catalyse is enhanced by the **Model Context Protocol (MCP)** to enable seamless, context-aware AI interactions across features.
- **Standardised Connectivity**: Allows the AI to interact with external tools and services through a unified protocol.
- **Context Retention**: Maintains awareness of ongoing tasks, ensuring consistent and relevant responses.
- **Scalable Integration**: Easily connects to tools like calendars, databases, and content systems to enhance functionality.

MCP ensures that every AI interaction in Catalyse feels smart, relevant, and securely integrated.

## Why Catalyse?

Because your business deserves to:
- **Grow smarter, not harder**
- **Catch trends before they pass**
- **And most importantly — meow-nitor insights like a pro**

## Tech Stack

- **Frontend:** React
- **Backend:** Node.js
- **ML Engine:** Python
- **Database:** MongoDB

## Live Demo

Check out our [live demo on Vercel](https://cat-alyse.vercel.app/) to experience Catalyse for yourself. 

## Cloning and Running Locally

Follow these steps to clone the repository and run the application locally.

## Prerequisites

Before you can run the application, you need to have the following installed:
- **Node.js** (v14.0.0 or higher)
  [Download Node.js](https://nodejs.org/en)
- **npm** (Node Package Manager)
  npm is bundled with Node.js, so you don't need to install it separately if you have Node.js.
- **WSL/Ubuntu** (on Windows)
  Install using:
  ```bash
    wsl --install
  ```
- **Python** (for ML model)
  [Download Python](https://www.python.org/downloads/)
- **uv** (a fast Python package manager)
  Install after entering WSL using:
  ```bash
    pip install uv
  ```

## Installation

To get started with **Catalyse**, clone the repository and install the dependencies:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/EmoBanana/Catalyse.git
   ```

2. **Navigate to the project directory**:
   ```bash
   cd Catalyse
   ```

### Backend (Inside WSL)

1. **Enter WSL**
   ```bash
     wsl
   ```

2. **Navigate to the backend directory**
   ```bash
     cd ~/Catalyse/mcp
   ```

3. **Install Python dependencies using `uv`**
   ```bash
     uv pip install -r requirements.txt
   ```

4. **Run the backend server**
   ```bash
     uvicorn client:app --reload
   ```

### Frontend (From project root on host machine)

1. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

### Running the Application

To start the application locally, run the following command:

```bash
npm start
```

This will start the development server, and the app should automatically open in your default browser. If not, visit `http://localhost:3000` to view the application.

## Contributing

We welcome contributions! Feel free to submit issues or pull requests to improve Catalyse.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

---

Made with ❤️
