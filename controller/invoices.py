from sqlalchemy.orm import Session
from models.models_db import Invoices
from sqlalchemy import text

def add_invoice(
    db: Session,
    cart_id: str,
    user_id: int,
    invoice_id: str,
):
    amount_str = text("SET @amount := 0")
    db.execute(amount_str)
    sql = text("CALL AddInvoice(:cart_id, :invoice_id, :user_id, @amount)")
    db.execute(sql, {
        "cart_id": cart_id,
        "invoice_id": invoice_id,
        "user_id": user_id
    })
    # Lấy giá trị amount từ biến session
    get_amount = text("SELECT @amount as amount")
    amount_result = db.execute(get_amount).fetchone()
    amount = amount_result['amount'] if amount_result else 0

    # Cập nhật trường price của Invoices
    invoice_item = db.query(Invoices).filter(Invoices.InvoiceId == invoice_id).first()
    invoice_item.Price = amount
    db.add(invoice_item)
    db.commit()
    db.refresh(invoice_item)
    return invoice_item