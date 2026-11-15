import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("updater", ROOT / "scripts/update-gitops-images.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class ImageUpdates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ticketops-image-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "manifests").mkdir()

    def fixtures(self, references):
        for service, reference in zip(sorted(updater.SERVICES), references):
            (self.root / "manifests" / f"{service}.yaml").write_text(
                f"image: {reference.format(service=service)}\nversion: v1.6.3\n",
                encoding="utf-8",
            )

    def test_quotes_tags_digests_and_retries(self):
        prefix = updater.REGISTRY + "/ticketops-dev-{service}"
        self.fixtures([
            f'"{prefix}:__IMAGE_TAG__"',
            f"'{prefix}:v1.6.9' # preserve comment",
            prefix + "@sha256:" + "a" * 64,
            prefix + ":v1.6.9@sha256:" + "b" * 64,
        ])
        self.assertEqual(updater.update_images(self.root, "v1.0.0"), (4, 4))
        self.assertEqual(updater.update_images(self.root, "v1.0.1"), (4, 4))
        self.assertEqual(updater.update_images(self.root, "v1.0.1"), (0, 4))
        combined = "".join(p.read_text() for p in (self.root / "manifests").glob("*.yaml"))
        self.assertNotIn("__IMAGE_TAG__", combined)
        self.assertNotIn("sha256:", combined)
        self.assertEqual(combined.count("version: v1.0.1"), 4)
        self.assertIn("# preserve comment", combined)

    def test_missing_service_stops_before_writing(self):
        self.fixtures([updater.REGISTRY + "/ticketops-dev-{service}:__IMAGE_TAG__"])
        path = next((self.root / "manifests").glob("*.yaml"))
        before = path.read_text()
        with self.assertRaisesRegex(ValueError, "missing"):
            updater.update_images(self.root, "v1.0.0")
        self.assertEqual(path.read_text(), before)

    def test_other_registry_is_untouched(self):
        self.fixtures([updater.REGISTRY + "/ticketops-dev-{service}:v1.0.0"] * 4)
        path = self.root / "manifests" / "other.yaml"
        path.write_text("image: example.org/ticketops-dev-events-api:v7.0.0\n")
        updater.update_images(self.root, "v1.0.1")
        self.assertIn(":v7.0.0", path.read_text())

    def test_invalid_release_tag_is_rejected(self):
        for tag in ("latest", "v1.0.0; echo bad", "v1.0.0-beta.1"):
            with self.assertRaises(ValueError):
                updater.update_images(self.root, tag)

    @unittest.skipUnless(
        (ROOT.parent / "ticketops-gitops-config" / "manifests").is_dir(),
        "Local integration check needs the sibling private GitOps checkout",
    )
    def test_actual_gitops_tree_initial_update_and_next_release(self):
        source = ROOT.parent / "ticketops-gitops-config" / "manifests"
        shutil.copytree(source, self.root / "manifests", dirs_exist_ok=True)
        files, references = updater.update_images(self.root, "v1.0.0")
        self.assertEqual(references, 6)
        self.assertEqual(files, 6)
        self.assertEqual(updater.update_images(self.root, "v1.0.1"), (6, 6))
        self.assertEqual(updater.update_images(self.root, "v1.0.1"), (0, 6))


if __name__ == "__main__":
    unittest.main()
