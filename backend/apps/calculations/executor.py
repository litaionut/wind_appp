"""Synchronous calculation executors."""

from __future__ import annotations

from django.utils import timezone

from apps.calculations.models import CalculationLog, CalculationRun, LogLevel, RunStatus


def execute_run(run: CalculationRun) -> CalculationRun:
    run.status = RunStatus.RUNNING
    run.started_at = timezone.now()
    run.save(update_fields=["status", "started_at"])
    CalculationLog.objects.create(
        run=run, level=LogLevel.INFO, message="Calculation started."
    )

    try:
        if run.method.method_id == "platform_stub" and run.method.version == "v1":
            label = run.parameters.get("label", "default")
            run.results = {
                "method": run.method.registry_key,
                "label": label,
                "message": f"Stub result for {label}",
                "value": 42,
                "unit": "1",
            }
            run.warnings = []
            run.errors = []
            run.status = RunStatus.SUCCEEDED
            CalculationLog.objects.create(
                run=run, level=LogLevel.INFO, message="Stub calculation completed."
            )
        else:
            run.status = RunStatus.FAILED
            run.errors = [f"No executor registered for {run.method.registry_key}."]
            CalculationLog.objects.create(
                run=run, level=LogLevel.ERROR, message=run.errors[0]
            )
    except Exception as exc:  # noqa: BLE001 — convert to failed run
        run.status = RunStatus.FAILED
        run.errors = [str(exc)]
        CalculationLog.objects.create(
            run=run, level=LogLevel.ERROR, message=str(exc)
        )

    run.completed_at = timezone.now()
    run.save(
        update_fields=[
            "status",
            "results",
            "warnings",
            "errors",
            "completed_at",
        ]
    )
    return run
