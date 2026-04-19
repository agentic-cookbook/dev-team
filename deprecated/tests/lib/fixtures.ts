import {
  mkdtempSync,
  mkdirSync,
  rmSync,
  writeFileSync,
  copyFileSync,
  existsSync,
} from "fs";
import { join, resolve } from "path";
import { tmpdir } from "os";

const FIXTURES_DIR = join(import.meta.dirname, "../fixtures");

function repoRoot(): string {
  return resolve(import.meta.dirname, "../../..");
}

export function createTestCookbook(name: string): string {
  const dest = mkdtempSync(join(tmpdir(), `cookbook-test-${name}-`));
  const root = repoRoot();

  const dirs = [
    "principles",
    "guidelines/testing",
    "recipes/infrastructure",
    "compliance/artifact-formatting",
    "introduction",
    ".claude",
  ];
  for (const d of dirs) {
    mkdirSync(join(dest, d), { recursive: true });
  }

  copyFileSync(
    join(FIXTURES_DIR, "valid-principle.md"),
    join(dest, "principles/simplicity.md")
  );
  copyFileSync(
    join(FIXTURES_DIR, "valid-guideline.md"),
    join(dest, "guidelines/testing/test-pyramid.md")
  );
  copyFileSync(
    join(FIXTURES_DIR, "valid-recipe.md"),
    join(dest, "recipes/infrastructure/logging.md")
  );

  const complianceFiles = [
    "principle-formatting.md",
    "guideline-formatting.md",
    "recipe-formatting.md",
  ];
  for (const f of complianceFiles) {
    const src = join(root, "compliance/artifact-formatting", f);
    if (existsSync(src)) {
      copyFileSync(src, join(dest, "compliance/artifact-formatting", f));
    }
  }

  for (const f of ["conventions.md", "glossary.md"]) {
    const src = join(root, "introduction", f);
    if (existsSync(src)) {
      copyFileSync(src, join(dest, "introduction", f));
    }
  }

  writeFileSync(
    join(dest, "index.md"),
    `# Index\n\n## Principles\n\n- [Simplicity](principles/simplicity.md)\n\n## Guidelines\n\n- [Test Pyramid](guidelines/testing/test-pyramid.md)\n\n## Recipes\n\n- [Logging](recipes/infrastructure/logging.md)\n`
  );

  writeFileSync(
    join(dest, "README.md"),
    `# Test Cookbook\n\n### Principles (1 files)\n\n### Guidelines (1 files)\n\n### Recipes (1 files)\n`
  );

  writeFileSync(
    join(dest, ".claude/CLAUDE.md"),
    `# Test Cookbook\n\n| Type | Count |\n|------|-------|\n| Principle | 1 |\n| Guideline | 1 |\n| Recipe | 1 |\n`
  );

  mkdirSync(join(dest, ".git"));
  writeFileSync(
    join(dest, ".git/config"),
    `[core]\n\trepositoryformatversion = 0\n`
  );
  writeFileSync(join(dest, ".git/HEAD"), "ref: refs/heads/main\n");

  return dest;
}

export function createTestWebsite(name: string): string {
  const dest = mkdtempSync(join(tmpdir(), `agenticcookbookweb-test-${name}-`));
  mkdirSync(join(dest, "cookbook"), { recursive: true });
  return dest;
}

export function copyFixture(
  fixtureName: string,
  destDir: string,
  destPath: string
): void {
  const src = join(FIXTURES_DIR, fixtureName);
  const dest = join(destDir, destPath);
  mkdirSync(join(dest, ".."), { recursive: true });
  copyFileSync(src, dest);
}

export function cleanup(dir: string | undefined): void {
  if (dir && dir.startsWith(tmpdir())) {
    rmSync(dir, { recursive: true, force: true });
  }
}
