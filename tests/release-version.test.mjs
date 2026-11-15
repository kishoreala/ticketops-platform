import assert from "node:assert/strict";
import test from "node:test";
import { selectReleaseVersion } from "../scripts/release-version.mjs";

test("new release uses the published version", () => {
  assert.equal(selectReleaseVersion({ nextRelease: { version: "1.0.0" } }, ""), "v1.0.0");
});
test("rerun reuses a stable release tag already at HEAD", () => {
  assert.equal(selectReleaseVersion(false, "v1.2.3\r\n"), "v1.2.3");
});
test("non-release commit skips publishing", () => {
  assert.equal(selectReleaseVersion(false, ""), "");
});
test("unrelated and prerelease tags do not trigger stable publishing", () => {
  assert.equal(selectReleaseVersion(false, "backup\nv1.0.0-beta.1\n"), "");
});
test("ambiguous stable tags stop rather than publish the wrong version", () => {
  assert.throws(() => selectReleaseVersion(false, "v1.0.0\nv2.0.0"), /ambiguous/);
});
