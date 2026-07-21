# backend/main.py
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_offline import FastAPIOffline
from pydantic import BaseModel, EmailStr
from supabase import Client, create_client

load_dotenv()

# Initialize FastAPI app using FastAPIOffline
app = FastAPIOffline(title="IZHAR Finance Management API", version="1.0.0")

# Root path route (Fixes {"detail": "Not Found"})
@app.get("/")
def read_root():
    return {"message": "API is running"}

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://izhar-finance.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase: Optional[Client] = None

try:
    supabase = create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_KEY", "")
    )
except Exception:
    supabase = None

security = HTTPBearer()

# Models
class TransactionCreate(BaseModel):
    type: str
    category: str
    sub_category: Optional[str] = None
    amount: float
    payment_method: str
    description: Optional[str] = None
    date: str
    status: str = "completed"
    reference_id: Optional[str] = None

class InvestmentCreate(BaseModel):
    type: str
    name: str
    purchase_price: float
    current_price: float
    quantity: float
    purchase_date: str
    status: str = "active"

class BorrowCreate(BaseModel):
    type: str
    person_name: str
    amount: float
    interest_rate: Optional[float] = None
    due_date: str
    status: str = "pending"

class CreditCardCreate(BaseModel):
    name: str
    limit: float
    due_date: str
    statement_date: str

# Dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/dashboard")
async def get_dashboard(user=Depends(get_current_user)):
    try:
        response = supabase.rpc("get_dashboard_data", {"p_user_id": user.id}).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions")
async def create_transaction(transaction: TransactionCreate, user=Depends(get_current_user)):
    try:
        data = transaction.model_dump()
        data["user_id"] = user.id
        data["id"] = str(uuid.uuid4())
        
        response = supabase.table("transactions").insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions")
async def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user=Depends(get_current_user)
):
    try:
        query = supabase.table("transactions").select("*").eq("user_id", user.id)
        
        if start_date:
            query = query.gte("date", start_date)
        if end_date:
            query = query.lte("date", end_date)
        if category:
            query = query.eq("category", category)
            
        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/investments")
async def create_investment(investment: InvestmentCreate, user=Depends(get_current_user)):
    try:
        data = investment.model_dump()
        data["user_id"] = user.id
        data["id"] = str(uuid.uuid4())
        
        response = supabase.table("investments").insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/investments")
async def get_investments(user=Depends(get_current_user)):
    try:
        response = supabase.table("investments").select("*").eq("user_id", user.id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/borrow")
async def create_borrow(borrow: BorrowCreate, user=Depends(get_current_user)):
    try:
        data = borrow.model_dump()
        data["user_id"] = user.id
        data["id"] = str(uuid.uuid4())
        
        response = supabase.table("borrow").insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/borrow")
async def get_borrow(user=Depends(get_current_user)):
    try:
        response = supabase.table("borrow").select("*").eq("user_id", user.id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credit-cards")
async def create_credit_card(card: CreditCardCreate, user=Depends(get_current_user)):
    try:
        data = card.model_dump()
        data["user_id"] = user.id
        data["id"] = str(uuid.uuid4())
        data["outstanding"] = 0
        
        response = supabase.table("credit_cards").insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/credit-cards")
async def get_credit_cards(user=Depends(get_current_user)):
    try:
        response = supabase.table("credit_cards").select("*").eq("user_id", user.id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{report_type}")
async def get_report(
    report_type: str,
    start_date: str,
    end_date: str,
    user=Depends(get_current_user)
):
    try:
        response = supabase.rpc("generate_report", {
            "p_user_id": user.id,
            "p_report_type": report_type,
            "p_start_date": start_date,
            "p_end_date": end_date
        }).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/{format}")
async def export_data(
    format: str,
    start_date: str,
    end_date: str,
    user=Depends(get_current_user)
):
    try:
        response = supabase.rpc("export_transactions", {
            "p_user_id": user.id,
            "p_start_date": start_date,
            "p_end_date": end_date
        }).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)