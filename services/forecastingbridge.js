const { spawn } = require("child_process");

function forecasting(inputData) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python", [
      "forecasting.py",
      inputData.merchant_id,
    ]);

    let output = "";
    let errorOutput = "";

    // If you don't need stdin, you might not write anything. Otherwise:
    pythonProcess.stdin.write(JSON.stringify(inputData));
    pythonProcess.stdin.end();

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        return reject(
          new Error(`Python script exited with code ${code}: ${errorOutput}`)
        );
      }
      // Log any warnings but resolve if exit code is 0.
      if (errorOutput.trim()) {
        console.warn("Python warnings/info:", errorOutput);
      }
      resolve(output.trim());
    });
  });
}

module.exports = { forecasting };
