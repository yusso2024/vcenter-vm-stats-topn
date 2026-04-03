#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import ssl
from pathlib import Path

import yaml
from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    required = ["vcenter_host", "vcenter_user", "vcenter_password"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError(f"Missing required config values: {', '.join(missing)}")
    return data


def connect(config: dict):
    context = None
    if config.get("insecure", False):
        context = ssl._create_unverified_context()
    port = int(config.get("vcenter_port", 443))
    return SmartConnect(
        host=config["vcenter_host"],
        user=config["vcenter_user"],
        pwd=config["vcenter_password"],
        port=port,
        sslContext=context,
    )


def all_vms(si) -> list:
    content = si.RetrieveContent()
    view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vms = list(view.view)
    view.Destroy()
    return vms


def vm_stats(vm: vim.VirtualMachine) -> dict:
    summary = vm.summary
    quick = summary.quickStats if summary else None
    committed = summary.storage.committed if summary and summary.storage else 0
    return {
        "cpu_usage": int(getattr(quick, "overallCpuUsage", 0) or 0),
        "memory_usage": int(getattr(quick, "guestMemoryUsage", 0) or 0),
        "storage_usage": round((committed or 0) / (1024 ** 3), 2),
    }


def collect(config_path: Path, output_path: Path) -> int:
    config = load_config(config_path)
    si = connect(config)
    try:
        stats = {vm.name: vm_stats(vm) for vm in all_vms(si)}
    finally:
        Disconnect(si)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)
    return len(stats)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch vCenter VM stats to JSON")
    parser.add_argument("--config", required=True, help="Path to YAML config with vCenter credentials")
    parser.add_argument("--output", default="data/vm_stats.json", help="Output JSON file")
    args = parser.parse_args()

    count = collect(Path(args.config), Path(args.output))
    print(f"Collected stats for {count} VMs -> {args.output}")


if __name__ == "__main__":
    main()
