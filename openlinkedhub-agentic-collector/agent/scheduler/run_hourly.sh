#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date '+%Y%m%dT%H').log"
LOCK_FILE="$LOG_DIR/collector.lock"

cleanup_logs() {
  find "$LOG_DIR" -type f -name '*.log' -mtime +7 -delete || true
}

cleanup_logs

{
  flock -n 9 || exit 0
  source "$ROOT_DIR/.env" 2>/dev/null || true
  echo "[$(date --iso-8601=seconds)] Starting hourly collection" | tee -a "$LOG_FILE"
  python -m agent.orchestrator >>"$LOG_FILE" 2>&1
  echo "[$(date --iso-8601=seconds)] Finished run" | tee -a "$LOG_FILE"
} 9>"$LOCK_FILE"
