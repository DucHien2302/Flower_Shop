from datetime import datetime
from pydantic import BaseModel

class PaymentResponse(BaseModel):
    vnp_Amount: int
    vnp_BankCode: str
    vnp_BankTranNo: str
    vnp_CardType: str
    vnp_OrderInfo: str
    vnp_PayDate: datetime
    vnp_ResponseCode: str
    vnp_TmnCode: str
    vnp_TransactionNo: str
    vnp_TransactionStatus: str
    vnp_TxnRef: str
    # vnp_SecureHash: str