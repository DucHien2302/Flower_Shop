from fastapi import APIRouter, Depends, HTTPException, Cookie, Request
import uuid
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
    session_id: str = Cookie(None),
):
    try:
        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID not found")
        if session_id not in sessions:
            raise HTTPException(status_code=400, detail="Session ID is invalid")        
        user_id = sessions[session_id]
        invoice_id = str(uuid.uuid4()).replace("-", "")
        invoice_item = add_invoice(db, session_id, user_id, invoice_id)
        if invoice_item is None:
            raise HTTPException(status_code=400, detail="Failed to add invoice item")
        # Call the payment service
        payment_url = to_url(invoice_item, request.client.host)
        if payment_url is None:
            raise HTTPException(status_code=400, detail="Failed to create payment URL")
        return {"payment_url": payment_url}
    except Exception:
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