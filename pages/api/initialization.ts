import { NextApiRequest, NextApiResponse } from "next";
import { spawn } from "child_process";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const pythonProcess = spawn("python3", ["./scripts/initialization.py"]);

  pythonProcess.stdout.on("data", (data) => {
    console.log(`Output: ${data}`);
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`Error: ${data}`);
  });

  pythonProcess.on("close", (code) => {
    console.log(`Initialization function exited with code ${code}`);
    res.status(200).json({ message: "Initialization function executed successfully" });
  });
}
