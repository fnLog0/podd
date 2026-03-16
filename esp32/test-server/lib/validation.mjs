// Validation helpers

// Max upload size: 512 KB (ESP32 sends ~64 KB for 2s recording)
export const MAX_UPLOAD_BYTES = 512 * 1024;

export function isSafePath(userPath) {
  // Reject path traversal attempts
  if (userPath.includes('..') || userPath.includes('\0')) {
    return false;
  }
  // Only allow alphanumeric, dash, underscore, dot, and forward slash
  return /^[a-zA-Z0-9_\-./]+$/.test(userPath);
}

export function validateUploadSize(length) {
  if (length === 0) {
    return { ok: false, error: 'Empty upload body' };
  }
  if (length > MAX_UPLOAD_BYTES) {
    return { ok: false, error: `Upload too large: ${length} bytes (max ${MAX_UPLOAD_BYTES})` };
  }
  return { ok: true };
}
