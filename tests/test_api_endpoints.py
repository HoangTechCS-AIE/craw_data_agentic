from __future__ import annotations

from fastapi.testclient import TestClient

from api import main
from api.deps import get_session
from api.models import Base, Record, create_engine_and_session


def test_records_endpoint_filters(tmp_path):
    db_url = f"sqlite:///{tmp_path}/records.db"
    engine, SessionLocal = create_engine_and_session(db_url)
    Base.metadata.create_all(engine)
    session = SessionLocal()
    session.add(
        Record(
            id="1",
            source="worldbank",
            dataset="Internet users",
            resource_id="IT.NET.USER.ZS",
            tags=["internet"],
            indicator="internet",
            province=None,
            province_code=None,
            year="2022",
            date=None,
            value=75.5,
            raw={"sample": True},
        )
    )
    session.commit()
    session.close()

    def override_session():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_session] = override_session
    client = TestClient(main.app)
    response = client.get("/api/records", params={"indicator": "internet"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["indicator"] == "internet"
    main.app.dependency_overrides.clear()
