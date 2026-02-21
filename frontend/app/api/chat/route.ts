import { NextRequest, NextResponse } from 'next/server';

export const maxDuration = 120;

export async function POST(req: NextRequest) {
  const body = await req.json();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 115_000);

  try {
    const res = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(timeout);
    const data = await res.json();
    if (!res.ok) {
      return NextResponse.json(data, { status: res.status });
    }
    return NextResponse.json(data);
  } catch (err: any) {
    clearTimeout(timeout);
    if (err.name === 'AbortError') {
      return NextResponse.json(
        { detail: 'Request timed out — the AI is taking too long. Try a simpler message.' },
        { status: 504 },
      );
    }
    return NextResponse.json(
      { detail: err.message || 'Backend unreachable' },
      { status: 502 },
    );
  }
}
