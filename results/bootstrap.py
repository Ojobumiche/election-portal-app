from ast import literal_eval
from pathlib import Path

from django.db import connection, transaction


def _read_insert_rows(file_path: Path):
    if not file_path.exists():
        print(f"[BOOTSTRAP] Skipping missing file: {file_path}")
        return []

    content = file_path.read_text(encoding='utf-8')

    values_marker = 'VALUES'
    start = content.find(values_marker)
    if start == -1:
        return []

    values_text = content[start + len(values_marker):].strip().rstrip(';')
    values_text = values_text.replace('NULL', 'None')

    try:
        return list(literal_eval(f'[{values_text}]'))
    except Exception as e:
        print(f"[BOOTSTRAP] Failed parsing {file_path}: {e}")
        return []


def _ensure_tables():
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS states (
                state_id INTEGER PRIMARY KEY,
                state_name VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lga (
                uniqueid INTEGER PRIMARY KEY,
                lga_id INTEGER NOT NULL,
                lga_name VARCHAR(50) NOT NULL,
                state_id INTEGER NOT NULL,
                lga_description TEXT,
                entered_by_user VARCHAR(50) NOT NULL,
                date_entered TIMESTAMP NOT NULL,
                user_ip_address VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ward (
                uniqueid INTEGER PRIMARY KEY,
                ward_id INTEGER NOT NULL,
                ward_name VARCHAR(50) NOT NULL,
                lga_id INTEGER NOT NULL,
                ward_description TEXT,
                entered_by_user VARCHAR(50) NOT NULL,
                date_entered TIMESTAMP NOT NULL,
                user_ip_address VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS polling_unit (
                uniqueid INTEGER PRIMARY KEY,
                polling_unit_id INTEGER NOT NULL,
                ward_id INTEGER NOT NULL,
                lga_id INTEGER NOT NULL,
                uniquewardid INTEGER,
                polling_unit_number VARCHAR(50),
                polling_unit_name VARCHAR(100),
                polling_unit_description TEXT,
                lat VARCHAR(255),
                long VARCHAR(255),
                entered_by_user VARCHAR(50),
                date_entered TIMESTAMP,
                user_ip_address VARCHAR(50)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announced_pu_results (
                result_id INTEGER PRIMARY KEY,
                polling_unit_uniqueid INTEGER NOT NULL,
                party_abbreviation VARCHAR(10) NOT NULL,
                party_score INTEGER NOT NULL,
                entered_by_user VARCHAR(50) NOT NULL,
                date_entered TIMESTAMP NOT NULL,
                user_ip_address VARCHAR(50) NOT NULL
            )
        """)


def _bulk_seed(model_class, rows, field_map):
    objects = []

    for row in rows:
        data = {field: None for field in field_map}

        for index, field in enumerate(field_map):
            if index < len(row):
                data[field] = row[index]

        objects.append(model_class(**data))

    if objects:
        model_class.objects.bulk_create(objects, ignore_conflicts=True)


def bootstrap_legacy_database():
    project_root = Path(__file__).resolve().parent.parent.parent

    polling_unit_sql = project_root / 'polling_unit_data.sql'
    lga_sql = project_root / 'lga_data.sql'
    announced_results_sql = project_root / 'announced_pu_results.sql'

    _ensure_tables()

    from .models import LGA, PollingUnit, AnnouncedPUResult

    with transaction.atomic():

        lga_rows = _read_insert_rows(lga_sql)
        pu_rows = _read_insert_rows(polling_unit_sql)
        result_rows = _read_insert_rows(announced_results_sql)

        if lga_rows:
            _bulk_seed(
                LGA,
                lga_rows,
                [
                    'uniqueid',
                    'lga_id',
                    'lga_name',
                    'state_id',
                    'lga_description',
                    'entered_by_user',
                    'date_entered',
                    'user_ip_address',
                ],
            )

        if pu_rows:
            _bulk_seed(
                PollingUnit,
                pu_rows,
                [
                    'uniqueid',
                    'polling_unit_id',
                    'ward_id',
                    'lga_id',
                    'polling_unit_name',
                ],
            )

        if result_rows:
            _bulk_seed(
                AnnouncedPUResult,
                result_rows,
                [
                    'result_id',
                    'polling_unit_uniqueid',
                    'party_abbreviation',
                    'party_score',
                    'entered_by_user',
                    'date_entered',
                    'user_ip_address',
                ],
            )