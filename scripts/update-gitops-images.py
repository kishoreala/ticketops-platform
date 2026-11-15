"""Update only TicketOps image references and matching workload version labels."""
import argparse
from pathlib import Path
import re

REGISTRY = "238005915203.dkr.ecr.us-east-1.amazonaws.com"
SERVICES = {"events-api", "admin-api", "bookings-worker", "dashboard"}
IMAGE = re.compile(
    r"(?m)^(\s*image:\s*[\"']?)"
    + re.escape(REGISTRY)
    + r"/ticketops-dev-(events-api|admin-api|bookings-worker|dashboard)"
    + r"(?::[A-Za-z0-9_.-]+)?(?:@sha256:[a-fA-F0-9]{64})?"
    + r"(?=[\"']?\s*(?:#.*)?$)"
)


def update_images(root: Path, tag: str) -> tuple[int, int]:
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("Image tag must be a stable release such as v1.0.0")
    updates = []
    services = set()
    references = 0
    for path in sorted((root / "manifests").rglob("*.yaml")):
        old = path.read_text(encoding="utf-8")
        matches = list(IMAGE.finditer(old))
        if not matches:
            continue
        services.update(match.group(2) for match in matches)
        references += len(matches)
        new = IMAGE.sub(lambda match: f"{match.group(1)}{REGISTRY}/ticketops-dev-{match.group(2)}:{tag}", old)
        new = re.sub(r"(?m)^(\s*version:\s*)v\d+\.\d+\.\d+\s*$", lambda match: match.group(1) + tag, new)
        if new != old:
            updates.append((path, new))
    if services != SERVICES:
        raise ValueError(f"Expected images for all four services; missing {sorted(SERVICES - services)}")
    for path, content in updates:
        path.write_text(content, encoding="utf-8")
    return len(updates), references


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    try:
        files, images = update_images(args.root, args.tag)
    except ValueError as error:
        parser.error(str(error))
    print(f"Updated {files} files; found {images} TicketOps image references.")
