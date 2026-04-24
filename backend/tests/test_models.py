from sqlalchemy import create_engine, inspect

from app.models import Base


def test_tables_can_be_created() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert "users" in tables
    assert "job_postings" in tables
    assert "applications" in tables
    assert "match_scores" in tables
    assert "invitations" in tables
    assert "audit_logs" in tables
