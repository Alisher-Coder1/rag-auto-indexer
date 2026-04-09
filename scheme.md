```mermaid
graph TD
    A[get_db_index()] --> B{knowledge_base.txt exists?}
    B -->|No| C[Raise FileNotFoundError]
    B -->|Yes| D[Compute current hash]
    D --> E[Load saved hash]
    E --> F{Rebuild needed?}
    F -->|Yes: index missing / hash missing / hash changed| G[_clean_index_dir]
    G --> H[build_and_save_faiss_index]
    H --> I[save_kb_hash]
    I --> J[load_faiss_index]
    F -->|No| J
    J -->|Load error| K[_clean_index_dir]
    K --> M[build_and_save_faiss_index]
    M --> N[save_kb_hash]
    N --> O[load_faiss_index again]
    O -->|Success| P[Return index]
    O -->|Error| Q[Raise RuntimeError]
    J -->|Success| P
```
