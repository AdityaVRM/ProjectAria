import { NextRequest, NextResponse } from 'next/server';

const BACKEND = 'http://127.0.0.1:8000';

export async function GET(_req: NextRequest, { params }: { params: { userId: string } }) {
  const res = await fetch(`${BACKEND}/memory/${encodeURIComponent(params.userId)}`);
  return NextResponse.json(await res.json(), { status: res.status });
}

export async function PUT(req: NextRequest, { params }: { params: { userId: string } }) {
  const body = await req.json();
  const res = await fetch(`${BACKEND}/memory/${encodeURIComponent(params.userId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return NextResponse.json(await res.json(), { status: res.status });
}

export async function PATCH(req: NextRequest, { params }: { params: { userId: string } }) {
  const body = await req.json();
  const res = await fetch(`${BACKEND}/memory/${encodeURIComponent(params.userId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return NextResponse.json(await res.json(), { status: res.status });
}
