import { appendFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import semanticRelease from "semantic-release";
import { selectReleaseVersion } from "./release-version.mjs";

if (!process.env.GITHUB_OUTPUT) {
  throw new Error("GITHUB_OUTPUT is required; run this script in GitHub Actions.");
}
// Use the API result instead of parsing human-readable CLI logs.
const result = await semanticRelease();
const version = selectReleaseVersion(
  result,
  result ? "" : execFileSync("git", ["tag", "--points-at", "HEAD"], { encoding: "utf8" }),
);
const published = Boolean(version);
if (!result && version) console.log(`Reusing ${version} at HEAD to retry image publishing.`);
appendFileSync(
  process.env.GITHUB_OUTPUT,
  `new_release_published=${published}\nnew_release_version=${version}\n`,
);
