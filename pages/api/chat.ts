// import { Message } from "@/types";
// import { OpenAIStream } from "@/scripts/utils";

// export const config = {
//   runtime: "edge"
// };

// const handler = async (req: Request): Promise<Response> => {
//   try {
//     const { messages } = (await req.json()) as {
//       messages: Message[];
//     };

//     const charLimit = 12000;
//     let charCount = 0;
//     let messagesToSend = [];

//     for (let i = 0; i < messages.length; i++) {
//       const message = messages[i];
//       if (charCount + message.content.length > charLimit) {
//         break;
//       }
//       charCount += message.content.length;
//       messagesToSend.push(message);
//     }

//     const stream = await OpenAIStream(messagesToSend);

//     return new Response(stream);
//   } catch (error) {
//     console.error(error);
//     return new Response("Error", { status: 500 });
//   }
// };

// export default handler;

import { Message } from "@/types";
import { spawn } from "child_process";
import { NextApiRequest, NextApiResponse } from "next"

export const config = {
  runtime: "edge"
};

const handler = async (req: NextApiRequest, res: NextApiResponse): Promise<NextApiResponse> => {
  const body = req.body;
  const question  = body.question as Message;

  const pythonVersion = process.env.PYTHON_EXECUTABLE || "python3";
  const pythonProcess = spawn(pythonVersion, ["./scripts/main.py", JSON.stringify(question)]);

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