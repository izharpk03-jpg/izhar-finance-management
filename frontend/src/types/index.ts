// src/types/index.ts
export interface User {
  id: string
  email: string
  full_name: string
  avatar_url?: string
  currency: string
  theme: 'light' | 'dark'
  created_at: string
}

export interface Transaction {
  id: string
  user_id: string
  type: 'income' | 'expense' | 'investment' | 'borrow_given' | 'borrow_taken' | 'transfer' | 'savings'
  category: string
  sub_category?: string
  amount: number
  payment_method: string
  description?: string
  date: string
  status: 'pending' | 'completed' | 'cancelled'
  reference_id?: string
  created_at: string
}

export interface Account {
  id: string
  user_id: string
  type: 'cash' | 'bank' | 'savings'
  name: string
  balance: number
  currency: string
  created_at: string
}

export interface Investment {
  id: string
  user_id: string
  type: string
  name: string
  purchase_price: number
  current_price: number
  quantity: number
  purchase_date: string
  status: 'active' | 'sold' | 'matured'
  created_at: string
}

export interface Borrow {
  id: string
  user_id: string
  type: 'given' | 'taken'
  person_name: string
  amount: number
  interest_rate?: number
  due_date: string
  status: 'pending' | 'partial' | 'completed' | 'overdue'
  created_at: string
}

export interface CreditCard {
  id: string
  user_id: string
  name: string
  limit: number
  outstanding: number
  due_date: string
  statement_date: string
  created_at: string
}

export interface DashboardData {
  total_balance: number
  cash_balance: number
  bank_balance: number
  total_income: number
  total_expenses: number
  total_investments: number
  borrow_given: number
  borrow_taken: number
  credit_card_outstanding: number
  savings: number
  monthly_profit: number
  monthly_loss: number
  net_worth: number
  today_income: number
  today_expenses: number
  pending_borrow_collection: number
  upcoming_payments: number
}