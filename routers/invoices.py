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
    session_id: str = Cookie(None)
):
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID not found")
    
    user_id = sessions.get(session_id)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    invoice_id = str(uuid.uuid4()).replace("-", "")

    try:
        
        invoice = add_invoice(db, session_id, user_id, invoice_id)
        # Tạo đường dẫn thanh toán
        payment_url = to_url(invoice, request.client.host)
        if not payment_url:
            raise HTTPException(status_code=400, detail="Failed to create payment URL")

        return {"payment_url": payment_url}

    except Exception as e:
        print(f"Error: {e}")  # debug log
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/vnpaymentresponse")
async def vnpayment_response(
    vnp_Amount: str = None,
    vnp_BankCode: str = None,
    vnp_BankTranNo: str = None,
    vnp_CardType: str = None,
    vnp_OrderInfo: str = None,
    vnp_PayDate: str = None,
    vnp_ResponseCode: str = None,
    vnp_TmnCode: str = None,
    vnp_TransactionNo: str = None,
    vnp_TransactionStatus: str = None,
    vnp_TxnRef: str = None,
    vnp_SecureHash: str = None,
    db: Session = Depends(get_db),
):
    try:
        if vnp_ResponseCode != "00":
            raise HTTPException(status_code=400, detail="Payment failed")

        payment_response = PaymentResponse(
            vnp_Amount=vnp_Amount,
            vnp_BankCode=vnp_BankCode,
            vnp_BankTranNo=vnp_BankTranNo,
            vnp_CardType=vnp_CardType,
            vnp_OrderInfo=vnp_OrderInfo,
            vnp_PayDate=vnp_PayDate,
            vnp_ResponseCode=vnp_ResponseCode,
            vnp_TmnCode=vnp_TmnCode,
            vnp_TransactionNo=vnp_TransactionNo,
            vnp_TransactionStatus=vnp_TransactionStatus,
            vnp_TxnRef=vnp_TxnRef,
            vnp_SecureHash=vnp_SecureHash
        )

        invoice_item = db.query(Invoices).filter(Invoices.InvoiceId == vnp_TxnRef).first()
        if invoice_item is None:
            raise HTTPException(status_code=400, detail="Invoice not found")
        invoice_item.Status = 1
        db.commit()
        db.refresh(invoice_item)

        payment_item = add_vnpayment(db, payment_response)
        if payment_item is None:
            raise HTTPException(status_code=400, detail="Failed to add payment item")
        return payment_item
    except Exception as e:
        print(f"Error in payment response: {str(e)}")  # Thêm log chi tiết lỗi
        raise HTTPException(status_code=500, detail="Internal Server Error")