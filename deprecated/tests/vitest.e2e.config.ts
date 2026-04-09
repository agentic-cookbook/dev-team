import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    include: ["specs/*.test.ts"],
    testTimeout: 1_860_000,
    hookTimeout: 1_860_000,
    reporters: ["verbose"],
    pool: "threads",
    poolOptions: {
      threads: { maxThreads: 1 },
    },
  },
});
