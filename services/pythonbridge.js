const { spawn } = require("child_process");

/**
 * Runs the Python script with the provided input.
 * @param {Object} inputData - Contains `building_description` and `geosat`
 * @returns {Promise<string>} - Resolves with the Python script's output
 */
function p(inputData) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python", [""]); // Adjust path if needed

    pythonProcess.stdin.write(JSON.stringify(inputData));
    pythonProcess.stdin.end();

    let output = "";
    let errorOutput = "";

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0 || errorOutput) {
        return reject(new Error(`Python error: ${errorOutput}`));
      }
      resolve(output.trim());
    });
  });
}

module.exports = { p };
