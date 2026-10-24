#!/usr/bin/env python3
"""
Runs inside the GitHub Actions runner. Talks to the woozle-trap honeypot
pilot backend, then writes the returned decoy file into the build
workspace.

Vendored from AndyShortt/woozle-trap's action/register_and_inject.py --
woozle-trap is a private repo on a personal account, so it can't be
referenced as a remote Action (`uses: AndyShortt/woozle-trap/action@main`)
from a different repo; there's no org-level setting to share it cross-repo
on a personal account. Keep this in sync with the source if it changes.

Deliberately dependency-free (urllib only) so no `pip install` step is
needed -- ubuntu-latest ships python3 with a usable stdlib.

Never commits anything: this runs after checkout, writes one file into the
workspace, and appends that path to .git/info/exclude (a local-only
ignore, not committed) as a defensive backstop against a later step in the
same workflow doing something like `git add -A`.

Never prints decoy file content or the raw response body -- only
non-sensitive metadata (registrationId, decoyPath). Registers the real
credential values for GitHub Actions log masking as an extra safety net.
"""
import json
import os
import sys
import urllib.error
import urllib.request


def _mask(value):
    # GitHub Actions recognizes this exact workflow-command syntax on stdout.
    if value:
        print(f"::add-mask::{value}")


def main():
    backend_url = os.environ["BACKEND_URL"].rstrip("/")
    api_key = os.environ["BACKEND_API_KEY"]
    path_prefix = os.environ.get("PATH_PREFIX", "")
    repo = os.environ["GITHUB_REPOSITORY"]
    workflow_run_id = os.environ.get("GITHUB_RUN_ID", "")
    commit_sha = os.environ.get("GITHUB_SHA", "")
    workspace = os.environ["GITHUB_WORKSPACE"]

    marker_files = []
    try:
        for entry in os.listdir(workspace):
            full = os.path.join(workspace, entry)
            if os.path.isfile(full):
                marker_files.append(entry)
        # One level deep too (covers e.g. src/requirements.txt layouts)
        # without walking the whole tree.
        for entry in os.listdir(workspace):
            full = os.path.join(workspace, entry)
            if os.path.isdir(full) and not entry.startswith("."):
                try:
                    for sub in os.listdir(full):
                        if os.path.isfile(os.path.join(full, sub)):
                            marker_files.append(sub)
                except OSError:
                    continue
    except OSError as e:
        print(f"::warning::could not list workspace for ecosystem detection: {e}")

    marker_files = sorted(set(marker_files))[:200]

    payload = json.dumps(
        {
            "repo": repo,
            "workflowRunId": str(workflow_run_id),
            "commitSha": commit_sha,
            "markerFiles": marker_files,
            "pathPrefix": path_prefix,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{backend_url}/register",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json", "x-api-key": api_key},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        print(f"::warning::honeypot registration failed ({e.code}); continuing build without a decoy. {detail[:300]}")
        return
    except urllib.error.URLError as e:
        print(f"::warning::honeypot registration unreachable; continuing build without a decoy. {e}")
        return

    for token in body.get("maskTokens", []):
        _mask(token)

    decoy_path = body["decoyPath"]
    decoy_content = body["decoyContent"]
    target = os.path.join(workspace, decoy_path)

    if os.path.exists(target):
        print(f"::warning::decoy target {decoy_path} already exists in the workspace; skipping to avoid overwriting a real file")
        return

    os.makedirs(os.path.dirname(target) or workspace, exist_ok=True)
    with open(target, "w") as f:
        f.write(decoy_content)

    exclude_path = os.path.join(workspace, ".git", "info", "exclude")
    try:
        os.makedirs(os.path.dirname(exclude_path), exist_ok=True)
        with open(exclude_path, "a") as f:
            f.write(f"\n# honeypot-pilot: build-time decoy, never commit\n{decoy_path}\n")
    except OSError as e:
        print(f"::warning::could not update .git/info/exclude for decoy path: {e}")

    print(f"honeypot decoy placed (registrationId={body['registrationId']}, path={decoy_path})")


if __name__ == "__main__":
    main()
