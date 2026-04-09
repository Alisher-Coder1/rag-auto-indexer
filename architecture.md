project-root/
│
├── knowledge_base.txt # существующий файл с данными (исходная база знаний)
├── app.py (или rag.py) # существующий главный модуль, содержащий:
│ ├── build_and_save_faiss_index() # уже реализована
│ ├── load_faiss_index() # уже реализована (или будет выделена)
│ ├── get_db_index() # МОДИФИЦИРУЕТСЯ
│ └── добавляемые функции: # в том же файле, без новых модулей
│ ├── compute_file_hash()
│ ├── load_kb_hash()
│ ├── save_kb_hash()
│ ├── faiss_index_exists()
│ └── \_clean_index_dir() # внутренняя, не экспортируется
│
├── faiss_index/ # директория, создаваемая автоматически
│ ├── index.faiss # бинарный FAISS-индекс
│ └── docstore.json # метаданные документов
│
└── kb_hash.json # создаётся автоматически, хранит хеш knowledge_base.txt
