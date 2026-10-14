import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const serverlessEndpointId = process.env.RUNPOD_SERVERLESS_ENDPOINT_ID;
    const serverlessUrl =
      process.env.RUNPOD_SERVERLESS_URL ||
      (serverlessEndpointId
        ? `https://api.runpod.ai/v2/${serverlessEndpointId}/runsync`
        : null);
    const runpodApiKey = process.env.RUNPOD_API_KEY;

    // Mode: RunPod Serverless
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
        body: JSON.stringify({
          input: {
            session_id: body.session_id,
            user_id: body.user_id,
            message: body.message,
          },
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        return NextResponse.json(
          { detail: `Serverless error (${res.status}): ${errText}` },
          { status: res.status }
        );
      }

      const runpodJson = await res.json();
      // RunPod returns { status: "COMPLETED", output: { status: "success", data: { ... } } }
      if (runpodJson.output?.data) {
        return NextResponse.json(runpodJson.output.data);
      } else if (runpodJson.output?.error) {
        return NextResponse.json(
          { detail: runpodJson.output.error },
          { status: 400 }
        );
      } else if (runpodJson.error) {
        return NextResponse.json(
          { detail: runpodJson.error },
          { status: 500 }
        );
      }
      return NextResponse.json(runpodJson.output || runpodJson);
    }

    // Mode: HTTP API (Pod / Container / Local FastAPI)
    const apiUrl = (process.env.API_INTERNAL_URL || "http://127.0.0.1:8000").replace(
      /\/+$/,
      ""
    );
    const res = await fetch(`${apiUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { detail: `Proxy communication error: ${msg}` },
      { status: 502 }
    );
  }
}
