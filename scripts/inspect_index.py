#!/usr/bin/env python3
"""
Скрипт для анализа текущей реализации FAISS-индекса (Этап 1 дорожной карты).
Запускать из корня проекта: python scripts/inspect_index.py
"""

import os
import sys
import importlib.util
import inspect

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))


def main():
    print("=" * 60)
    print("Анализ существующей реализации FAISS-индекса")
    print("=" * 60)

    # 1. Определяем основной файл, где предположительно находится get_db_index
    possible_main_files = [
        "rag.py",
        "app.py",
        "main.py",
        "indexer.py",
        "faiss_utils.py",
    ]
    main_file = None
    for fname in possible_main_files:
        if os.path.exists(fname):
            main_file = fname
            break

    if not main_file:
        print("[ERROR] Не найден основной файл с get_db_index. Укажите имя вручную.")
        sys.exit(1)

    print(f"\n[+] Основной файл: {main_file}")

    # 2. Загружаем модуль
    spec = importlib.util.spec_from_file_location("project", main_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 3. Проверяем наличие get_db_index
    if not hasattr(module, "get_db_index"):
        print("[ERROR] Функция get_db_index не найдена в", main_file)
        sys.exit(1)
    print("[+] get_db_index найдена")

    # 4. Проверяем наличие build_and_save_faiss_index
    if hasattr(module, "build_and_save_faiss_index"):
        print("[+] build_and_save_faiss_index найдена")
        sig = inspect.signature(module.build_and_save_faiss_index)
        print(f"    Сигнатура: {sig}")
    else:
        print("[WARN] build_and_save_faiss_index не найдена")

    # 5. Проверяем наличие load_faiss_index
    if hasattr(module, "load_faiss_index"):
        print("[+] load_faiss_index найдена")
        sig = inspect.signature(module.load_faiss_index)
        print(f"    Сигнатура: {sig}")
    else:
        print(
            "[WARN] load_faiss_index не найдена. Возможно, загрузка внутри get_db_index."
        )

    # 6. Ищем константы путей
    constants = ["INDEX_DIR", "KNOWLEDGE_BASE_PATH", "HASH_STORE_PATH"]
    print("\n[Поиск констант путей]:")
    for const in constants:
        if hasattr(module, const):
            val = getattr(module, const)
            print(f"  {const} = {val}")
        else:
            print(f"  {const} = (не определена)")

    # 7. Пытаемся определить пути из кода get_db_index
    print("\n[Анализ тела get_db_index]:")
    source = inspect.getsource(module.get_db_index)
    # Примитивный поиск упоминаний путей
    import re

    patterns = [
        r'["\']([^"\']*faiss[^"\']*\.(?:bin|pkl|faiss))["\']',
        r'["\']([^"\']*docstore[^"\']*\.json)["\']',
        r'["\']([^"\']*knowledge_base\.txt)["\']',
    ]
    for pat in patterns:
        matches = re.findall(pat, source, re.IGNORECASE)
        if matches:
            print(f"  Найдены возможные пути: {matches}")

    # 8. Проверяем, создаётся ли директория индекса
    if "makedirs" in source or "exist_ok" in source:
        print("[+] build_and_save_faiss_index или get_db_index создают директорию")
    else:
        print(
            "[?] Не обнаружено явного создания директории. Возможно, требуется добавить."
        )

    print("\n" + "=" * 60)
    print("Рекомендации по результатам анализа:")
    print(
        "- Зафиксируйте константы в начале файла (INDEX_DIR, KNOWLEDGE_BASE_PATH, HASH_STORE_PATH)."
    )
    print(
        "- Уточните точные имена файлов индекса (например, index.faiss, docstore.json)."
    )
    print("- Убедитесь, что load_faiss_index существует; если нет – выделите её.")
    print(
        "- Проверьте, создаёт ли build_and_save_faiss_index директорию. Если нет – добавьте os.makedirs."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
