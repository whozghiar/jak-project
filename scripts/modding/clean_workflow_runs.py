#!/usr/bin/env python3
"""
Utility script to clean up GitHub Actions workflow runs history for whozghiar/jak-project.
Authenticates automatically via Windows Credential Manager or GITHUB_TOKEN environment variable.
"""

import ctypes
from ctypes import wintypes
import json
import os
import sys
import time
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = "whozghiar/jak-project"


def get_token() -> str:
  token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
  if token:
    return token.strip()

  if sys.platform == "win32":
    try:
      advapi32 = ctypes.windll.advapi32

      class CREDENTIAL(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

      pcred = ctypes.POINTER(CREDENTIAL)()
      res = advapi32.CredReadW("git:https://github.com", 1, 0, ctypes.byref(pcred))
      if res:
        cred = pcred.contents
        blob = bytes(cred.CredentialBlob[: cred.CredentialBlobSize])
        token = blob.decode(
            "utf-16le"
            if blob.startswith(b"\xff\xfe") or b"\x00" in blob
            else "utf-8"
        ).strip()
        advapi32.CredFree(pcred)
        return token
    except Exception as err:
      print(f"Warning: Could not read Windows Credential Manager: {err}")

  return ""


def make_request(url: str, token: str, method: str = "GET") -> dict:
  req = urllib.request.Request(
      url,
      method=method,
      headers={
          "Authorization": f"Bearer {token}",
          "Accept": "application/vnd.github+json",
          "User-Agent": "OpenGOAL-Modding-Cleanup",
      },
  )
  with urllib.request.urlopen(req) as resp:
    if method == "DELETE":
      return {"status": resp.status}
    body = resp.read().decode("utf-8")
    return json.loads(body) if body else {}


def delete_all_workflow_runs():
  token = get_token()
  if not token:
    print("Error: GitHub authentication token not found.", file=sys.stderr)
    sys.exit(1)

  print(f"🔍 Fetching workflow runs for {REPO}...")

  total_deleted = 0
  while True:
    try:
      data = make_request(
          f"https://api.github.com/repos/{REPO}/actions/runs?per_page=100",
          token,
      )
      runs = data.get("workflow_runs", [])
      total_count = data.get("total_count", 0)

      if not runs:
        print(f"\n✅ All workflow runs cleaned! (Total deleted: {total_deleted})")
        break

      print(f"Found {len(runs)} workflow run(s) to delete (total remaining on server: {total_count})...")

      for run in runs:
        run_id = run.get("id")
        run_name = run.get("name") or "Workflow"
        conclusion = run.get("conclusion") or run.get("status")

        del_url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}"
        try:
          make_request(del_url, token, method="DELETE")
          total_deleted += 1
          print(f"  🗑️ [{total_deleted}] Deleted run {run_id} ({run_name} - {conclusion})")
        except urllib.error.HTTPError as err:
          print(f"  ❌ Failed to delete run {run_id}: {err}")

        # Slight pause to avoid GitHub API rate-limits
        time.sleep(0.2)

    except Exception as err:
      print(f"Error fetching runs: {err}", file=sys.stderr)
      break


if __name__ == "__main__":
  delete_all_workflow_runs()
