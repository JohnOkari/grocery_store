from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response as DRFResponse
from typing import cast, Any, Dict
from store.models import Category, Product, Order


def make_user(username: str = "alice", password: str = "pass") -> User:
    return User.objects.create_user(username=username, password=password)


def auth_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_create_category_authenticated(db):
    user = make_user()
    client = auth_client(user)
    url = reverse('category-create')
    resp = cast(DRFResponse, client.post(url, {"name": "Fruits", "parent": None}, format='json'))
    assert resp.status_code == status.HTTP_201_CREATED
    assert Category.objects.filter(name="Fruits").exists()


def test_product_create_and_average_price(db):
    user = make_user()
    client = auth_client(user)

    # Create category tree
    root = Category.objects.create(name="Food")
    child = Category.objects.create(name="Fruits", parent=root)

    # Create products
    p1 = Product.objects.create(name="Apple", price=10, category=child)
    p2 = Product.objects.create(name="Banana", price=20, category=child)

    # Average price endpoint
    url = reverse('average-price', kwargs={"category_id": root.id})
    resp = cast(DRFResponse, client.get(url))
    assert resp.status_code == status.HTTP_200_OK
    data = cast(Dict[str, Any], resp.data)
    assert data["average_price"] == 15


def test_order_create_sends_notifications_paths(db, monkeypatch):
    user = make_user()
    client = auth_client(user)
    cat = Category.objects.create(name="Stationery")
    p1 = Product.objects.create(name="Pen", price=50, category=cat)
    p2 = Product.objects.create(name="Notebook", price=150, category=cat)

    # Monkeypatch notification functions to observe calls
    emails = {"sent": False}
    sms = {"sent": False}

    def fake_email(subject: str, message: str):  # noqa: ANN001
        emails["sent"] = True
        return True

    def fake_sms(phone_number: str, message: str):  # noqa: ANN001
        sms["sent"] = True
        return True

    monkeypatch.setattr("store.notifications.send_admin_order_email", fake_email)
    monkeypatch.setattr("store.notifications.send_sms_via_africastalking", fake_sms)

    url = reverse('order-create')
    resp = cast(DRFResponse, client.post(
        url,
        {"products": [p1.id, p2.id]},
        format='json',
    ))
    assert resp.status_code == status.HTTP_201_CREATED
    data = cast(Dict[str, Any], resp.data)
    order = Order.objects.get(id=data["id"])
    assert float(order.total) == 200.0
    assert emails["sent"] is True
    assert sms["sent"] is True


def test_bulk_upload_via_json_and_error_paths(db):
    user = make_user()
    client = auth_client(user)

    # Error when missing category
    url = reverse('product-bulk-upload')
    resp = cast(DRFResponse, client.post(url, {"products": [{"name": "X", "price": 10}]}, format='json'))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    data = cast(Dict[str, Any], resp.data)
    assert data["errors"][0]["error"].startswith("Category is required")

    # Success path creating category by name
    payload = {
        "products": [
            {"name": "A", "price": 5, "category_name": "Snacks"},
            {"name": "B", "price": 15, "category_name": "Snacks"},
        ]
    }
    resp2 = cast(DRFResponse, client.post(url, payload, format='json'))
    assert resp2.status_code == status.HTTP_201_CREATED
    data2 = cast(Dict[str, Any], resp2.data)
    assert data2["created"] == 2
    assert Category.objects.filter(name="Snacks").exists()


