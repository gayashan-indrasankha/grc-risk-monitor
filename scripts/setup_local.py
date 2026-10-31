#!/usr/bin/env python3
"""Create a local SQLite demo database from CSVs. No pip install needed."""
from pathlib import Path
import sqlite3, csv
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'grc_stage1.sqlite'
if DB.exists():
    DB.unlink()   # reproducible demo; do not use on live business DBs!

with sqlite3.connect(DB) as conn:
    conn.execute('PRAGMA foreign_keys=ON')
    conn.executescript((ROOT/'sql'/'schema.sql').read_text(encoding='utf-8'))
    for table in ('employees','suppliers','purchase_requests','invoices','payments'):
        path=ROOT/'data'/f'{table}.csv'
        with path.open(newline='',encoding='utf-8') as f:
            reader=csv.DictReader(f)
            fields=reader.fieldnames
            rows=[]
            for record in reader:
                rows.append(tuple(record[k] if record[k]!='' else None for k in fields))
        qs=','.join(['?']*len(fields))
        conn.executemany(f"INSERT INTO {table} ({','.join(fields)}) VALUES ({qs})",rows)
        print(f'{table}: {len(rows)} records')
    conn.commit()
print(f'Created {DB}')
