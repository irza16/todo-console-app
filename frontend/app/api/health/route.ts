import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ 
    status: 'healthy',
    message: 'Frontend service is running',
    timestamp: new Date().toISOString()
  });
}