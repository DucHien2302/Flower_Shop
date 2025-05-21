from sqlalchemy.orm import Session
from models.models import VnPayment
from schemas.payment import PaymentResponse

def add_vnpayment(
    db: Session,
    item: PaymentResponse,
) -> VnPayment:
    payment = VnPayment(
        TxnRef = item.vnp_TxnRef,
        TmnCode = item.vnp_TmnCode,
        Amount = item.vnp_Amount,
        BankCode = item.vnp_BankCode,
        BankTranNo = item.vnp_BankTranNo,
        CardType = item.vnp_CardType,
        OrderInfo = item.vnp_OrderInfo,
        PayDate = item.vnp_PayDate,
        ResponseCode = item.vnp_ResponseCode,
        TransactionNo = item.vnp_TransactionNo,
        TransactionStatus = item.vnp_TransactionStatus,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
