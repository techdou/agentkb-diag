"""
Basic API tests for AgentKB-Diag backend.

These tests verify that all API endpoints are properly registered and
return the expected status codes and response shapes.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealth:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "AgentKB-Diag Backend"

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "endpoints" in data


class TestSources:
    def test_list_sources(self):
        response = client.get("/api/sources")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_load_demo(self):
        response = client.post("/api/sources/load-demo")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "source_count" in data

    def test_get_source_not_found(self):
        response = client.get("/api/sources/nonexistent")
        assert response.status_code == 404


class TestWiki:
    def test_list_pages(self):
        response = client.get("/api/wiki/pages")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_page_not_found(self):
        response = client.get("/api/wiki/pages/nonexistent")
        assert response.status_code == 404

    def test_overview(self):
        response = client.get("/api/wiki/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_sources" in data
        assert "total_claims" in data
        assert "total_pages" in data
        assert "rounds_available" in data


class TestDiagnosis:
    def test_run_diagnosis(self):
        response = client.post("/api/diagnosis/run", params={"round_name": ""})
        # Without any round data, it should return 404
        assert response.status_code in (200, 404)

    def test_summary(self):
        response = client.get("/api/diagnosis/summary")
        assert response.status_code in (200, 404)

    def test_list_issues(self):
        response = client.get("/api/diagnosis/issues")
        assert response.status_code in (200, 404)

    def test_get_issue_not_found(self):
        response = client.get("/api/diagnosis/issues/nonexistent")
        assert response.status_code == 404


class TestRetrieval:
    def test_search(self):
        response = client.post(
            "/api/retrieval/search",
            json={"query": "test query", "round_name": "", "top_k": 3},
        )
        assert response.status_code in (200, 404)

    def test_evaluate(self):
        response = client.post("/api/retrieval/evaluate", params={"round_name": ""})
        assert response.status_code in (200, 404)

    def test_failures(self):
        response = client.get("/api/retrieval/failures")
        assert response.status_code in (200, 404)


class TestGraph:
    def test_knowledge_graph(self):
        response = client.get("/api/graph/knowledge")
        assert response.status_code in (200, 404)

    def test_provenance_not_found(self):
        response = client.get("/api/graph/provenance", params={"claim_id": "nonexistent"})
        assert response.status_code == 404

    def test_failure_graph_not_found(self):
        response = client.get("/api/graph/failure", params={"query_id": "nonexistent"})
        assert response.status_code == 404


class TestExperiments:
    def test_get_metrics(self):
        response = client.get("/api/experiments/metrics")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_export_csv(self):
        response = client.get("/api/experiments/export", params={"format": "csv"})
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")

    def test_export_json(self):
        response = client.get("/api/experiments/export", params={"format": "json"})
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")

    def test_run_round_not_found(self):
        response = client.post(
            "/api/experiments/run-round",
            json={"round_name": "nonexistent"},
        )
        assert response.status_code == 404
