import { NextResponse } from "next/server";

export async function GET() {
  try {
    const serverlessEndpointId = process.env.RUNPOD_SERVERLESS_ENDPOINT_ID;
    const serverlessUrl =
      process.env.RUNPOD_SERVERLESS_URL ||
      (serverlessEndpointId
        ? `https://api.runpod.ai/v2/${serverlessEndpointId}/runsync`
        : null);
    const runpodApiKey = process.env.RUNPOD_API_KEY;

    if (serverlessUrl) {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (runpodApiKey) {
        headers["Authorization"] = `Bearer ${runpodApiKey}`;
      }

      const res = await fetch(serverlessUrl, {
        method: "POST",
        headers,
        body: JSON.stringify({ input: { ping: true } }),
      });

      if (res.ok) {
        return NextResponse.json({
          status: "ok",
          message: "RunPod Serverless Worker is responsive",
          model: `RunPod Serverless (${serverlessEndpointId || "Endpoint"})`,
        });
      }
      return NextResponse.json(
        {
          status: "error",
          message: `RunPod Serverless returned HTTP ${res.status}`,
        },
        { status: 503 }
      );
    }

    const apiUrl = (process.env.API_INTERNAL_URL || "http://127.0.0.1:8000").replace(
      /\/+$/,
      ""
    );
    const res = await fetch(`${apiUrl}/health/llm`);
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { status: "error", message: `LLM health endpoint unreachable: ${msg}` },
      { status: 503 }
    );
  }
}
