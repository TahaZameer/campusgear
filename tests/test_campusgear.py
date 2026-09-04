import pytest
from app.main import app
from app.database import LocalSession
from app.models import User, Category, Item, LoanRequest, LoanEvent
from app.enums import Role, ItemCondition, ItemStatus, LoanStatus, LoanEventType
from app.auth import password_hashing
from app.schemas import Token
from fastapi.testclient import TestClient
from datetime import date, datetime

@pytest.fixture
def client():
    client = TestClient(app)
    return client

@pytest.fixture
def db():
    session = LocalSession()

    yield session

    session.query(LoanEvent).delete()
    session.query(LoanRequest).delete()
    session.query(Item).delete()
    session.query(Category).delete()
    session.query(User).delete()

    session.commit()
    session.close()

@pytest.fixture
def users(db):
    admin = User(
        full_name="Test Admin",
        email="admin@test.com",
        password_hash=password_hashing.hash("admin"),
        role=Role.admin,
    )

    staff = User(
        full_name="Test Staff",
        email="staff@test.com",
        password_hash=password_hashing.hash("staff"),
        role=Role.staff,
    )

    member = User(
        full_name="Test Member",
        email="member@test.com",
        password_hash=password_hashing.hash("member"),
        role=Role.member,
    )

    member2 = User(
        full_name="Test Member 2",
        email="member2@test.com",
        password_hash=password_hashing.hash("member2"),
        role=Role.member,
    )

    db.add_all([admin, staff, member, member2])
    db.commit()

    return {
        "member": member,
        "member2": member2,
        "staff": staff,
        "admin": admin,
    }

@pytest.fixture
def categories_and_items(db):
    category1 = Category(
        name="cameras",
        description="Camera equipment"
    )

    category2 = Category(
        name="laptops",
        description="Laptop equipment"
    )

    db.add_all([category1, category2])
    db.flush()

    item1 = Item(
        name="Canon Camera",
        category_id=category1.id,
        asset_code="CAM-001",
        description="Test camera",
        condition=ItemCondition.good,
        purchase_date=date(2025, 1, 10),
        status=ItemStatus.available,
    )

    item2 = Item(
        name="Nikon Camera",
        category_id=category1.id,
        asset_code="CAM-002",
        description="Another test camera",
        condition=ItemCondition.good,
        purchase_date=date(2025, 2, 10),
        status=ItemStatus.requested,
    )

    item3 = Item(
        name="Dell Laptop",
        category_id=category2.id,
        asset_code="LAP-001",
        description="Test laptop",
        condition=ItemCondition.excellent,
        purchase_date=date(2025, 3, 10),
        status=ItemStatus.checked_out,
    )

    item4 = Item(
        name="Razor Laptop",
        category_id=category2.id,
        asset_code="LAP-009",
        description="Gaming laptop",
        condition=ItemCondition.excellent,
        purchase_date=date(2025, 3, 10),
        status=ItemStatus.available,
    )

    db.add_all([item1, item2, item3, item4])
    db.commit()

    return {
        "categories": [category1, category2],
        "items": [item1, item2, item3, item4],
    }

@pytest.fixture
def loan_requests(db, users, categories_and_items):
    member = users["member"]

    item1 = categories_and_items["items"][0]
    item2 = categories_and_items["items"][1]
    item3 = categories_and_items["items"][2]
    item4 = categories_and_items["items"][3]

    request1 = LoanRequest(
        item_id=item1.id,
        borrower_id=member.id,
        requested_return_date=date(2028, 2, 9),
        status=LoanStatus.pending
    )

    request2 = LoanRequest(
    item_id=item2.id,
    borrower_id=member.id,
    requested_return_date=date(2028, 3, 15),
    status=LoanStatus.approved
    )

    request3 = LoanRequest(
        item_id=item3.id,
        borrower_id=member.id,
        requested_return_date=date(2027, 1, 20),
        status=LoanStatus.checked_out
    )

    request4 = LoanRequest(
        item_id=item1.id,
        borrower_id=member.id,
        requested_return_date=date(2026, 1, 10),
        status=LoanStatus.rejected,
        decision_reason="Item was needed for another purpose"
    )

    request5 = LoanRequest(
        item_id=item1.id,
        borrower_id=member.id,
        requested_return_date=date(2026, 1, 10),
        status=LoanStatus.pending
    )

    request6 = LoanRequest(
        item_id=item4.id,
        borrower_id=member.id,
        requested_return_date=date(2026, 8, 21),
        status=LoanStatus.returned,
        return_condition=ItemCondition.good,
        returned_at=datetime(2026, 8, 22, 14, 30)
    )

    db.add_all([request1, request2, request3, request4, request5, request6])
    db.commit()

    return {
        "requests": [request1, request2, request3, request4, request5, request6]
    }

@pytest.fixture
def multi_user_loan_requests(db, users, categories_and_items):
    member = users["member"]
    member2 = users["member2"]

    item1 = categories_and_items["items"][0]
    item2 = categories_and_items["items"][1]
    item3 = categories_and_items["items"][2]
    item4 = categories_and_items["items"][3]

    request1 = LoanRequest(
        item_id=item1.id,
        borrower_id=member.id,
        requested_return_date=date(2028, 2, 9),
        status=LoanStatus.pending
    )

    request2 = LoanRequest(
        item_id=item2.id,
        borrower_id=member.id,
        requested_return_date=date(2028, 3, 15),
        status=LoanStatus.approved
    )

    request3 = LoanRequest(
        item_id=item3.id,
        borrower_id=member.id,
        requested_return_date=date(2027, 1, 20),
        status=LoanStatus.checked_out
    )

    request4 = LoanRequest(
        item_id=item1.id,
        borrower_id=member2.id,
        requested_return_date=date(2026, 1, 10),
        status=LoanStatus.rejected,
        decision_reason="Item was needed for another purpose"
    )

    request5 = LoanRequest(
        item_id=item1.id,
        borrower_id=member2.id,
        requested_return_date=date(2026, 1, 10),
        status=LoanStatus.pending
    )

    request6 = LoanRequest(
        item_id=item4.id,
        borrower_id=member2.id,
        requested_return_date=date(2026, 8, 21),
        status=LoanStatus.returned,
        return_condition=ItemCondition.good,
        returned_at=datetime(2026, 8, 22, 14, 30)
    )

    db.add_all([
        request1, request2, request3,
        request4, request5, request6
    ])
    db.commit()

    return {
        "requests": [
            request1, request2, request3,
            request4, request5, request6
        ],
        "member1_requests": [request1, request2, request3],
        "member2_requests": [request4, request5, request6],
    }

@pytest.fixture
def overdue_loan_requests(db, users, categories_and_items):
    member = users["member"]

    item1 = categories_and_items["items"][0]
    item2 = categories_and_items["items"][1]
    item3 = categories_and_items["items"][2]

    request1 = LoanRequest(
        item_id=item1.id,
        borrower_id=member.id,
        requested_return_date=date(2026, 7, 21),
        status=LoanStatus.checked_out,
    )

    request2 = LoanRequest(
    item_id=item2.id,
    borrower_id=member.id,
    requested_return_date=date(2026, 8, 21),
    status=LoanStatus.checked_out,
    )

    request3 = LoanRequest(
        item_id=item3.id,
        borrower_id=member.id,
        requested_return_date=date(2023, 11, 20),
        status=LoanStatus.checked_out,
    )

    request4 = LoanRequest(
        item_id=item1.id,
        borrower_id=member.id,
        requested_return_date=date(2026, 1, 10),
        status=LoanStatus.checked_out
    )

    request5 = LoanRequest(
        item_id=item1.id,
        borrower_id=member.id,
        requested_return_date=date(2026, 7, 12),
        status=LoanStatus.checked_out
    )

    request6 = LoanRequest(
        item_id=item3.id,
        borrower_id=member.id,
        requested_return_date=date(2026, 8, 1),
        status=LoanStatus.checked_out
    )

    db.add_all([request1, request2, request3, request4, request5, request6])
    db.commit()

    return {
        "requests": [request1, request2, request3, request4, request5, request6]
    }

def login_as_admin(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@test.com",
            "password": "admin"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"

def login_as_member(client, no):

    if no == 1:
        response = client.post(
            "/auth/login",
            data={
                "username": "member@test.com",
                "password": "member"
            }
        )
    elif no == 2:
        response = client.post(
                "/auth/login",
                data={
                    "username": "member2@test.com",
                    "password": "member2"
                }
            )

    assert response.status_code == 200

    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"

def login_as_staff(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "staff@test.com",
            "password": "staff"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"

def test_register(db, client):
    response = client.post("/auth/register", json={"full_name": "hello", "email": "user@main.com", "password": "user"})
    assert response.status_code == 200

def test_dupe_register(db, client):
    response = client.post("/auth/register", json={"full_name": "hello", "email": "user@main.com", "password": "user"})
    assert response.status_code == 200
    response = client.post("/auth/register", json={"full_name": "hello", "email": "user@main.com", "password": "user"})
    assert response.status_code == 409

def test_wrong_register(db, client, users):
    response = client.post("/auth/register", json={"full_name": "dare", "email": "user@main.com", "password": "ussdasdasdadsadaser"})
    assert response.status_code == 422

def test_login(db, client, users):
    response = client.post("/auth/login", data={"username": "admin@test.com", "password": "admin"})
    data = response.json()

    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert response.status_code == 200

def test_wrong_login(db, client):
    response = client.post("/auth/login", data={"username": "admin@test.com", "password": "wrong-pass"})
    assert response.status_code == 401

def test_me(db, client, users):
    login_as_member(client, 1)

    response = client.get("/auth/me")
    assert response.status_code == 200

def test_me_without_token(db, client):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_create_category_as_admin(db, users, client):
    login_as_admin(client)

    response = client.post('/categories', json={"name": "testing", "description": "empty"})
    assert response.status_code == 200
    assert response.json()["name"] == "testing"

def test_create_category_as_staff(db, users, client):
    login_as_staff(client)

    response = client.post('/categories', json={"name": "testing", "description": "empty"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not Authorized"

def test_create_category_as_member(db, users, client):
    login_as_member(client, 1)

    response = client.post('/categories', json={"name": "testing", "description": "empty"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not Authorized"

def test_create_item_as_member(db, users, client):
    login_as_member(client, 1)

    response = client.post("/items/", json={"name": "bat", "category": "sports", "asset_code": "ABC123", "description": "New Good Bat", "condition": "good", "purchase_date": "2024-08-22"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Not Authorized"

def test_edit_item_as_member(db, users, client, categories_and_items):
    login_as_member(client, 1)

    item = categories_and_items["items"][0]

    response = client.patch(f"/items/{item.id}", json={"name": "noob"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not Authorized"

def test_delete_item_as_member(db, users, client, categories_and_items):
    login_as_member(client, 1)

    item = categories_and_items["items"][0]
    response = client.delete(f"items/{item.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not Authorized"

def test_create_item_as_admin_staff(db, users, client, categories_and_items):
    login_as_staff(client)

    response = client.post("/items/", json={"name": "bat", "category": "cameras", "asset_code": "ABC123", "description": "New Good Bat", "condition": "good", "purchase_date": "2024-08-22"})

    assert response.status_code == 200
    assert response.json()["name"] == "bat"

    login_as_admin(client)
    
    response = client.post("/items/", json={"name": "bat", "category": "laptops", "asset_code": "ABCD1234", "description": "New Good Bat", "condition": "good", "purchase_date": "2024-08-22"})

    assert response.status_code == 200
    assert response.json()["name"] == "bat"

def test_member_state_changing(db, client, users, loan_requests):
    login_as_member(client, 1)
    req_to_approve = loan_requests["requests"][0]
    response = client.patch(f"/staff/requests/{req_to_approve.id}/approve")
    assert response.status_code == 403

    req_to_checkout = loan_requests["requests"][1]
    response = client.patch(f"/staff/requests/{req_to_checkout.id}/checkout")
    assert response.status_code == 403

    req_to_reject = loan_requests["requests"][0]
    response = client.patch(f"/staff/requests/{req_to_reject.id}/reject")
    assert response.status_code == 403

    req_to_return = loan_requests["requests"][2]
    response = client.patch(f"/staff/requests/{req_to_return.id}/return", json={"item_condition": "excellent"})
    assert response.status_code == 403

def test_loan_req_creation_as_member(db, users, categories_and_items, client):
    login_as_member(client, 1)

    item = categories_and_items["items"][0]

    response = client.post(f"/items/{item.id}/requests", json={"requested_return_date": "2028-02-09"})

    assert response.status_code == 200

def test_loan_req_creation_as_staff(db, users, categories_and_items, client):
    login_as_staff(client)

    item = categories_and_items["items"][0]

    response = client.post(f"/items/{item.id}/requests", json={"requested_return_date": "2028-02-09"})
    
    assert response.status_code == 403

def test_loan_req_creation_as_admin(db, users, categories_and_items, client):
    login_as_admin(client)

    item = categories_and_items["items"][0]

    response = client.post(f"/items/{item.id}/requests", json={"requested_return_date": "2028-02-09"})
    
    assert response.status_code == 403

def test_loan_approval_as_staff(db, users, client, loan_requests):
    login_as_staff(client)

    request = loan_requests["requests"][0]
    item_id = request.item_id

    response = client.get(f"/items/{item_id}")

    info = response.json()

    assert info["status"] == "available"

    response = client.patch(f"/staff/requests/{request.id}/approve")
    assert response.status_code == 200

    response = client.get(f"/items/{item_id}")

    info = response.json()

    assert response.status_code == 200  
    assert info["status"] == "requested"

def test_loan_rejection_as_staff(db, users, client, loan_requests):
    login_as_staff(client)

    request = loan_requests["requests"][0]
    item_id = request.item_id

    response = client.get(f"/items/{item_id}")
    info = response.json()
    assert info["status"] == "available"

    response = client.patch(f"/staff/requests/{request.id}/reject")
    assert response.status_code == 200

    response = client.get(f"/items/{item_id}")
    info = response.json()
    assert info["status"] == "available"

def test_loan_checkout_as_staff(db, users, client, loan_requests):
    login_as_staff(client)

    request = loan_requests["requests"][1]

    response = client.patch(f"/staff/requests/{request.id}/checkout")

    assert response.status_code == 200

def test_loan_return_as_staff(db, users, client, loan_requests):
    login_as_staff(client)

    request = loan_requests["requests"][2]
    item_id = request.item_id

    response = client.get(f"/items/{item_id}")
    info = response.json()
    assert info["status"] == "checked_out"
    assert info["condition"] == "excellent"

    response = client.patch(f"/staff/requests/{request.id}/return", json={"item_condition": "damaged"})

    assert response.status_code == 200

    response = client.get(f"/items/{item_id}")
    info = response.json()
    assert info["condition"] == "damaged"
    assert info["status"] == "available"

    ######

def test_loan_approval_as_admin(db, users, client, loan_requests):
    login_as_admin(client)

    request = loan_requests["requests"][0]
    item_id = request.item_id

    response = client.get(f"/items/{item_id}")

    info = response.json()

    assert info["status"] == "available"

    response = client.patch(f"/staff/requests/{request.id}/approve")
    assert response.status_code == 200

    response = client.get(f"/items/{item_id}")

    info = response.json()

    assert response.status_code == 200  
    assert info["status"] == "requested"

def test_loan_rejection_as_admin(db, users, client, loan_requests):
    login_as_admin(client)

    request = loan_requests["requests"][0]
    item_id = request.item_id

    response = client.get(f"/items/{item_id}")
    info = response.json()
    assert info["status"] == "available"

    response = client.patch(f"/staff/requests/{request.id}/reject")
    assert response.status_code == 200

    response = client.get(f"/items/{item_id}")
    info = response.json()
    assert info["status"] == "available"

def test_loan_checkout_as_admin(db, users, client, loan_requests):
    login_as_admin(client)

    request = loan_requests["requests"][1]

    response = client.patch(f"/staff/requests/{request.id}/checkout")

    assert response.status_code == 200

def test_loan_return_as_admin(db, users, client, loan_requests):
    login_as_admin(client)

    request = loan_requests["requests"][2]
    item_id = request.item_id

    response = client.get(f"/items/{item_id}")
    info = response.json()
    assert info["status"] == "checked_out"
    assert info["condition"] == "excellent"

    response = client.patch(f"/staff/requests/{request.id}/return", json={"item_condition": "damaged"})

    assert response.status_code == 200

    response = client.get(f"/items/{item_id}")
    info = response.json()
    assert info["condition"] == "damaged"
    assert info["status"] == "available"

    ######

def test_category_creation(db, client, users):
    login_as_admin(client)

    response = client.post("/categories", json={"name": "Camera", "description": "Cameras are good"})
    assert response.status_code == 200
    assert response.json()["name"] == "camera"

    response = client.get("/categories")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "camera"

def test_requesting_requested_item(db, client, categories_and_items, users):
    login_as_member(client, 1)

    item = categories_and_items["items"][1]

    response = client.post(f"/items/{item.id}/requests", json={"requested_return_date": "2026-08-21"})
    assert response.status_code == 409

def test_two_request_approval(db, client, users, loan_requests):
    login_as_staff(client)

    request1 = loan_requests["requests"][0]
    request2 = loan_requests["requests"][4]

    response = client.patch(f"/staff/requests/{request1.id}/approve")
    assert response.status_code == 200

    response = client.patch(f"/staff/requests/{request2.id}/approve")
    assert response.status_code == 409

def test_edit_returned_loan(db, client, users, loan_requests):
    login_as_staff(client)

    req = loan_requests["requests"][5]

    response = client.patch(f"/staff/requests/{req.id}/approve")
    assert response.status_code == 409

    response = client.patch(f"/staff/requests/{req.id}/reject")
    assert response.status_code == 409

    response = client.patch(f"/staff/requests/{req.id}/checkout")
    assert response.status_code == 409

    response = client.patch(f"/staff/requests/{req.id}/return", json={"item_condition": "excellent"})
    assert response.status_code == 409

def test_overdue_filtering_as_member(client, db, users, loan_requests):
    login_as_member(client, 1)

    response = client.get("/staff/loans/overdue")

    assert response.status_code == 403

def test_overdue_filtering(client, db, users, overdue_loan_requests):
    login_as_staff(client)

    response = client.get("/staff/loans/overdue")

    assert response.status_code == 200

    requests = response.json()

    request = requests[0]

    print(requests)

    assert len(requests) == 6

    assert request["status"] == LoanStatus.overdue

def test_delete_active_loan_item(db, users, loan_requests, client):
    login_as_staff(client)

    request = loan_requests["requests"][2] #23 fail

    response = client.get(f"/items/{request.item_id}")

    assert response.json()["status"] == ItemStatus.checked_out

    response = client.delete(f'/items/{request.item_id}')

    assert response.status_code == 409

    #response = client.get(f"/items/{request.item_id}")
    
    #assert response.json()["status"] == ItemStatus.retired

def test_see_own_requests_member1(db, client, multi_user_loan_requests, users):
    login_as_member(client, 1)

    response = client.get("/requests/mine")
    requests = response.json()

    assert len(requests) == 3
    assert response.status_code == 200

    assert all(request["borrower_id"] == users["member"].id for request in requests)

def test_see_own_requests_member2(db, client, multi_user_loan_requests, users):
    login_as_member(client, 2)

    response = client.get("/requests/mine")
    requests = response.json()

    assert len(requests) == 3
    assert response.status_code == 200
    assert all(request["borrower_id"] == users["member2"].id for request in requests)

def test_full_workflow(client, categories_and_items, users):
    login_as_member(client, 1)

    #create loan request

    item = categories_and_items["items"][0]
    assert item.status == ItemStatus.available

    response = client.post(f"/items/{item.id}/requests", json={"requested_return_date": "2027-08-20"})
    assert response.status_code == 200
    request = response.json()
    assert request["status"] == LoanStatus.pending

    #approve loan request

    login_as_staff(client)
    response = client.patch(f"/staff/requests/{request["id"]}/approve")
    assert response.status_code == 200
    request = response.json()
    assert request["status"] == LoanStatus.approved

    response = client.get(f"/items/{item.id}")
    assert response.status_code == 200
    assert response.json()["status"] == ItemStatus.requested

    #checkout loan request

    response = client.patch(f"/staff/requests/{request["id"]}/checkout")
    assert response.status_code == 200
    request = response.json()
    assert request["status"] == LoanStatus.checked_out

    response = client.get(f"/items/{item.id}")
    assert response.status_code == 200
    assert response.json()["status"] == ItemStatus.checked_out

    #return loan_request

    response = client.get(f"/items/{item.id}")
    assert response.status_code == 200
    assert response.json()["status"] == ItemStatus.checked_out
    assert response.json()["condition"] == ItemCondition.good

    response = client.patch(f"/staff/requests/{request["id"]}/return", json={"item_condition": ItemCondition.damaged})
    assert response.status_code == 200
    request = response.json()
    assert request["returned_at"] is not None
    assert request["checked_out_at"] is not None
    assert request["status"] == LoanStatus.returned
    assert request["return_condition"] == ItemCondition.damaged

    response = client.get(f"/items/{item.id}")
    assert response.json()["status"] == ItemStatus.available
    assert response.json()["condition"] == ItemCondition.damaged

def test_cancel_own_pending_request(client, categories_and_items, loan_requests, users):
    login_as_member(client, 1)

    req = loan_requests["requests"][0] # or 4

    response = client.patch(f"/requests/{req.id}/cancel")
    assert response.status_code == 200

def test_cancel_own_approved_request(client, categories_and_items, loan_requests, users):
    login_as_member(client, 1)

    req = loan_requests["requests"][1]

    response = client.patch(f"/requests/{req.id}/cancel")
    assert response.status_code == 409

def test_cancel_own_checked_out_request(client, categories_and_items, loan_requests, users):
    login_as_member(client, 1)

    req = loan_requests["requests"][2]

    response = client.patch(f"/requests/{req.id}/cancel")
    assert response.status_code == 409

def test_cancel_own_rejected_request(client, categories_and_items, loan_requests, users):
    login_as_member(client, 1)

    req = loan_requests["requests"][3]

    response = client.patch(f"/requests/{req.id}/cancel")
    assert response.status_code == 409

def test_cancel_own_returned_request(client, categories_and_items, loan_requests, users):
    login_as_member(client, 1)

    req = loan_requests["requests"][5]

    response = client.patch(f"/requests/{req.id}/cancel")
    assert response.status_code == 409

def test_cancel_other_member_request(client, multi_user_loan_requests, users):
    login_as_member(client, 1)

    req = multi_user_loan_requests["member2_requests"][2]

    response = client.patch(f"/requests/{req.id}/cancel")
    assert response.status_code == 404

def test_item_history(client, users, loan_requests):
    login_as_staff(client)
    req = loan_requests["requests"][0]
    response = client.get(f"/items/{req.item_id}/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) > 0

def test_loan_events(db, client, users, loan_requests):
    login_as_staff(client)

    req = loan_requests["requests"][0]

    response = client.patch(
        f"/staff/requests/{req.id}/approve"
    )
    assert response.status_code == 200

    response = client.patch(
        f"/staff/requests/{req.id}/checkout"
    )
    assert response.status_code == 200

    response = client.patch(
        f"/staff/requests/{req.id}/return",
        json={"item_condition": "excellent"}
    )
    assert response.status_code == 200

    events = (
        db.query(LoanEvent)
        .filter(LoanEvent.loan_request_id == req.id)
        .all()
    )

    assert len(events) == 3

    assert events[0].event_type == LoanEventType.approved
    assert events[0].old_status == LoanStatus.pending
    assert events[0].new_status == LoanStatus.approved

    assert events[1].event_type == LoanEventType.checked_out
    assert events[1].old_status == LoanStatus.approved
    assert events[1].new_status == LoanStatus.checked_out

    assert events[2].event_type == LoanEventType.returned
    assert events[2].old_status == LoanStatus.checked_out
    assert events[2].new_status == LoanStatus.returned

def test_request_with_past_return_date(client, categories_and_items, users):
    login_as_member(client, 1)

    item = categories_and_items["items"][0]

    response = client.post(
        f"/items/{item.id}/requests",
        json={"requested_return_date": "2020-01-01"}
    )

    assert response.status_code == 400