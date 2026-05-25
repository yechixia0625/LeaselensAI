export interface DemoSession {
  authenticated: boolean;
  username: string | null;
  authEnabled: boolean;
}

export class UnauthorizedError extends Error {
  constructor() {
    super("unauthorized");
  }
}

export function isUnauthorizedError(error: unknown): boolean {
  return error instanceof Error && error.message === "unauthorized";
}

export class AuthService {
  static async session(): Promise<DemoSession> {
    const response = await fetch("/api/auth/session", {
      credentials: "include",
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error(`Session check failed: HTTP ${response.status}`);
    }
    return response.json();
  }

  static async login(username: string, password: string): Promise<DemoSession> {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (response.status === 401) {
      throw new UnauthorizedError();
    }
    if (!response.ok) {
      throw new Error(`Login failed: HTTP ${response.status}`);
    }
    return response.json();
  }

  static async logout(): Promise<void> {
    await fetch("/api/auth/logout", {
      method: "POST",
      credentials: "include",
    });
  }
}
