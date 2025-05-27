from fastapi import APIRouter, Depends, HTTPException, Cookie, Request
import uuid
from sqlalchemy.orm import Session
from config.db import get_db
from controller.invoices import add_invoice
from controller.vnpayment import add_vnpayment
from models.models_db import Invoices, SysUser, InvoiceDetails, Products, Informations
from schemas.payment import PaymentResponse
from services.vnpaymentservices import to_url
from globals import sessions
from datetime import datetime

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
        # Kiểm tra mã phản hồi
        if vnp_ResponseCode != "00":
            raise HTTPException(status_code=400, detail=f"Payment failed with code: {vnp_ResponseCode}")

        # TODO: Thêm xác thực SecureHash để đảm bảo request đến từ VNPay
        # is_valid_hash = verify_secure_hash(...)
        # if not is_valid_hash:
        #     raise HTTPException(status_code=400, detail="Invalid secure hash")
        
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

        # Tìm hóa đơn
        invoice_item = db.query(Invoices).filter(Invoices.InvoiceId == vnp_TxnRef).first()
        if invoice_item is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Kiểm tra số tiền
        payment_amount = int(vnp_Amount) / 100  # VNPay trả về số tiền x100
        if payment_amount != float(invoice_item.Amount):
            raise HTTPException(
                status_code=400, 
                detail=f"Payment amount mismatch: {payment_amount} vs {invoice_item.Amount}"
            )
        
        # Cập nhật trạng thái hóa đơn
        invoice_item.Status = 1
        db.commit()
        db.refresh(invoice_item)

        # Lưu thông tin thanh toán
        payment_item = add_vnpayment(db, payment_response)
        if payment_item is None:
            raise HTTPException(status_code=500, detail="Failed to record payment")
        
        # Lấy thông tin người dùng
        user = db.query(SysUser).filter(SysUser.id == invoice_item.UserId).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        info = db.query(Informations).filter(Informations.UserId == user.id).first()
        if info is None:
            raise HTTPException(status_code=404, detail="User information not found")
        
        # Lấy chi tiết hóa đơn
        invoice_details = db.query(
            InvoiceDetails, 
            Products.Name,
            Products.Price
        ).join(
            Products, InvoiceDetails.ProductId == Products.id
        ).filter(
            InvoiceDetails.InvoiceId == invoice_item.InvoiceId
        ).all()
        
        # Chuẩn bị thông tin phản hồi
        user_info = {
            "user_id": user.id,
            "email": user.Email,
            "full_name": info.FullName,
            "gender": info.Gender,
            "date_of_birth": info.DateOfBirth.strftime("%d-%m-%Y"),
            "address": info.Address,
        }
        
        invoice_info = {
            "invoice_id": invoice_item.InvoiceId,
            "date": invoice_item.CreateAt.strftime("%d-%m-%Y %H:%M:%S"),
            "total_amount": invoice_item.Amount,
            "status": "Đã thanh toán",
            "items": [
                {
                    "product_name": item[1],
                    "quantity": item[0].Quantity,
                    "price": item[2],
                    "total": item[0].Quantity * item[2]
                }
                for item in invoice_details
            ]
        }
        
        # Xử lý ngày thanh toán
        payment_date = None
        if vnp_PayDate:
            try:
                payment_date = datetime.strptime(vnp_PayDate, "%Y%m%d%H%M%S").strftime("%d/%m/%Y %H:%M:%S")
            except ValueError as e:
                print(f"Invalid payment date format: {vnp_PayDate}, error: {str(e)}")
        
        payment_info = {
            "payment_id": payment_item.TxnRef,
            "payment_date": payment_date,
            "bank_code": vnp_BankCode,
            "card_type": vnp_CardType,
            "transaction_no": vnp_TransactionNo
        }
        
        return {
            "status": "success",
            "message": "Payment successful",
            "user_info": user_info,
            "invoice_info": invoice_info,
            "payment_info": payment_info
        }
    except HTTPException as e:
        # Giữ nguyên các HTTP exception đã tạo
        raise e
    except ValueError as e:
        # Xử lý lỗi chuyển đổi dữ liệu
        print(f"Data conversion error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format")
    except Exception as e:
        # Xử lý các lỗi khác
        print(f"Error in payment response: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")