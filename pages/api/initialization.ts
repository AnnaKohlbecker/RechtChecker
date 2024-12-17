import { NextApiResponse } from "next";
import { spawn } from "child_process";

export default function handler(res: NextApiResponse) {
  const pythonVersion = process.env.PYTHON_EXECUTABLE || "python";
  const pythonProcess = spawn(pythonVersion, ["./scripts/initialization.py"]);

  let result = "";
  let error = "";

  // Listen for data output
  pythonProcess.stdout.on("data", (data) => {
    result += data.toString(); // Accumulate standard output
  });

  // Listen for errors
  pythonProcess.stderr.on("data", (data) => {
    error += data.toString(); // Accumulate error output
  });

  // On process close
  pythonProcess.on("close", (code) => {
    if (code === 0) {
      // If successful, send the result back as JSON
      try {
        const parsedResult = JSON.parse(result); // Parse the output if it's JSON
        res.status(200).json(parsedResult);
      } catch (parseError) {
        res.status(200).json({ output: result }); // Send raw output if not JSON
      }
    } else {
      res.status(500).json({
        error: "Python script failed",
        details: error || "Unknown error occurred",
      });
    }
  });
}
