from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import uuid4


class PipelineRunner:
    """Coordinate platform gates and enabled data stages.

    Gold is registered as a future stage but remains NOT_REQUESTED until its
    implementation and publication contract are enabled.
    """

    def __init__(
        self,
        health_service: Any,
        bootstrap_job: Any,
        bronze_to_silver_pipeline: Any,
        gold_pipeline: Any | None = None,
        clock=perf_counter,
    ):
        self.health_service = health_service
        self.bootstrap_job = bootstrap_job
        self.bronze_to_silver_pipeline = bronze_to_silver_pipeline
        self.gold_pipeline = gold_pipeline
        self.clock = clock

    def run(self, mode: str = "full") -> dict[str, object]:
        started_at = datetime.now(timezone.utc)
        started_clock = self.clock()
        run_id = str(uuid4())
        requested_stages = ["bronze", "silver"]
        health = self.health_service.check_all()
        if health.get("status") != "ok":
            return self._result(
                run_id, mode, requested_stages, started_at, started_clock,
                health=health, bootstrap=None, pipeline=None,
                failed_stage="health",
            )

        bootstrap = self.bootstrap_job.run()
        if bootstrap.get("status") != "ok":
            return self._result(
                run_id, mode, requested_stages, started_at, started_clock,
                health=health, bootstrap=bootstrap, pipeline=None,
                failed_stage="bootstrap",
            )

        pipeline = self.bronze_to_silver_pipeline.run(mode=mode)
        if pipeline.get("status") != "SUCCESS":
            return self._result(
                run_id, mode, requested_stages, started_at, started_clock,
                health=health, bootstrap=bootstrap, pipeline=pipeline,
                failed_stage="silver",
            )

        return self._result(
            run_id, mode, requested_stages, started_at, started_clock,
            health=health, bootstrap=bootstrap, pipeline=pipeline,
            failed_stage=None,
        )

    def _result(
        self,
        run_id,
        mode,
        requested_stages,
        started_at,
        started_clock,
        *,
        health,
        bootstrap,
        pipeline,
        failed_stage,
    ) -> dict[str, object]:
        finished_at = datetime.now(timezone.utc)
        pipeline = pipeline or {}
        status = "SUCCESS" if failed_stage is None else "FAILED"
        return {
            "run_id": run_id,
            "pipeline_name": "adventureworks",
            "mode": mode,
            "requested_stages": requested_stages,
            "status": status,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "duration_ms": max(0, int((self.clock() - started_clock) * 1000)),
            "failed_stage": failed_stage,
            "health": health,
            "bootstrap": bootstrap,
            "bronze": pipeline.get("bronze"),
            "bronze_gate": pipeline.get("bronze_gate"),
            "snapshot_id": pipeline.get("snapshot_id"),
            "silver": pipeline.get("silver"),
            "gold": {"status": "NOT_REQUESTED"},
            "report_paths": [],
        }
