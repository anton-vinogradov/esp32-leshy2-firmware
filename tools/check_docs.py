#!/usr/bin/env python3
"""Cross-reference checker for the Leshy2 docs.

Keeps the firmware and hardware READMEs from drifting apart: every markdown
link is resolved and a broken one fails the build. It catches the class of
bug that a section renumber creates — a link whose anchor no longer exists,
here or in the sibling repo.

Checks, all offline (the sibling repo is a local checkout in CI):
  * intra-file anchor links  `](#heading)`            -> heading exists here
  * local file links         `](path.md#heading)`     -> file + anchor exist
  * sibling-repo anchor links `](…/esp32-leshy2#x)`   -> anchor exists in the
                                                          sibling's README.md
  * sibling-repo path links   `](…/tree/main/foo)`     -> path exists there

Semantic drift (a capability list that disagrees) is not auto-diffed — that
stays a human reconcile, flagged by review. This tool guarantees the links
between the two source-of-truth docs never rot.

Usage:
    check_docs.py [--repo-root DIR] [--sibling-slug OWNER/REPO]
                  [--sibling-path DIR]
Exit code 1 if any reference is broken.
"""

import argparse
import os
import re
import sys

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def gh_anchor(text):
    """GitHub's heading -> anchor slug (Unicode-aware, matches README anchors)."""
    text = text.strip().lower()
    kept = [c for c in text if c.isalnum() or c in " -_"]
    return "".join(kept).replace(" ", "-")


def anchors_of(md_text):
    seen, out = {}, set()
    for line in md_text.splitlines():
        m = HEADING_RE.match(line)
        if not m:
            continue
        base = gh_anchor(m.group(2))
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.add(base if n == 0 else f"{base}-{n}")
    return out


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def md_files(root):
    for name in sorted(os.listdir(root)):
        if name.endswith(".md") and os.path.isfile(os.path.join(root, name)):
            yield os.path.join(root, name)
    docs = os.path.join(root, "docs")
    for dirpath, _, names in os.walk(docs):
        for name in sorted(names):
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--sibling-slug", default="anton-vinogradov/esp32-leshy2")
    ap.add_argument("--sibling-path", default=None,
                    help="local checkout of the sibling repo (enables its checks)")
    args = ap.parse_args()

    root = os.path.abspath(args.repo_root)
    anchor_cache = {}

    def file_anchors(path):
        if path not in anchor_cache:
            anchor_cache[path] = anchors_of(read(path)) if os.path.isfile(path) else None
        return anchor_cache[path]

    sibling_readme_anchors = None
    if args.sibling_path:
        sib_readme = os.path.join(args.sibling_path, "README.md")
        if os.path.isfile(sib_readme):
            sibling_readme_anchors = anchors_of(read(sib_readme))

    sibling_url = f"https://github.com/{args.sibling_slug}"
    errors = []

    for path in md_files(root):
        rel = os.path.relpath(path, root)
        own_anchors = file_anchors(path)
        for target in LINK_RE.findall(read(path)):
            # intra-file anchor
            if target.startswith("#"):
                if target[1:] not in own_anchors:
                    errors.append(f"{rel}: dead intra-file anchor {target}")
                continue
            # sibling repo link
            if target.startswith(sibling_url):
                tail = target[len(sibling_url):]
                if tail.startswith("/tree/") or tail.startswith("/blob/"):
                    sub = tail.split("#", 1)[0].split("/", 3)
                    subpath = sub[3] if len(sub) > 3 else ""
                    if args.sibling_path and subpath and not os.path.exists(
                            os.path.join(args.sibling_path, subpath)):
                        errors.append(f"{rel}: sibling path missing: {subpath}")
                elif "#" in tail:
                    frag = tail.split("#", 1)[1]
                    if sibling_readme_anchors is not None and frag not in sibling_readme_anchors:
                        errors.append(f"{rel}: dead sibling anchor #{frag}")
                continue
            # other external URL — out of scope
            if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                continue
            # local relative link
            filepart, _, frag = target.partition("#")
            dest = os.path.normpath(os.path.join(os.path.dirname(path), filepart))
            if not os.path.exists(dest):
                errors.append(f"{rel}: missing local file: {filepart}")
            elif frag and dest.endswith(".md"):
                da = file_anchors(dest)
                if da is not None and frag not in da:
                    errors.append(f"{rel}: dead anchor #{frag} in {filepart}")

    if errors:
        print("Doc cross-reference check FAILED:\n")
        for e in errors:
            print("  ✗ " + e)
        print(f"\n{len(errors)} broken reference(s).")
        return 1
    print("Doc cross-reference check passed.")
    if sibling_readme_anchors is None:
        print("  (sibling repo not provided — cross-repo anchors not verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
