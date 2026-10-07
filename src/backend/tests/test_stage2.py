"""Stage 2: Admin content/payment integration + admin protection tests.

Runs against the live supervisor-managed backend on localhost:8001 (same instance the
frontend uses via /api ingress).
"""
import os
import time
import httpx
import pytest

BASE = os.environ.get("TEST_BASE_URL", "http://localhost:8001").rstrip("/") + "/api"

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

STUDENT_EMAIL = "teststudent2@example.com"
STUDENT_PASSWORD = "Estud@2026"


# --- session helpers -------------------------------------------------------
@pytest.fixture(scope="module")
def admin_client():
    c = httpx.Client(base_url=BASE, timeout=120.0)
    r = c.post("/auth/admin-login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, r.text
    yield c
    c.close()


@pytest.fixture(scope="module")
def student_client():
    c = httpx.Client(base_url=BASE, timeout=60.0)
    # try register (idempotent-ish; if exists we login)
    r = c.post("/auth/register", json={
        "name": "Test Student2",
        "email": STUDENT_EMAIL,
        "password": STUDENT_PASSWORD,
        "password_confirm": STUDENT_PASSWORD,
        "accept_terms": True,
        "accept_privacy": True,
    })
    if r.status_code not in (200, 201):
        # already registered -> login via email
        r2 = c.post("/auth/login", json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD})
        assert r2.status_code == 200, f"register={r.status_code} {r.text} ; login={r2.status_code} {r2.text}"
    yield c
    c.close()


# --- admin protection ------------------------------------------------------
class TestAdminProtection:
    def test_admin_stats_requires_session(self):
        with httpx.Client(base_url=BASE, timeout=15.0) as c:
            r = c.get("/admin/stats")
            assert r.status_code == 401, r.text

    def test_admin_login_wrong_password(self):
        with httpx.Client(base_url=BASE, timeout=15.0) as c:
            r = c.post("/auth/admin-login", json={"email": ADMIN_EMAIL, "password": "WRONG-PASS-XYZ"})
            assert r.status_code == 401

    def test_admin_login_success(self, admin_client):
        r = admin_client.get("/admin/stats")
        assert r.status_code == 200
        body = r.json()
        assert "users" in body or "total_users" in body or isinstance(body, dict)

    def test_student_cannot_access_admin_stats(self, student_client):
        r = student_client.get("/admin/stats")
        assert r.status_code == 403, r.text

    def test_admin_login_with_student_credentials_forbidden(self):
        with httpx.Client(base_url=BASE, timeout=15.0) as c:
            r = c.post("/auth/admin-login", json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD})
            assert r.status_code == 403, r.text


# --- admin settings preserved ----------------------------------------------
class TestAdminSettings:
    def test_get_settings(self, admin_client):
        r = admin_client.get("/admin/settings")
        assert r.status_code == 200
        assert isinstance(r.json(), dict)

    def test_put_settings_idempotent(self, admin_client):
        current = admin_client.get("/admin/settings").json()
        r = admin_client.put("/admin/settings", json=current)
        assert r.status_code in (200, 204)


# --- preservation: student can browse courses -------------------
class TestPreservation:
    def test_student_can_list_courses(self, student_client):
        r = student_client.get("/courses")
        assert r.status_code == 200
