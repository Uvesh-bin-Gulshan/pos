// Get server-side API URL from environment variables
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

/**
 * Reusable server-side GET request handler
 */
export async function serverGet<T>(
  endpoint: string,
  options: {
    token?: string;
    cache?: RequestCache;
    tags?: string[];
    params?: Record<string, any>;
  } = {}
): Promise<{ data: T | null; error: string | null }> {
  try {
    const url = `${API_BASE_URL}${endpoint}${
      options.params ? `?${new URLSearchParams(options.params).toString()}` : ''
    }`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(options.token && { Authorization: `Bearer ${options.token}` }),
      },
      cache: options.cache || 'no-store',
      ...(options.tags && { next: { tags: options.tags } }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: T = await response.json();
    return { data, error: null };
  } catch (error) {
    return handleApiError<T>(error);
  }
}

/**
 * Reusable server-side data submission handler
 */
export async function serverSubmit<T>(
  endpoint: string,
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  payload: any,
  token?: string
): Promise<{ data: T | null; error: string | null }> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(errorBody || `HTTP error! status: ${response.status}`);
    }

    const data: T = await response.json();
    return { data, error: null };
  } catch (error) {
    return handleApiError<T>(error);
  }
}

/**
 * Handle API errors consistently
 */
function handleApiError<T>(error: unknown): { data: null; error: string } {
  if (error instanceof Error) {
    return { data: null, error: error.message };
  }
  return { data: null, error: 'Unknown server error' };
}

/**
 * Server-side auth token retrieval
 */
export function getAuthToken() {
  // In real implementation, retrieve from cookies/headers
  return '';
}
