from sqlalchemy.orm import Session
from models.models_db import Invoices
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

def add_invoice(
    db: Session,
    cart_id: str,
    user_id: int,
    invoice_id: str,
):
    try:
        # Khởi tạo biến amount
        db.execute(text("SET @amount := 0"))

        # Gọi stored procedure
        db.execute(
            text("CALL AddInvoice(:cart_id, :invoice_id, :user_id, @amount)"),
            {
                "cart_id": cart_id,
                "invoice_id": invoice_id,
                "user_id": user_id
            }
        )

        # Lấy giá trị từ biến output
        amount_result = db.execute(text("SELECT @amount as amount")).fetchone()
        amount = amount_result['amount'] if amount_result and 'amount' in amount_result else 0

        # Tìm và cập nhật hóa đơn
        invoice_item = db.query(Invoices).filter(Invoices.InvoiceId == invoice_id).first()
        if not invoice_item:
            raise HTTPException(status_code=404, detail="Invoice not found")

        invoice_item.Price = amount
        db.add(invoice_item)
        db.commit()
        db.refresh(invoice_item)
        return invoice_item

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
