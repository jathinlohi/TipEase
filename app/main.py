from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import crud, schemas
from models import Base
from database import engine

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






# Waiter Endpoints
@app.post('/waiters/')
def add_waiter(waiter: schemas.WaiterInput, db: Session = Depends(get_db)):
    return crud.create_waiter(db, waiter)

@app.get('/waiter/{waiter_id}', response_model=schemas.WaiterOutput)
def get_waiter_by_id(waiter_id: int, db: Session = Depends(get_db)):
    return crud.get_waiter_by_id(db, waiter_id)

@app.get('/waiters/{name}', response_model=schemas.WaiterOutput)
def get_waiter_by_name(name: str, db: Session = Depends(get_db)):
    return crud.get_waiter_by_name(db, name)







# Bill Endpoints
@app.post('/bills/')
def add_bill(bill: schemas.BillInput, db: Session = Depends(get_db)):
    return crud.create_bill(db, bill)

@app.get('/bills/{id}', response_model=schemas.BillOutput)
def get_bill(id: int, db: Session = Depends(get_db)):
    return crud.get_bill(db, id)

@app.post("/bills/qr")
def create_bill_with_qr(bill: schemas.BillInput, db: Session = Depends(get_db)):
    return crud.create_bill_qr(db, bill)






# Transaction Endpoints
@app.post('/transactions/')
def add_transaction(transaction: schemas.TransactionInput, db: Session = Depends(get_db)):
    return crud.create_transaction(db, transaction)

@app.get('/transactions/{id}', response_model=schemas.TransactionOutput)
def get_transaction_by_id(id: int, db: Session = Depends(get_db)):
    return crud.get_transaction_by_id(db, id)

@app.post("/bills/{bill_id}/pay")
def mark_bill_as_paid(
    bill_id: int,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    bill, transaction = crud.mark_bill_as_paid(db, bill_id, transaction_id)

    if not bill or not transaction:
        raise HTTPException(status_code=404, detail="Bill or Transaction not found")

    return {
        "message": "Bill marked as paid",
        "bill": {
            "id": bill.id,
            "status": bill.status
        },
        "transaction": {
            "id": transaction.id,
            "transaction_id": transaction.transaction_id,
            "status": transaction.status
        }
    }





# Settle Tips Endpoint
@app.post("/settle_tips/{waiter_id}")
def settle_tips_for_waiter_endpoint(waiter_id: int, db: Session = Depends(get_db)):
    return crud.settle_tips_for_waiter(db, waiter_id)

# Settle Tips Form 
@app.get("/settle_tips", response_class=HTMLResponse)
def settle_tips_form(request: Request):
    return templates.TemplateResponse("settle_tips.html", {"request": request})




# Front-End Routes
from fastapi.middleware.cors import CORSMiddleware
import base64
import json
from fastapi.responses import RedirectResponse
import uuid

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now. You can restrict it to your frontend URL later.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/waiters", response_class=HTMLResponse)
async def create_waiter_form(
    request: Request,
    name: str = Form(...),
    upi_id: str = Form(...),
    db: Session = Depends(get_db)
):
    waiter_input = schemas.WaiterInput(name=name, upi_id=upi_id)
    crud.create_waiter(db, waiter_input)
    return RedirectResponse(url="/", status_code=303)

@app.get("/tip/{waiter_id}", response_class=HTMLResponse)
def tip_page(waiter_id: int, request: Request, db: Session = Depends(get_db)):
    waiter = crud.get_waiter_by_id(db, waiter_id)
    if not waiter:
        raise HTTPException(status_code=404, detail="Waiter not found")
    return templates.TemplateResponse("tip_page.html", {"request": request, "waiter": waiter})

@app.get("/pay/{encoded_data}", response_class=HTMLResponse)
def pay_page_with_encoded_qr(
    request: Request,
    encoded_data: str,
    db: Session = Depends(get_db)
):
    try:
        decoded = base64.urlsafe_b64decode(encoded_data.encode()).decode()
        data = json.loads(decoded)
        waiter_id = data["waiter_id"]
        amount = data["amount"]
        table_no = data["table_no"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid QR data")

    waiter = crud.get_waiter_by_id(db, waiter_id)
    if not waiter:
        raise HTTPException(status_code=404, detail="Waiter not found")
    
    return templates.TemplateResponse("tip_page.html", {
        "request": request,
        "waiter": waiter,
        "table_no": table_no,
        "amount": amount
    })

@app.post("/process_payment")
def process_payment(
    waiter_id: int = Form(...),
    table_no: int = Form(...),
    amount: int = Form(...),
    tip_amount: int = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Create the bill
    bill_data = schemas.BillInput(
        waiter_id=waiter_id,
        table_no=table_no,
        amount=amount
    )
    bill = crud.create_bill(db, bill_data)

    # 2. Mock a successful UPI payment
    transaction_id = str(uuid.uuid4())  # Simulate a real payment ID

    transaction_data = schemas.TransactionInput(
        waiter_id=waiter_id,
        bill_id=bill.id,
        tip_amount=tip_amount,
        total_amount=amount + tip_amount,
        status="success",
        transaction_id=transaction_id
    )
    crud.create_transaction(db, transaction_data)

    # 3. Mark bill as paid
    crud.mark_bill_as_paid(db, bill.id, transaction_id)

    # 4. Redirect to a thank you page
    return RedirectResponse(url=f"/thankyou?tid={transaction_id}", status_code=303)

@app.get("/thankyou", response_class=HTMLResponse)
def thank_you_page(request: Request, tid: str):
    return templates.TemplateResponse("thankyou.html", {
        "request": request,
        "transaction_id": tid
    })

@app.get("/create_bill", response_class=HTMLResponse)
def create_bill_form(request: Request):
    return templates.TemplateResponse("create_bill.html", {"request": request})

@app.post("/create_bill", response_class=HTMLResponse)
def submit_bill_and_generate_qr(
    request: Request,
    waiter_id: int = Form(...),
    amount: int = Form(...),
    table_no: int = Form(...),
    db: Session = Depends(get_db)
):
    bill_data = schemas.BillInput(waiter_id=waiter_id, amount=amount, table_no=table_no)
    qr_data = crud.create_bill_qr(db, bill_data)
    return templates.TemplateResponse("create_bill.html", {
        "request": request,
        "qr_code": qr_data["qr_code_base64"]
    })
