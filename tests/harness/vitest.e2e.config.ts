import { defineConfig } from "vitest/config";

/** E2E config — only interview tests that invoke Claude. */
export default defineConfig({
  test: {
    globals: true,
    include: ["specs/*.test.ts"],
    exclude: ["specs/unit/**"],
    testTimeout: 960_000, // 16 minutes — interviews with agent spawns are slow
    hookTimeout: 960_000, // 16 minutes — beforeAll runs the interview
    reporters: ["verbose"],
    pool: "threads",
    poolOptions: {
      threads: { maxThreads: 1 }, // serialize — one interview at a time
    },
  },
});
