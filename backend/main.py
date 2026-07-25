from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="IZHAR Finance Management API", version="1.0.0")

# CORS configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    raise

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
    limit_amount: float
    due_date: str
    statement_date: str

# Dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return user.user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# Routes
@app.get("/")
async def root():
    return {"message": "IZHAR Finance Management API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/dashboard")
async def get_dashboard(user=Depends(get_current_user)):
    try:
        response = supabase.rpc("get_dashboard_data", {"p_user_id": user.id}).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return {}
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions")
async def create_transaction(transaction: TransactionCreate, user=Depends(get_current_user)):
    try:
        data = transaction.dict()
        data["user_id"] = user.id
        data["id"] = str(uuid.uuid4())
        data["created_at"] = datetime.now().isoformat()
        
        response = supabase.table("transactions").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Failed to create transaction")
    except Exception as e:
        logger.error(f"Transaction creation error: {e}")
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
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Transactions fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/investments")
async def create_investment(investment: InvestmentCreate, user=Depends(get_current_user)):
    try:
        data = investment.dict()
        data["user_id"] = user.id
        data["id"] = str(uuid.uuid4())
        data["created_at"] = datetime.now().isoformat()
        
        response = supabase.table("investments").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Failed to create investment")
    except Exception as e:
        logger.error(f"Investment creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/investments")
async def get_investments(user=Depends(get_current_user)):
    try:
        response = supabase.table("investments").select("*").eq("user_id", user.id).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Investments fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/borrow")
async def create_borrow(borrow: BorrowCreate, user=Depends(get_current_user)):
    try:
        data = borrow.dict()
        data["user_id"] = user.id
        data["id"] = str(uuid.uuid4())
        data["created_at"] = datetime.now().isoformat()
        
        response = supabase.table("borrow").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Failed to create borrow record")
    except Exception as e:
        logger.error(f"Borrow creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/borrow")
async def get_borrow(user=Depends(get_current_user)):
    try:
        response = supabase.table("borrow").select("*").eq("user_id", user.id).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Borrow fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credit-cards")
async def create_credit_card(card: CreditCardCreate, user=Depends(get_current_user)):
    try:
        data = card.dict()
        data["user_id"] = user.id
        data["id"] = str(uuid.uuid4())
        data["outstanding"] = 0
        data["created_at"] = datetime.now().isoformat()
        
        response = supabase.table("credit_cards").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Failed to create credit card")
    except Exception as e:
        logger.error(f"Credit card creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/credit-cards")
async def get_credit_cards(user=Depends(get_current_user)):
    try:
        response = supabase.table("credit_cards").select("*").eq("user_id", user.id).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Credit cards fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)