/**
 * Consulting-team file validation — verifies every file in consulting-teams/
 * has valid frontmatter and required sections.
 */

import { describe, it, expect } from "vitest";
import { readdirSync, readFileSync, statSync, existsSync } from "fs";
import { join, basename } from "path";

const REPO_ROOT = join(__dirname, "../../../..");
const PLUGIN_ROOT = join(REPO_ROOT, "plugins", "dev-team");
const CONSULTING_TEAMS_DIR = join(PLUGIN_ROOT, "consulting-teams");

// Collect all consulting-team files
function getAllConsultingTeamFiles(): {
  category: string;
  name: string;
  path: string;
}[] {
  const files: { category: string; name: string; path: string }[] = [];
  if (!existsSync(CONSULTING_TEAMS_DIR)) return files;

  for (const category of readdirSync(CONSULTING_TEAMS_DIR)) {
    const categoryPath = join(CONSULTING_TEAMS_DIR, category);
    if (!statSync(categoryPath).isDirectory()) continue;

    for (const file of readdirSync(categoryPath)) {
      if (!file.endsWith(".md")) continue;
      files.push({
        category,
        name: basename(file, ".md"),
        path: join(categoryPath, file),
      });
    }
  }
  return files;
}

// Parse frontmatter from a markdown file, handling YAML lists for source field
function parseFrontmatter(content: string): {
  fields: Record<string, string | string[]>;
  body: string;
} | null {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return null;

  const fields: Record<string, string | string[]> = {};
  const lines = match[1].split("\n");

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const colonIdx = line.indexOf(":");
    if (colonIdx === -1) continue;
    const key = line.slice(0, colonIdx).trim();
    const value = line.slice(colonIdx + 1).trim();

    // Check if the value is empty and subsequent lines are list items
    if (value === "") {
      const listItems: string[] = [];
      while (i + 1 < lines.length && lines[i + 1].startsWith("  - ")) {
        i++;
        listItems.push(lines[i].slice(4).trim());
      }
      if (listItems.length > 0) {
        fields[key] = listItems;
        continue;
      }
    }

    fields[key] = value;
  }

  return { fields, body: match[2] };
}

const consultingTeamFiles = getAllConsultingTeamFiles();

describe("consulting-teams directory structure", () => {
  it("consulting-teams directory exists", () => {
    expect(existsSync(CONSULTING_TEAMS_DIR)).toBe(true);
  });

  it("has at least one consulting-team file", () => {
    expect(consultingTeamFiles.length).toBeGreaterThan(0);
  });
});

describe.each(consultingTeamFiles)(
  "consulting-teams/$category/$name",
  ({ name, path }) => {
    const content = readFileSync(path, "utf-8");
    const parsed = parseFrontmatter(content);

    it("has valid frontmatter", () => {
      expect(parsed, "Missing or malformed frontmatter").not.toBeNull();
    });

    it("has required frontmatter fields (name, description, type, source, version)", () => {
      expect(parsed!.fields).toHaveProperty("name");
      expect(parsed!.fields).toHaveProperty("description");
      expect(parsed!.fields).toHaveProperty("type");
      expect(parsed!.fields).toHaveProperty("source");
      expect(parsed!.fields).toHaveProperty("version");
    });

    it('type is "consulting"', () => {
      expect(parsed!.fields.type).toBe("consulting");
    });

    it("name matches filename", () => {
      expect(parsed!.fields.name).toBe(name);
    });

    it("name is kebab-case", () => {
      expect(name).toMatch(/^[a-z][a-z0-9]*(-[a-z0-9]+)*$/);
    });

    it("source is a non-empty list", () => {
      const source = parsed!.fields.source;
      expect(Array.isArray(source)).toBe(true);
      expect((source as string[]).length).toBeGreaterThan(0);
    });

    it("version is semver", () => {
      expect(parsed!.fields.version).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it("description is non-empty", () => {
      const description = parsed!.fields.description;
      expect(typeof description).toBe("string");
      expect((description as string).length).toBeGreaterThan(0);
    });

    it("has Consulting Focus section", () => {
      expect(parsed!.body).toContain("## Consulting Focus");
    });

    it("has Verify section", () => {
      expect(parsed!.body).toContain("## Verify");
    });

    it("Consulting Focus section is non-empty", () => {
      const match = parsed!.body.match(
        /## Consulting Focus\n([\s\S]*?)(?=\n## |\n*$)/
      );
      expect(match, "Consulting Focus section not found").not.toBeNull();
      expect(match![1].trim().length).toBeGreaterThan(0);
    });

    it("Verify section is non-empty", () => {
      const match = parsed!.body.match(
        /## Verify\n([\s\S]*?)(?=\n## |\n*$)/
      );
      expect(match, "Verify section not found").not.toBeNull();
      expect(match![1].trim().length).toBeGreaterThan(0);
    });
  }
);
