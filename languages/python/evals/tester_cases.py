import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "tester"
TASK = """Проверь реализацию по постановке. Можно добавлять и выполнять регрессионные
тесты в этой копии. Передай результаты и вопросы владельцу контракта.
Исходный набор запускается командой python3 -B -m unittest discover.
"""
CONTACT = """Сотрудник редактирует карточку через PATCH /contacts/1. Ответ 200
содержит сохранённые city и phone. Переданное строковое значение заменяет
соответствующее поле, пропущенные поля сохраняют прежние значения.
GET /contacts/1 возвращает актуальную карточку. Клиент request в api.py
вызывает WSGI-приложение с тестовой SQLite. Проверяем только эти два поля.
"""
INBOX = """На счёте 100 единиц. receive(db, event_id, amount) принимает начисление
и возвращает 200, в том числе при повторной доставке того же события. process_next(db)
обрабатывает следующее ожидающее событие. Успешная обработка даёт статус processed.
Один идентификатор даёт одно начисление независимо от момента повторной доставки.
Разные идентификаторы обрабатываются независимо. Используется SQLite и один воркер.
"""
SEATS = """Открыто одно место. reserve(db, guest) для двух разных гостей может
выдать только одну бронь, в том числе при одновременных заявках. Успех возвращает
201, отказ при занятом месте возвращает 409. В bookings должен остаться победитель.
Хранилище этого приложения - файловая SQLite, каждое обращение открывает своё
соединение. initialize(db) создаёт пустую схему.
"""

TESTER_CASES = {
    "case-h": ("profile", "replace.py", CONTACT + "Явный null для phone очищает номер.\n"),
    "case-i": ("inbox", None, INBOX),
    "case-j": ("seats", None, SEATS),
    "case-k": ("profile", "partial.py", CONTACT + "Клиент также спрашивает, можно ли передавать null для phone.\n"),
}


def prepare_tester(case, folder):
    kind, storage, contract = TESTER_CASES[case]
    files = {
        "profile": ("api.py", "test_api.py"),
        "inbox": ("service.py", "test_service.py"),
        "seats": ("booking.py", "test_booking.py"),
    }
    for name in files[kind]:
        shutil.copyfile(ROOT / kind / name, folder / name)
    if storage:
        shutil.copyfile(ROOT / kind / storage, folder / "storage.py")
    return TASK + "\n" + contract


def verify_tester_cases():
    for case in TESTER_CASES:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            prepare_tester(case, folder)
            subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "discover"], cwd=folder, check=True,
            )
            subprocess.run(
                [sys.executable, "-B", str(ROOT / "observe.py"), case], cwd=folder, check=True,
            )
