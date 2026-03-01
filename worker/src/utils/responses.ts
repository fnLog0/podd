import type { AppContext } from "../types";

export function success<T>(c: AppContext, data: T, status = 200) {
  return c.json({ success: true, data }, status as 200);
}

export function error(c: AppContext, message: string, status = 400) {
  return c.json({ success: false, error: message }, status as 400);
}

export function unauthorized(c: AppContext, message = "Unauthorized") {
  return c.json({ success: false, error: message }, 401 as 401);
}
