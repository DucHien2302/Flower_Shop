from fastapi import APIRouter, Depends, HTTPException, Cookie, Request
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session
from config.db import get_db
from controller.invoices import add_invoice
from controller.vnpayment import add_vnpayment
from models.models_db import Invoices
from schemas.payment import PaymentResponse
from services.vnpaymentservices import to_url
from globals import sessions

router = APIRouter(
    prefix="/invoices",
)

@router.post("/payment")
async def add_invoice_item(
    request: Request,
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID not found")
    
    user_id = sessions.get(session_id)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    invoice_id = str(uuid.uuid4()).replace("-", "")

    try:
        # Thiết lập biến output cho stored procedure
        db.execute(text("SET @p_Amount := 0"))

        # Gọi stored procedure AddInvoice
        db.execute(
            text("CALL AddInvoice(:p_CartId, :p_UserId, :p_InvoiceId, @p_Amount)"),
            {
                "p_CartId": session_id,
                "p_UserId": user_id,
                "p_InvoiceId": invoice_id
            }
        )
        print("p_CartId: ", session_id)
        print("p_UserId: ", user_id)
        print("p_InvoiceId: ", invoice_id)

        # Lấy số tiền tính từ stored procedure
        result = db.execute(text("SELECT @p_Amount AS amount")).fetchone()
        amount = result[0] if result else 0

        print("amount", amount)

        # Cập nhật hoá đơn trong bảng
        invoice = db.query(Invoices).filter_by(InvoiceId=invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        invoice.Price = amount
        db.commit()
        db.refresh(invoice)

        # Tạo đường dẫn thanh toán
        payment_url = to_url(invoice, request.client.host)
        if not payment_url:
            raise HTTPException(status_code=400, detail="Failed to create payment URL")

        return {"payment_url": payment_url}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/vnpaymentresponse")
async def vnpayment_response(
    item: PaymentResponse,
    db: Session = Depends(get_db),
):
    try:
        if item.vnp_ResponseCode != "00":
            raise HTTPException(status_code=400, detail="Payment failed")
        invoice_item = db.query(Invoices).filter(Invoices.InvoiceId == item.vnp_TxnRef).first()
        if invoice_item is None:
            raise HTTPException(status_code=400, detail="Invoice not found")
        invoice_item.Status = 1
        db.commit()
        db.refresh(invoice_item)
        # Call the payment service
        payment_item = add_vnpayment(db, item)
        if payment_item is None:
            raise HTTPException(status_code=400, detail="Failed to add payment item")
        return payment_item
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")