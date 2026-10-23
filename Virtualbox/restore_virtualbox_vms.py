#!/usr/bin/env python3

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path("/media/nimaathari/APPS/VMs/Arvan")

MACHINES = {
    "71165adf-9590-42a9-996c-06687a86c532":
        "Projects/Bash Script/Debian13-BashScript_Hello/Debian13-BashScript_Hello.vbox",

    "92e633f8-a1fa-47aa-b405-7aff38c41095":
        "Projects/WEB/Debian13-StaticWebAndFileServer/Debian13-StaticWebAndFileServer.vbox",

    "1ec2ed64-e893-49a1-bd1c-63d0ebaf903e":
        "Projects/WEB/Debian13-Wordpress_Nginx/Debian13-Wordpress_Nginx.vbox",

    "4d11fbe4-6cef-49fe-b6de-0e6cb70a6ee8":
        "Projects/Monitoring/ELK/Debian12-ELK/Debian12-ELK.vbox",

    "e1e380c6-1f9c-4b34-9cee-995c074f859f":
        "Projects/OLD/promotheuse011/promotheuse011.vbox",

    "bc6e89e9-6c05-43d8-86e3-92a5e793b634":
        "Projects/Monitoring/Promotheuse/Debian12-Promotheuse/Debian12-Promotheuse.vbox",

    "0b793532-dd0b-4327-8666-f0db07383f74":
        "Projects/Begginer_Vargrant/vagrant0211 Clone/vagrant0211 Clone.vbox",
}


def run(*args):
    return subprocess.run(
        args,
        capture_output=True,
        text=True
    )


def get_uuid(path):
    root = ET.parse(path).getroot()

    machine = next(
        element for element in root.iter()
        if element.tag.split("}")[-1] == "Machine"
    )

    return machine.attrib["uuid"].strip("{}").lower()


print("========== PREFLIGHT ==========", flush=True)

registered = run("VBoxManage", "list", "vms")
if registered.returncode != 0:
    sys.exit(registered.stderr)

# Validate every file before making any changes.
for uuid, relative_path in MACHINES.items():
    path = BASE / relative_path

    if not path.is_file():
        sys.exit(f"Missing configuration: {path}")

    actual_uuid = get_uuid(path)

    if actual_uuid != uuid:
        sys.exit(
            f"UUID mismatch:\n"
            f"File: {path}\n"
            f"Expected: {uuid}\n"
            f"Actual: {actual_uuid}"
        )

    if f'"<inaccessible>" {{{uuid}}}' not in registered.stdout:
        sys.exit(
            f"VM is not registered as inaccessible: {uuid}\n"
            "No changes made."
        )

    print(f"VALID: {uuid} -> {path}", flush=True)

print("\n========== RESTORE ==========", flush=True)

for uuid, relative_path in MACHINES.items():
    path = BASE / relative_path

    print(f"\nRestoring: {path.name}", flush=True)

    remove = run(
        "VBoxManage",
        "unregistervm",
        uuid
    )

    if remove.returncode != 0:
        sys.exit(
            f"Unregister failed: {uuid}\n{remove.stderr}"
        )

    restore = run(
        "VBoxManage",
        "registervm",
        str(path)
    )

    if restore.returncode != 0:
        sys.exit(
            f"Register failed: {uuid}\n"
            f"{restore.stderr}\n"
            f"Configuration remains at: {path}\n"
            "Stopped to prevent further changes."
        )

    verify = run(
        "VBoxManage",
        "showvminfo",
        uuid,
        "--machinereadable"
    )

    if verify.returncode != 0:
        sys.exit(
            f"Verification failed: {uuid}\n{verify.stderr}"
        )

    print(f"RESTORED: {uuid}", flush=True)

print("\nAll 7 machines restored successfully.", flush=True)
