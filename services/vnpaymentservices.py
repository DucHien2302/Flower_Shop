import urllib.parse
from collections import OrderedDict
import hmac
import hashlib
from globals import payment
from models.models import Invoices

def hmac_sha512(key, data):
    return hmac.new(key.encode(), data.encode(), hashlib.sha512).hexdigest()

def to_url(obj: Invoices, client_id: str) -> str:
    """
    Convert an Invoice object and payment config to a VNPay URL.
    """
    params = OrderedDict([
        ("vnp_Amount", str(int(obj.Amount * 100))),
        ("vnp_Command", payment["vnp_Command"]),
        ("vnp_CreateDate", obj.CreateAt.strftime("%Y%m%d%H%M%S")),
        ("vnp_CurrCode", payment["vnp_CurrCode"]),
        ("vnp_IpAddr", client_id),
        ("vnp_Locale", payment["vnp_Locale"]),
        ("vnp_OrderInfo", f"Payment for {obj.InvoiceId} with amount {obj.Amount}"),
        ("vnp_OrderType", payment["vnp_OrderType"]),
        ("vnp_ReturnUrl", payment["vnp_ReturnUrl"]),
        ("vnp_TmnCode", payment["vnp_TmnCode"]),
        ("vnp_TxnRef", obj.InvoiceId),
        ("vnp_Version", payment["vnp_Version"]),
    ])
    query = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in params.items())
    secure_hash = hmac_sha512(payment["vnp_HashSecret"], query)
    return f"{payment["vnp_Url"]}?{query}&vnp_SecureHash={secure_hash}"