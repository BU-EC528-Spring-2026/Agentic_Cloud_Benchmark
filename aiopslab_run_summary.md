# AIOpsLab Local Setup and Trial Runs (Windows + kind)

## Environment

- OS: Windows
- Kubernetes: `kind` local cluster (`kind-kind`)
- Python: 3.11 (via Poetry)
- Helm: `v3.19.2`
- kind: `0.30.0`

## What was completed

1. Installed project dependencies with Poetry (`python >=3.11,<3.13`)
2. Created local kind cluster using `kind/kind-config-x86.yaml`
3. Configured `aiopslab/config.yml` for local kind use (`k8s_host: kind`)
4. Created `.env` and tested both:
   - Human agent flow (`cli.py`)
   - GPT baseline flow (`clients/gpt.py`)

## Trial Run 1 (Human agent)

- Problem: `misconfig_app_hotel_res-detection-1`
- Result: `Correct detection: Yes`
- Submission: `submit("Yes")`

Notes:
- Fault injected into service `geo`
- End-to-end deployment + fault injection + evaluation worked on local machine

## Trial Run 2 (GPT baseline, single problem test)

- Problem: `misconfig_app_hotel_res-detection-1`
- Result: `Correct detection: Yes`
- Example agent actions:
  - `kubectl get pods -n test-hotel-reservation`
  - `kubectl describe pod geo-... -n test-hotel-reservation`
  - `submit("Yes")`

Metrics from run (example):
- `TTD`: ~11.25s
- `steps`: 8

## Trial Run 3 (GPT baseline, full-run started)

- Additional scenarios started successfully (e.g., social-network namespace)
- Framework deployed workloads, injected faults, and evaluated submissions
- One scenario showed a wrong classification by the baseline model (expected baseline limitation)
- Run was interrupted by OpenAI API rate limit (`429 TPM limit`)

## Trial Run 4 (GPT baseline, targeted multi-scenario run)

Command used:

```powershell
cd C:\Projects\AIOpsLab
$env:PATH = "$PWD\tools\bin;$env:PATH"
C:\Users\TBtb0\AppData\Local\Programs\Python\Python311\python.exe -m poetry run python clients\gpt.py `
  --problem-id misconfig_app_hotel_res-detection-1 `
  --problem-id scale_pod_zero_social_net-detection-1 `
  --max-steps 20
```

### Scenario A

- Problem: `misconfig_app_hotel_res-detection-1`
- Result: `Correct detection: Yes`
- Observed evidence:
  - `geo` pod entered `Error`
  - `geo` logs showed DB misconfiguration / connection failure (`mongodb-geo:27777`, `no reachable servers`)
- Example metrics:
  - `TTD`: ~6.01s
  - `steps`: 7

### Scenario B

- Problem: `scale_pod_zero_social_net-detection-1`
- Result: `Correct detection: Yes`
- Fault injected: scaled `user-service` deployment to `0` replicas
- Observed evidence:
  - upstream service logs showed `user-service:9090` connection refused
  - `kubectl describe svc user-service` showed empty `Endpoints`
- Example metrics:
  - `TTD`: ~6.26s
  - `steps`: 7

Summary:
- Targeted GPT run completed **2/2 detection scenarios successfully** on local `kind` cluster.

## Local fixes made for Windows compatibility

1. `aiopslab/service/apps/hotelres.py`
   - Replaced Linux-only cleanup pipeline (`grep | awk`) with Python parsing of `kubectl get pv` output
   - Prevents noisy Windows cleanup errors during fault recovery

2. `clients/gpt.py`
   - Temporarily switched to single-problem mode for validation, then restored full-problem iteration
   - Added CLI args for targeted runs: `--problem-id` (repeatable), `--max-steps`, `--list-problems`

## How to run (commands used)

```powershell
cd C:\Projects\AIOpsLab
$env:PATH = "$PWD\tools\bin;$env:PATH"
C:\Users\TBtb0\AppData\Local\Programs\Python\Python311\python.exe -m poetry run python cli.py
```

```powershell
cd C:\Projects\AIOpsLab
$env:PATH = "$PWD\tools\bin;$env:PATH"
C:\Users\TBtb0\AppData\Local\Programs\Python\Python311\python.exe -m poetry run python clients\gpt.py
```

```powershell
# Targeted run (recommended for demos / screenshots)
cd C:\Projects\AIOpsLab
$env:PATH = "$PWD\tools\bin;$env:PATH"
C:\Users\TBtb0\AppData\Local\Programs\Python\Python311\python.exe -m poetry run python clients\gpt.py `
  --problem-id misconfig_app_hotel_res-detection-1 `
  --problem-id scale_pod_zero_social_net-detection-1 `
  --max-steps 20
```