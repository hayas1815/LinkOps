export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type ClientOptions = {
  method?: HttpMethod;
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
};

export class ApiClient {
  constructor(private readonly baseUrl: string) {}

  async request<TResponse>(path: string, options: ClientOptions = {}): Promise<TResponse> {
    const { method = 'GET', headers, body, signal } = options;

    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      signal,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`API client placeholder error: ${response.status}`);
    }

    return (await response.json()) as TResponse;
  }
}
