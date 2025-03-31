import prettier from "prettier";

// Vercel requires async handlers for Node.js functions
export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Only POST requests allowed" });
  }

  try {
    // Parse JSON body explicitly
    const { code } = JSON.parse(req.body);
    
    if (!code) {
      return res.status(400).json({ error: 'Missing "code" in request body' });
    }

    const formattedCode = await prettier.format(code, {
      parser: "babel",
    });

    return res.json({ formattedCode });
  } catch (error) {
    return res.status(500).json({ 
      error: error.message.startsWith("SyntaxError") 
        ? `Code syntax error: ${error.message}` 
        : `Formatting failed: ${error.message}`
    });
  }
}
