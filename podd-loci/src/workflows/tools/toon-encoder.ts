import { encode } from "@toon-format/toon";

export function toToon(data: unknown): string {
  if (data === null || data === undefined) return "";
  if (typeof data === "string") return data;
  try {
    return encode(data as Record<string, unknown>);
  } catch {
    return JSON.stringify(data, null, 2);
  }
}
