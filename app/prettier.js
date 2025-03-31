import prettier from "prettier";

export default function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Only POST requests allowed" });
  }

  const { code } = req.body;
  if (!code) {
    return res.status(400).json({ error: 'Missing "code" in request body' });
  }

  try {
    const formattedCode = prettier.format(code, { parser: "babel" });
    return res.json({ formattedCode });
  } catch (error) {
    return res.status(500).json({ error: `Prettier Error: ${error.message}` });
  }
}
