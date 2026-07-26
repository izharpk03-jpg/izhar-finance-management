import os
import logging
from datetime import datetime
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client  # Changed from supabase_py to supabase
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="IZHAR Finance Management API",
    version="1.0.0",
    description="Production-ready finance management API"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://izhar-finance.vercel.app",
        "https://izhar-finance.netlify.app",
        "https://izhar-finance-backend.onrender.com",
        "*"  # Remove this in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
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

# ============ Models ============
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

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    currency: Optional[str] = None
    theme: Optional[str] = None

# ============ Authentication ============
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

# ============ Health Check ============
@app.get("/")
async def root():
    return {
        "message": "IZHAR Finance Management API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    try:
        # Test Supabase connection
        supabase.table("profiles").select("count").limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============ Dashboard ============
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

# ============ Transactions ============
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
    type: Optional[str] = None,
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
        if type:
            query = query.eq("type", type)
            
        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Transactions fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, user=Depends(get_current_user)):
    try:
        response = supabase.table("transactions") \
            .delete() \
            .eq("id", transaction_id) \
            .eq("user_id", user.id) \
            .execute()
        
        if response.data:
            return {"message": "Transaction deleted successfully"}
        raise HTTPException(status_code=404, detail="Transaction not found")
    except Exception as e:
        logger.error(f"Transaction deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Investments ============
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

@app.put("/api/investments/{investment_id}")
async def update_investment(investment_id: str, investment: InvestmentCreate, user=Depends(get_current_user)):
    try:
        data = investment.dict()
        data["updated_at"] = datetime.now().isoformat()
        
        response = supabase.table("investments") \
            .update(data) \
            .eq("id", investment_id) \
            .eq("user_id", user.id) \
            .execute()
        
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Investment not found")
    except Exception as e:
        logger.error(f"Investment update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Borrow ============
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
async def get_borrow(
    type: Optional[str] = None,
    status: Optional[str] = None,
    user=Depends(get_current_user)
):
    try:
        query = supabase.table("borrow").select("*").eq("user_id", user.id)
        
        if type:
            query = query.eq("type", type)
        if status:
            query = query.eq("status", status)
            
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Borrow fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/borrow/{borrow_id}")
async def update_borrow(borrow_id: str, borrow: BorrowCreate, user=Depends(get_current_user)):
    try:
        data = borrow.dict()
        data["updated_at"] = datetime.now().isoformat()
        
        response = supabase.table("borrow") \
            .update(data) \
            .eq("id", borrow_id) \
            .eq("user_id", user.id) \
            .execute()
        
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Borrow record not found")
    except Exception as e:
        logger.error(f"Borrow update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Credit Cards ============
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

@app.delete("/api/credit-cards/{card_id}")
async def delete_credit_card(card_id: str, user=Depends(get_current_user)):
    try:
        response = supabase.table("credit_cards") \
            .delete() \
            .eq("id", card_id) \
            .eq("user_id", user.id) \
            .execute()
        
        if response.data:
            return {"message": "Credit card deleted successfully"}
        raise HTTPException(status_code=404, detail="Credit card not found")
    except Exception as e:
        logger.error(f"Credit card deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Profile ============
@app.get("/api/profile")
async def get_profile(user=Depends(get_current_user)):
    try:
        response = supabase.table("profiles").select("*").eq("id", user.id).execute()
        if response.data:
            return response.data[0]
        
        # Create profile if doesn't exist
        profile_data = {
            "id": user.id,
            "full_name": user.user_metadata.get("full_name", ""),
            "currency": "USD",
            "theme": "dark",
            "created_at": datetime.now().isoformat()
        }
        response = supabase.table("profiles").insert(profile_data).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/profile")
async def update_profile(profile: ProfileUpdate, user=Depends(get_current_user)):
    try:
        data = {k: v for k, v in profile.dict().items() if v is not None}
        data["updated_at"] = datetime.now().isoformat()
        
        response = supabase.table("profiles") \
            .update(data) \
            .eq("id", user.id) \
            .execute()
        
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Profile not found")
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Reports ============
@app.get("/api/reports/summary")
async def get_summary_report(
    start_date: str,
    end_date: str,
    user=Depends(get_current_user)
):
    try:
        # Get transactions within date range
        response = supabase.table("transactions") \
            .select("*") \
            .eq("user_id", user.id) \
            .gte("date", start_date) \
            .lte("date", end_date) \
            .execute()
        
        transactions = response.data if response.data else []
        
        # Calculate summary
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net": total_income - total_expenses,
            "transaction_count": len(transactions)
        }
    except Exception as e:
        logger.error(f"Report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Main Entry Point ============
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENV") == "development" else False
    )