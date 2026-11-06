import runpy
from pathlib import Path

GUNICORN_CONF = Path(__file__).resolve().parents[2] / "gunicorn.conf.py"


class TestGunicornConf:
    def _load(self):
        return runpy.run_path(str(GUNICORN_CONF))

    def test_defaults(self, monkeypatch):
        monkeypatch.delenv("GUNICORN_WORKERS", raising=False)
        monkeypatch.delenv("GUNICORN_THREADS", raising=False)
        conf = self._load()
        assert conf["worker_class"] == "gthread"
        assert conf["workers"] == 2
        assert conf["threads"] == 4
        assert conf["timeout"] == 90
        assert conf["preload_app"] is True

    def test_sizing_from_environment(self, monkeypatch):
        """ECS task definition sets per-environment sizing via env vars."""
        monkeypatch.setenv("GUNICORN_WORKERS", "3")
        monkeypatch.setenv("GUNICORN_THREADS", "8")
        conf = self._load()
        assert conf["workers"] == 3
        assert conf["threads"] == 8
