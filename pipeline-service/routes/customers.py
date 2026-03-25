from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models.customer import Customer

router = APIRouter()


def serialize_customer(customer: Customer):
    return {
        "customer_id": customer.customer_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "date_of_birth": customer.date_of_birth.isoformat() if customer.date_of_birth else None,
        "account_balance": float(customer.account_balance) if isinstance(customer.account_balance, Decimal) else customer.account_balance,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
    }


@router.get("/api/customers")
def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit
    total = db.scalar(select(func.count()).select_from(Customer))
    customers = db.scalars(
        select(Customer)
        .order_by(Customer.customer_id)
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "data": [serialize_customer(customer) for customer in customers],
        "total": total or 0,
        "page": page,
        "limit": limit,
    }


@router.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return serialize_customer(customer)
