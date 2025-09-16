import { NextRequest, NextResponse } from "next/server";
import { API_BASE, PROJECT_API_KEY } from "../../../../lib/serverEnv";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const projectId = searchParams.get('project_id') || 'demo';

    const response = await fetch(`${API_BASE}/v1/analytics/dashboard?project_id=${projectId}`, {
      headers: {
        'x-api-key': PROJECT_API_KEY,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Analytics dashboard error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analytics data' },
      { status: 500 }
    );
  }
}
