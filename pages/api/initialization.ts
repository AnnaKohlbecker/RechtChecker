import { spawn } from "child_process";
import { NextApiRequest, NextApiResponse } from "next"

const handler = async(req: NextApiRequest, res: NextApiResponse): Promise<NextApiResponse> => {
    const pythonVersion = process.env.PYTHON_EXECUTABLE || "python3";
    const pythonProcess = spawn(pythonVersion, ["./scripts/initialization.py"]);

    //show pythonprocess output
    pythonProcess.stdout.on("data", (data) => {
      console.log(`stdout: ${data}`);
    });

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
  return res;
};

export default handler;