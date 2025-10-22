"""High level orchestrator for the OpenLinkedHub collectors."""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from agent.utils import logging as logging_utils

LOGGER = logging.getLogger(__name__)


@dataclass
class CollectorJob:
    """Description of a single collector invocation."""

    spider: str
    name: str
    parameters: Dict[str, str]


@dataclass
class RunReport:
    """Run summary persisted after the orchestrator finishes."""

    started_at: datetime
    finished_at: datetime | None
    jobs: List[Dict[str, object]]
    errors: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "jobs": self.jobs,
            "errors": self.errors,
        }


class Orchestrator:
    """Orchestrates Scrapy spiders for each configured source and tag."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir or Path(__file__).resolve().parents[1])
        self.config_dir = self.base_dir / "agent" / "config"
        self.exports_dir = self.base_dir / "exports" / "_meta"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.tags = self._load_yaml("tags.yaml").get("tags", [])
        self.ckan_sources = self._load_yaml("sources.ckan.yaml").get("portals", [])
        self.mic_sources = self._load_yaml("sources.mic.yaml")
        self.worldbank_sources = self._load_yaml("sources.worldbank.yaml").get("tags", {})

    def _load_yaml(self, name: str) -> Dict[str, object]:
        path = self.config_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Configuration file missing: {path}")
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def plan_jobs(self, only: Optional[str] = None) -> List[CollectorJob]:
        filters = {only} if only else None
        jobs: List[CollectorJob] = []
        if not filters or "ckan" in filters:
            for portal in self.ckan_sources:
                base = portal.get("base")
                if not base:
                    continue
                for tag in self.tags:
                    jobs.append(
                        CollectorJob(
                            spider="ckan_portal",
                            name=f"ckan:{base}:{tag}",
                            parameters={"base_url": base, "tag": tag},
                        )
                    )
        if not filters or "mic" in filters:
            mic_listings: Iterable[str] = self.mic_sources.get("listing_urls", [])
            for listing in mic_listings:
                for tag in self.tags:
                    jobs.append(
                        CollectorJob(
                            spider="mic_portal",
                            name=f"mic:{tag}",
                            parameters={"listing_url": listing, "tag": tag},
                        )
                    )
        if not filters or "worldbank" in filters:
            for tag, indicators in self.worldbank_sources.items():
                jobs.append(
                    CollectorJob(
                        spider="worldbank",
                        name=f"worldbank:{tag}",
                        parameters={"tag": tag, "indicators": ",".join(indicators)},
                    )
                )
        return jobs

    def _run_spider(self, job: CollectorJob) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env.setdefault("SCRAPY_SETTINGS_MODULE", "collector.settings")
        cmd = ["scrapy", "crawl", job.spider]
        for key, value in job.parameters.items():
            cmd.extend(["-a", f"{key}={value}"])
        LOGGER.info("Running spider %s", job)
        return subprocess.run(
            cmd,
            cwd=str(self.base_dir / "collectors"),
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )

    def run(self, only: Optional[str] = None) -> RunReport:
        started = datetime.utcnow()
        report = RunReport(started_at=started, finished_at=None, jobs=[], errors=[])
        for job in self.plan_jobs(only=only):
            try:
                for attempt in Retrying(
                    wait=wait_exponential(multiplier=1, min=2, max=30),
                    stop=stop_after_attempt(3),
                    retry=retry_if_exception_type(subprocess.CalledProcessError),
                    reraise=True,
                ):
                    with attempt:
                        completed = self._run_spider(job)
                        report.jobs.append(
                            {
                                "job": job.name,
                                "attempt": attempt.retry_state.attempt_number,
                                "stdout": completed.stdout[-2000:],
                                "stderr": completed.stderr[-2000:],
                            }
                        )
                        break
            except subprocess.CalledProcessError as exc:  # pragma: no cover
                LOGGER.exception("Spider %s failed", job.name)
                report.errors.append(f"{job.name}: {exc}")
        report.finished_at = datetime.utcnow()
        meta_path = self.exports_dir / f"run_{started.strftime('%Y%m%dT%H%M%S')}.json"
        with meta_path.open("w", encoding="utf-8") as handle:
            json.dump(report.to_dict(), handle, ensure_ascii=False, indent=2)
        return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run OpenLinkedHub collectors")
    parser.add_argument("--only", choices=["ckan", "mic", "worldbank"], help="Run only a specific collector", default=None)
    args = parser.parse_args(argv)
    logging_utils.configure()
    orchestrator = Orchestrator()
    orchestrator.run(only=args.only)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
