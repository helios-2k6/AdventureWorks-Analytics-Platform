from src.app.pipeline_runner import PipelineRunner


class _Health:
    def __init__(self, status="ok"):
        self.status = status
        self.called = False

    def check_all(self):
        self.called = True
        return {"status": self.status}


class _Bootstrap:
    def __init__(self, status="ok"):
        self.status = status
        self.called = False

    def run(self):
        self.called = True
        return {"status": self.status}


class _Stage:
    def __init__(self, status="SUCCESS"):
        self.status = status
        self.called = False

    def run(self, mode="full"):
        self.called = True
        return {"status": self.status, "bronze": {}, "silver": {}}


def test_runner_success_keeps_gold_registered_but_not_requested():
    health = _Health()
    bootstrap = _Bootstrap()
    stage = _Stage()
    runner = PipelineRunner(health, bootstrap, stage)

    result = runner.run()

    assert result["status"] == "SUCCESS"
    assert result["requested_stages"] == ["bronze", "silver"]
    assert result["gold"]["status"] == "NOT_REQUESTED"
    assert result["failed_stage"] is None
    assert result["duration_ms"] >= 0


def test_runner_health_failure_stops_before_bootstrap_and_data():
    health = _Health("degraded")
    bootstrap = _Bootstrap()
    stage = _Stage()
    result = PipelineRunner(health, bootstrap, stage).run()

    assert result["status"] == "FAILED"
    assert result["failed_stage"] == "health"
    assert bootstrap.called is False
    assert stage.called is False


def test_runner_bootstrap_failure_stops_before_data():
    health = _Health()
    bootstrap = _Bootstrap("failed")
    stage = _Stage()
    result = PipelineRunner(health, bootstrap, stage).run()

    assert result["status"] == "FAILED"
    assert result["failed_stage"] == "bootstrap"
    assert stage.called is False


def test_runner_stage_failure_records_silver_failure():
    stage = _Stage("FAILED")
    result = PipelineRunner(_Health(), _Bootstrap(), stage).run()

    assert result["status"] == "FAILED"
    assert result["failed_stage"] == "silver"
    assert result["gold"]["status"] == "NOT_REQUESTED"
