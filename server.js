const express = require("express");
const app = express();
const PORT = 5000;
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");

const cors = require("cors");
app.use(
  cors({
    origin: "http://localhost:3000",
  })
);
const { p } = require("./services/pythonbridge");
const { MongoClient } = require("mongodb");
const { forecasting } = require("./services/forecastingbridge");
// MongoDB URI (same as your friend's Python script)
const uri =
  "mongodb+srv://haohong0127:Hongwork123@cluster.xlxyiby.mongodb.net/?retryWrites=true&w=majority&appName=Cluster";
const client = new MongoClient(uri);
app.use(express.json());
// Define a generic fetch function
const fetchData = async (collectionName) => {
  await client.connect();
  const db = client.db("Umhack");
  const data = await db.collection(collectionName).find({}).toArray();
  return data;
};
const { finalpipe } = require("./services/final");
// === API Routes ===
// first step send mechent id to the engine

app.post("/merchant", async (req, res) => {
  const { merchant_id } = req.body;
  try {
    console.log("running forecasting");
    await forecasting({ merchant_id });
  } catch (err) {
    console.error("Composite/merchant failed:", err);
    res.status(500).json({ error: err.message });
  }
});
app.post("/final", async (req, res) => {
  const { merchant_id } = req.body;
  try {
    console.log("running final pipe");
    await finalpipe({ merchant_id });
  } catch (err) {
    console.error("Composite/final failed:", err);
    res.status(500).json({ error: err.message });
  }
});
// Call initial_analysis()
app.get("/analysis", (req, res) => {
  const py = spawn("python", ["mcp/client.py"]);

  py.stdout.on("data", (data) => {
    console.log(`stdout: ${data}`);
  });

  py.stderr.on("data", (data) => {
    console.error(`stderr: ${data}`);
  });

  py.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).send("Error running analysis");
    }

    const graphPath = path.join(__dirname, "graph_text_data.json");
    const textPath = path.join(__dirname, "text_data.json");
    const bottleneckPath = path.join(__dirname, "bottleneck_opportunity.json");

    const graphData = fs.readFileSync(graphPath, "utf8");
    const textData = fs.readFileSync(textPath, "utf8");
    const bottleneckData = fs.readFileSync(bottleneckPath, "utf8");

    res.json({
      graph: JSON.parse(graphData),
      text: JSON.parse(textData),
      suggestions: JSON.parse(bottleneckData),
    });
  });
});

// Call normal_run(query)
app.post("/ask", (req, res) => {
  const query = req.body.query;
  const merchant_id = req.body.merchant_id;
  if (!query) return res.status(400).json({ error: "Missing query" });
  if (!merchant_id) return res.status(400).json({ error: "Missing id" });

  const py = spawn("python", ["mcp/client.py", query, merchant_id]);
  console.log(query);

  let result = "";
  py.stdout.on("data", (data) => {
    result += data.toString();
  });

  py.stderr.on("data", (data) => {
    console.error(`stderr: ${data}`);
  });

  py.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).send("Error processing query");
    }
    res.send({ response: result.trim() });
  });
});
// Start server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
