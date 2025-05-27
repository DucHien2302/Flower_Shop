from sqlalchemy.orm import Session
from models.models_db import Invoices
from sqlalchemy import text
from fastapi import HTTPException

def add_invoice(
    db: Session,
    cart_id: str,
    user_id: int,
    invoice_id: str,
):
    try:
        db.execute(text("SET @p_Amount := 0"))
        db.execute(
            text("CALL AddInvoice(:p_CartId, :p_UserId, :p_InvoiceId, @p_Amount)"),
            {
                "p_CartId": cart_id,
                "p_UserId": user_id,
                "p_InvoiceId": invoice_id
            }
        )

        result = db.execute(text("SELECT @p_Amount AS amount")).fetchone()
        amount = result[0] if result else 0

        invoice = db.query(Invoices).filter_by(InvoiceId=invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        invoice.Price = amount
        invoice.Amount = amount - invoice.Discount
        db.commit()
        db.refresh(invoice)
        
        return invoice

    except Exception as e:
        print(f"Error: {e}")  # debug log
        raise HTTPException(status_code=500, detail="Internal Server Error")