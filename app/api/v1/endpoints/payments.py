from fastapi import APIRouter, Depends, HTTPException, Request
from app.core import db
from app.core.utility import default_response
from app.core.book_utility import confirm_booking
from app.core.security import get_current_user
from app.core.db import SessionLocal
from app.core.utility import redis_client

import uuid
import json
import hmac
import hashlib
import json
from app.models.booking import Payment
from app.models.user import User
from app.models.booking import Ticket
# from datetime import datetime, time
from app.core.config import settings
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import json
import razorpay
import hmac
import hashlib
from fastapi import HTTPException
from app.core.config import settings




router = APIRouter()

client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))

# step 1: user clicks "pay" on frontend
@router.post("/create")
def create_payment(
    reservation_id: str,
    request: Request,
    current_user = Depends(get_current_user)
):
    """
    call this API to create a payment order on Razorpay and get the order_id and other details. This is not confirming anything yet, just creating an order/payment intent on Razorpay and storing it in our DB with status PENDING.
    """
    db = SessionLocal()

    try:
        # 1. Fetch reservation from Redis
        reservation_key = f"reservation:{reservation_id}"
        reserved_data = redis_client.get(reservation_key)

        if not reserved_data:
            raise HTTPException(status_code=400, detail="Reservation expired")

        data = json.loads(reserved_data)

        # 2. Validate ownership
        if data["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized reservation")

        ticket_id = data["ticket_id"]

        # 3. Fetch ticket
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        amount = int(ticket.price * 100)  # paise

        # 4. Create Razorpay Order: A payment intent/order on Razorpay
        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })
        # order = {
        #             "id": f"order_{uuid.uuid4().hex[:12]}",
        #             "entity": "order",
        #             "amount": amount,
        #             "amount_paid": 0,
        #             "amount_due": amount,
        #             "currency": "INR",
        #             "receipt": None,
        #             "status": "created",
        #             "attempts": 0,
        #             # "created_at": int(time.time())
        #         }

        # 5. Store payment in DB
        payment = Payment(
            user_id=current_user.id,
            ticket_id=ticket_id,
            reservation_id=reservation_id,
            amount=amount,
            payment_gateway="razorpay",
            gateway_order_id=order["id"],
            status="PENDING"
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        # 6. Return response
        return default_response(
            data={
                "payment_id": payment.id,
                "order_id": order["id"],
                "amount": amount,
                "currency": "INR",
                "key": "RAZORPAY_KEY"
            },
            message="Payment order created",
            request=request
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

# Step 2: User pays on Razorpay UI
# step 3: Razorpay processes payment -> If sucess, money is deducted
# step 4: a. frontend callback (not trusted) --> Processing message. b. webhook to our backend
@router.get("/pay/{order_id}", response_class=HTMLResponse)
def pay_page(order_id: str, request: Request):
    """
    Serve Razorpay payment page
    """
    # Here, fetch payment info from DB
    db = SessionLocal()
    payment = db.query(Payment).filter(Payment.gateway_order_id == order_id).first()
    db.close()

    if not payment:
        return HTMLResponse("<h1>Payment not found</h1>", status_code=404)

    # Inject Razorpay info into HTML
    html_content = f"""
    <html>
    <head>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    </head>
    <body>
        <h2>Pay ₹{payment.amount/100} for your ticket</h2>
        <button id="pay-btn">Pay Now</button>

        <script>
            var options = {{
                "key": "{settings.RAZORPAY_KEY}",  // Razorpay test key
                "amount": {payment.amount}, // in paise
                "currency": "INR",
                "name": "Ticket Booking",
                "description": "Ticket for event",
                "order_id": "{payment.gateway_order_id}",
                "handler": function (response){{
                    alert("Payment done! Payment ID: " + response.razorpay_payment_id);
                    // optional: call your backend to check status
                }}
            }};

            document.getElementById("pay-btn").onclick = function(e){{
                var rzp = new Razorpay(options);
                rzp.open();
                e.preventDefault();
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html_content)

@router.post("/webhook")
async def payment_webhook(request: Request):
    # --------------------------
    # Simulated/test request body
    # --------------------------
    body = json.dumps({
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test123",
                    "order_id": "order_ST2sHdUFKsjtDU"
                }
            }
        }
    }).encode("utf-8")

    # Simulated signature for testing
    signature = hmac.new(
        b"RAZORPAY_WEBHOOK_SECRET",  # replace with your secret
        body,
        hashlib.sha256
    ).hexdigest()

    # --------------------------
    # Original code for real requests (commented out)
    # --------------------------
    # body = await request.body()
    # signature = request.headers.get("X-Razorpay-Signature")

    # Verify signature
    generated_signature = hmac.new(
        b"RAZORPAY_WEBHOOK_SECRET",
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = json.loads(body)
    event = payload.get("event")

    if event != "payment.captured":
        return {"status": "ignored"}

    payment_entity = payload["payload"]["payment"]["entity"]

    order_id = payment_entity["order_id"]
    payment_id = payment_entity["id"]

    db = SessionLocal()

    try:
        payment = db.query(Payment).filter(
            Payment.gateway_order_id == order_id
        ).first()

        if not payment:
            return {"status": "payment_not_found"}

        if payment.status == "SUCCESS":
            return {"status": "already_processed"}

        payment.status = "SUCCESS"
        payment.gateway_payment_id = payment_id
        db.commit()

        reservation_key = f"reservation:{payment.reservation_id}"
        reserved_data = redis_client.get(reservation_key)

        if not reserved_data:
            payment.status = "REFUND_REQUIRED"
            db.commit()
            return {"status": "reservation_expired"}

        data = json.loads(reserved_data)

        ticket = db.query(Ticket).filter(
            Ticket.id == data["ticket_id"]
        ).first()

        user = db.query(User).filter(
            User.id == data["user_id"]
        ).first()

        confirm_booking(db, ticket, user, reservation_key)

        return {"status": "success"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()