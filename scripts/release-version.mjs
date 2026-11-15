// A rerun may find that this commit's release was already published by the first
// attempt. Reuse that exact commit's version so unfinished image jobs can retry.
export function selectReleaseVersion(result, tagsAtHead) {
  if (result) return `v${result.nextRelease.version}`;
  const versions = tagsAtHead.split(/\r?\n/).filter((tag) => /^v\d+\.\d+\.\d+$/.test(tag));
  if (versions.length > 1) throw new Error("Multiple release tags point to HEAD; refusing an ambiguous retry.");
  return versions[0] || "";
}
