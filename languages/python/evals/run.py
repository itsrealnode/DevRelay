"""Prepare isolated cases and measure their behavior using Python's standard library."""

import argparse
import json
import shutil
import tempfile
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from runpy import run_path

from devops_cases import DEVOPS_CASES, prepare_devops, verify_devops_cases
from tester_cases import TESTER_CASES, prepare_tester, verify_tester_cases

BASE = Path(__file__).resolve().parent
PAGES = BASE / "pages"
JOBS = BASE / "jobs"
PAGE_CASES = {
    "case-a": "per_row.py",
    "case-b": "batched.py",
    "case-c": "late_slice.py",
    "case-d": "starter.py",
}
JOB_CASES = ("case-e", "case-f", "case-g")

PAGE_CONTRACT = """list_tickets(db, limit) возвращает первые limit заявок по возрастанию ID.
Элемент — пара (ID, имя команды), у заявки без команды имя равно None.
На вход поступает проверенный размер страницы от 1 до 50. Размер таблиц растёт.
Код работает на sqlite3 из стандартной библиотеки. Данные создаёт example_db.sample(size).
"""
ROLLOUT = """Выкладка постепенная. Формат сообщений определяется версией издателя.
Старые задачи и повторы могут оставаться в очереди сутки. Старые и новые воркеры
могут получать сообщения из общей очереди. До изменения язык отчёта был ru.
consumer.py — новая версия, legacy_consumer.py — предыдущая.
"""


def prepare(case):
    folder = Path(tempfile.mkdtemp(prefix="devrelay-python-case-"))
    if case in PAGE_CASES:
        shutil.copyfile(PAGES / PAGE_CASES[case], folder / "catalog.py")
        shutil.copyfile(PAGES / "example_db.py", folder / "example_db.py")
        action = "Реализуй" if case == "case-d" else "Проведи ревью реализации"
        prompt = f"{action} list_tickets в catalog.py.\n\n{PAGE_CONTRACT}"
    elif case in TESTER_CASES:
        prompt = prepare_tester(case, folder)
    elif case in DEVOPS_CASES:
        prompt = prepare_devops(case, folder)
    elif case == "case-o":
        shutil.copyfile(BASE / "tester" / "inbox" / "service.py", folder / "service.py")
        prompt = (
            "Покажи по коду на диаграмме, что означает 200 и что произойдёт, если "
            "одно и то же событие доставят ещё раз после его обработки. "
            "Для примера возьми начисление 50. Команда хочет гарантировать одно "
            "начисление на событие. Объясни, как предложил бы это обеспечить. "
            "Менять код не нужно."
        )
    elif case == "case-l":
        for name in ("storage.py", "get_investigation.py"):
            shutil.copyfile(BASE / "investigations" / name, folder / name)
        prompt = "Напиши use case на list для расследований, и всё."
    else:
        for name in ("consumer.py", "legacy_consumer.py"):
            shutil.copyfile(JOBS / name, folder / name)
        if case != "case-g":
            shutil.copyfile(JOBS / "messages.json", folder / "messages.json")
        if case == "case-e":
            prompt = "Проверь, можно ли выкатывать изменение формата задачи.\n\n" + ROLLOUT
        elif case == "case-f":
            shutil.copyfile(JOBS / "events.jsonl", folder / "events.jsonl")
            prompt = "После выкладки часть отчётов пропала, свежий запрос помог. Разберись в причине по приложенным материалам.\n\n" + ROLLOUT
        else:
            (folder / "events.jsonl").write_text(
                '{"time":"10:01:00Z","id":"C19","event":"published","version":"2"}\n',
                encoding="utf-8",
            )
            prompt = "Пользователь не увидел отчёт C19. Есть только фрагмент лога издателя. Определи, что известно, и предложи следующий шаг.\n\n" + ROLLOUT
    (folder / "TASK.md").write_text(prompt, encoding="utf-8")
    return folder


@dataclass(frozen=True)
class Reading:
    queries: int
    delivered_rows: int


def measure(implementation, size, limit):
    list_tickets = run_path(str(implementation))["list_tickets"]
    sample = run_path(str(PAGES / "example_db.py"))["sample"]
    statements = []
    delivered = 0

    def count_row(cursor, row):
        nonlocal delivered
        delivered += 1
        return row

    with closing(sample(size)) as db:
        db.execute("PRAGMA reverse_unordered_selects = ON")
        db.row_factory = count_row
        db.set_trace_callback(statements.append)
        result = list(list_tickets(db, limit))

    expected = [
        (i, f"Team {i}" if i % 4 else None)
        for i in range(1, min(size, limit) + 1)
    ]
    if result != expected:
        raise ValueError(f"{implementation.name}: incorrect page for {size=}, {limit=}")
    reads = sum(query.lstrip().upper().startswith(("SELECT", "WITH")) for query in statements)
    return Reading(reads, delivered)


def inspect_page(path):
    measure(path, 0, 1)
    measure(path, 3, 50)
    measure(path, 120, 50)
    small = measure(path, 80, 1)
    page = measure(path, 80, 20)
    grown = measure(path, 800, 20)
    print(f"{path.name}: SELECTs (page 1/20) {small.queries}/{page.queries}; "
          f"rows delivered (table 80/800, page 20) {page.delivered_rows}/{grown.delivered_rows}")
    return page.queries > small.queries + 1, grown.delivered_rows > page.delivered_rows


def verify_jobs():
    versions = {
        "v1": run_path(str(JOBS / "legacy_consumer.py"))["dispatch"],
        "v2": run_path(str(JOBS / "consumer.py"))["dispatch"],
    }
    messages = json.loads((JOBS / "messages.json").read_text())
    for code, compatible, expected in (
        ("A17", "v1", {"report_id": 17, "locale": "ru"}),
        ("B18", "v2", {"report_id": 18, "locale": "en"}),
    ):
        for version, dispatch in versions.items():
            try:
                outcome = dispatch(messages[code])
            except TypeError as error:
                if version == compatible or "locale" not in str(error):
                    raise
                print(f"{code} -> {version}: TypeError as expected")
            else:
                if version != compatible or outcome != expected:
                    raise ValueError(f"Unexpected dispatch result: {code}, {version}, {outcome}")
                print(f"{code} -> {version}: {outcome}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="check fixture output and distinguishing observations")
    prep = commands.add_parser("prepare", help="create a neutral working copy")
    prep.add_argument("case", choices=[*PAGE_CASES, *JOB_CASES, *TESTER_CASES, "case-l", *DEVOPS_CASES, "case-o"])
    page = commands.add_parser("check-page", help="check an implemented catalog.py")
    page.add_argument("implementation", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        print(prepare(args.case))
    elif args.command == "check-page":
        if any(inspect_page(args.implementation)):
            raise SystemExit("Page checks failed. Inspect queries and row counts.")
    else:
        for name, expected in (
            ("per_row.py", (True, False)),
            ("batched.py", (False, False)),
            ("late_slice.py", (False, True)),
        ):
            if inspect_page(PAGES / name) != expected:
                raise SystemExit(f"Fixture observations changed for {name}")
        verify_jobs()
        verify_tester_cases()
        verify_devops_cases()


if __name__ == "__main__":
    main()
