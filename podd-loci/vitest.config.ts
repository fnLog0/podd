import { defineConfig } from "vitest/config";
import dotenv from "dotenv";

dotenv.config();

export default defineConfig({
  test: {
    globals: true,
    testTimeout: 30_000,
    hookTimeout: 15_000,
  },
});
