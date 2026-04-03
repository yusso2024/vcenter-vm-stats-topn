# vCenter VM Stats Top-N

Collect VM statistics from vCenter and generate Top-N graphics by metric.

## What this repo does

- Fetches read-only VM stats from vCenter:
  - `cpu_usage` (MHz)
  - `memory_usage` (MB)
  - `storage_usage` (GB committed)
- Saves all stats to JSON
- Generates configurable Top-N bar chart graphics

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Config

Create `config.yaml` from sample:

```bash
cp config.yaml.sample config.yaml
```

Edit values:

- `vcenter_host`
- `vcenter_user`
- `vcenter_password`
- optional: `vcenter_port`, `insecure`

## 1) Fetch statistics

```bash
python fetch_vm_stats.py --config config.yaml --output data/vm_stats.json
```

## 2) Generate Top-N graphic

```bash
python top_n_graphic.py \
  --stats data/vm_stats.json \
  --metric cpu_usage \
  --top-n 15 \
  --output graphics/top15_cpu.png
```

### Parameters

- `--metric`: `cpu_usage`, `memory_usage`, `storage_usage`
- `--top-n`: number of VMs to include
- `--prefix`: optional VM name prefix filter (example: `FL`)
- `--title`: optional custom chart title
- `--output`: output PNG path

Examples:

```bash
python top_n_graphic.py --stats data/vm_stats.json --metric memory_usage --top-n 10 --output graphics/top10_memory.png
python top_n_graphic.py --stats data/vm_stats.json --metric storage_usage --top-n 20 --prefix FL --output graphics/top20_storage_fl.png
```

## Notes

- This workflow is read-only for metrics collection.
- VM create/delete/power operations are not used by these scripts.

## License

MIT
