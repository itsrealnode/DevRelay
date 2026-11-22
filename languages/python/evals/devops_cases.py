import json
import os
import shutil
from pathlib import Path
from runpy import run_path
from tempfile import TemporaryDirectory
from unittest.mock import patch


FIXTURES = Path(__file__).resolve().parent / "devops"
DEVOPS_CASES = ("case-m", "case-n")
TASK = """В staging добавляем фоновую выгрузку отчёта в очередь exports. Воркер будет
отправлять запрос, собранный существующей функцией build_report_request из provider.py.
Оцени, что потребуется для выкладки. Код и конфигурацию оставь как есть.

Релизный job запускает docker compose -f compose.staging.json up -d. В его окружение
уже передаются адрес провайдера, рабочий токен для него и адрес брокера.
"""


def prepare_devops(case, folder):
    manifest = json.loads((FIXTURES / "compose.staging.json").read_text())
    if case == "case-n":
        manifest["services"]["worker"]["environment"].remove("REPORTS_AUTH_TOKEN")
    (folder / "compose.staging.json").write_text(json.dumps(manifest, indent=2) + "\n")
    shutil.copyfile(FIXTURES / "provider.py", folder / "provider.py")
    return TASK


def verify_devops_cases():
    job_env = {
        "REPORTS_URL": "https://provider.invalid/reports",
        "REPORTS_AUTH_TOKEN": "fixture-token",
        "CELERY_BROKER_URL": "redis://broker",
    }
    for case in DEVOPS_CASES:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            prepare_devops(case, folder)
            manifest = json.loads((folder / "compose.staging.json").read_text())
            build_request = run_path(str(folder / "provider.py"))["build_report_request"]
            command = manifest["services"]["worker"]["command"]
            if "exports" not in command[command.index("-Q") + 1].split(","):
                raise ValueError(f"{case}: worker must subscribe to exports")
            for name in ("api", "worker"):
                keys = manifest["services"][name]["environment"]
                with patch.dict(os.environ, {key: job_env[key] for key in keys}, clear=True):
                    try:
                        request = build_request({"id": 1})
                    except KeyError as error:
                        result = ("missing", error.args[0])
                    else:
                        if (request.full_url, request.get_header("Authorization")) != (
                            job_env["REPORTS_URL"], "Bearer fixture-token"
                        ):
                            raise ValueError(f"{case}: incorrect provider request")
                        result = ("ready",)
                expected = ("ready",)
                if case == "case-n" and name == "worker":
                    expected = ("missing", "REPORTS_AUTH_TOKEN")
                if result != expected:
                    raise ValueError(f"{case}/{name}: {result}, expected {expected}")
                print(f"{case}/{name}: {', '.join(result)}")
