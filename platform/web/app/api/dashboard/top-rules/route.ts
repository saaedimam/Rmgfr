import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const projectId = searchParams.get('project_id');
    const hours = searchParams.get('hours') || '24';
    const limit = searchParams.get('limit') || '10';

    if (!projectId) {
      return NextResponse.json(
        { error: 'project_id is required' },
        { status: 400 }
      );
    }

    const response = await fetch(
      `${API_BASE_URL}/v1/dashboard/top-rules?project_id=${projectId}&hours=${hours}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching top rules:', error);
    return NextResponse.json(
      { error: 'Failed to fetch top rules' },
      { status: 500 }
    );
  }
}
