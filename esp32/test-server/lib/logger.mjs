// Request logger middleware

const LOG_COLORS = {
  GET: '\x1b[32m',    // green
  POST: '\x1b[33m',   // yellow
  ERR: '\x1b[31m',    // red
  RESET: '\x1b[0m',
};

export function logRequest(req, statusCode, startTime) {
  const duration = Date.now() - startTime;
  const method = req.method || '?';
  const url = req.url || '/';
  const color = statusCode >= 400 ? LOG_COLORS.ERR : (LOG_COLORS[method] || LOG_COLORS.RESET);

  const timestamp = new Date().toISOString();
  console.log(
    `${timestamp} ${color}${method}${LOG_COLORS.RESET} ${url} → ${statusCode} (${duration}ms)`
  );
}
