from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.index import create_in
from whoosh.writing import AsyncWriter
import os
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

def process_chunk(chunk):
    index_dir, schema, chunk_data = chunk
    ix = create_in(index_dir, schema)
    writer = AsyncWriter(ix)

    for _, row in chunk_data.iterrows():
        writer.add_document(
            file_name=row["Filename"],
            word=row["word"],
            page=row["page"],
            count=row["count"],
            author=row.get("Author", "Unknown"),
            create_date=row.get("CreateDate", "Unknown"),
        )
    writer.commit()


def create_index(data_path, index_dir):
    # Schema definieren
    schema = Schema(
        file_name=TEXT(stored=True),
        word=TEXT,
        page=NUMERIC(stored=True),
        count=NUMERIC,
        author=TEXT(stored=True),
        create_date=TEXT(stored=True)
    )

    # Index erstellen, falls Verzeichnis nicht existiert
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    # Daten laden
    data = pd.read_parquet(data_path)
    chunk_size = len(data) // cpu_count()
    chunks = [data.iloc[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    # Fortschrittsbalken initialisieren
    with tqdm(total=len(chunks), desc="Indexing chunks", unit="chunk") as pbar:
        with Pool(cpu_count()) as pool:
            for _ in pool.imap_unordered(
                process_chunk, [(index_dir, schema, chunk) for chunk in chunks]
            ):
                pbar.update(1)

    print("Indexing complete.")


if __name__ == "__main__":
    data_path = r"C:\Users\Michel\Documents\GitHub\1A_PYTHON\CAS IR Leistungsnachweis\IR Project V2 opt search engine\v2_filebased_index\indices\search_index_with_filenames.parquet"
    index_dir = r"P:\PY\CAS IR Leistungsnachweis\whoosh_index"
    create_index(data_path, index_dir)
