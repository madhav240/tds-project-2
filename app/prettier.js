import { NextRequest, NextResponse } from "next/server";
import prettier from "prettier";

export const config = {
  runtime: "edge", // Use Vercel Edge functions for performance
};

export default async function handler(req) {
  try {
    if (req.method !== "POST") {
      return new NextResponse("Only POST requests allowed", { status: 405 });
    }

    // Read text content from request body
    const { code } = await req.json();

    if (!code) {
      return new NextResponse('Missing "code" in request body', {
        status: 400,
      });
    }

    // Format code using Prettier
    const formattedCode = prettier.format(code, { parser: "babel" });

    return NextResponse.json({ formattedCode });
  } catch (error) {
    return new NextResponse(`Prettier Error: ${error.message}`, {
      status: 500,
    });
  }
}
