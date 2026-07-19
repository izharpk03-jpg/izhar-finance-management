-- database/schema.sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    avatar_url TEXT,
    currency VARCHAR(3) DEFAULT 'USD',
    theme VARCHAR(10) DEFAULT 'dark',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Accounts table
CREATE TABLE public.accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('cash', 'bank', 'savings')),
    name VARCHAR(100) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions table
CREATE TABLE public.transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense', 'investment', 'borrow_given', 'borrow_taken', 'transfer', 'savings')),
    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50),
    amount DECIMAL(15,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('cash', 'bank', 'credit_card', 'debit_card', 'upi', 'cheque', 'online_transfer', 'wallet')),
    description TEXT,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'cancelled')),
    reference_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Investments table
CREATE TABLE public.investments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('gold', 'silver', 'stocks', 'crypto', 'mutual_funds', 'business', 'property', 'savings_certificate', 'fd', 'other')),
    name VARCHAR(100) NOT NULL,
    purchase_price DECIMAL(15,2) NOT NULL,
    current_price DECIMAL(15,2) NOT NULL,
    quantity DECIMAL(15,4) NOT NULL,
    purchase_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'sold', 'matured')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Borrow table
CREATE TABLE public.borrow (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    type VARCHAR(10) NOT NULL CHECK (type IN ('given', 'taken')),
    person_name VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2),
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'partial', 'completed', 'overdue')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Credit Cards table
CREATE TABLE public.credit_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    limit_amount DECIMAL(15,2) NOT NULL,
    outstanding DECIMAL(15,2) DEFAULT 0,
    due_date DATE NOT NULL,
    statement_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table
CREATE TABLE public.categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense', 'investment', 'borrow', 'savings')),
    name VARCHAR(50) NOT NULL,
    icon VARCHAR(50),
    color VARCHAR(7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_transactions_user_id ON public.transactions(user_id);
CREATE INDEX idx_transactions_date ON public.transactions(date);
CREATE INDEX idx_transactions_type ON public.transactions(type);
CREATE INDEX idx_transactions_category ON public.transactions(category);
CREATE INDEX idx_investments_user_id ON public.investments(user_id);
CREATE INDEX idx_borrow_user_id ON public.borrow(user_id);
CREATE INDEX idx_credit_cards_user_id ON public.credit_cards(user_id);

-- Triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON public.accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON public.transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_investments_updated_at BEFORE UPDATE ON public.investments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_borrow_updated_at BEFORE UPDATE ON public.borrow FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_credit_cards_updated_at BEFORE UPDATE ON public.credit_cards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update account balances
CREATE OR REPLACE FUNCTION update_account_balance(
    p_user_id UUID,
    p_transaction_type VARCHAR,
    p_amount DECIMAL,
    p_payment_method VARCHAR
)
RETURNS VOID AS $$
BEGIN
    -- Update cash balance
    IF p_payment_method = 'cash' THEN
        IF p_transaction_type IN ('income', 'borrow_taken', 'investment_sale') THEN
            UPDATE accounts SET balance = balance + p_amount 
            WHERE user_id = p_user_id AND type = 'cash';
        ELSIF p_transaction_type IN ('expense', 'investment_purchase', 'borrow_given', 'transfer_out') THEN
            UPDATE accounts SET balance = balance - p_amount 
            WHERE user_id = p_user_id AND type = 'cash';
        END IF;
    END IF;

    -- Update bank balance
    IF p_payment_method = 'bank' OR p_payment_method = 'online_transfer' THEN
        IF p_transaction_type IN ('income', 'borrow_taken', 'investment_sale', 'transfer_in') THEN
            UPDATE accounts SET balance = balance + p_amount 
            WHERE user_id = p_user_id AND type = 'bank';
        ELSIF p_transaction_type IN ('expense', 'investment_purchase', 'borrow_given', 'transfer_out') THEN
            UPDATE accounts SET balance = balance - p_amount 
            WHERE user_id = p_user_id AND type = 'bank';
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to get dashboard data
CREATE OR REPLACE FUNCTION get_dashboard_data(p_user_id UUID)
RETURNS TABLE (
    total_balance DECIMAL,
    cash_balance DECIMAL,
    bank_balance DECIMAL,
    total_income DECIMAL,
    total_expenses DECIMAL,
    total_investments DECIMAL,
    borrow_given DECIMAL,
    borrow_taken DECIMAL,
    credit_card_outstanding DECIMAL,
    savings DECIMAL,
    monthly_profit DECIMAL,
    monthly_loss DECIMAL,
    net_worth DECIMAL,
    today_income DECIMAL,
    today_expenses DECIMAL,
    pending_borrow_collection DECIMAL,
    upcoming_payments DECIMAL
) AS $$
BEGIN
    -- Get account balances
    SELECT 
        COALESCE(SUM(CASE WHEN type = 'cash' THEN balance ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN type = 'bank' THEN balance ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN type = 'savings' THEN balance ELSE 0 END), 0)
    INTO cash_balance, bank_balance, savings
    FROM accounts
    WHERE user_id = p_user_id;

    -- Get total income and expenses for current month
    SELECT 
        COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0)
    INTO total_income, total_expenses
    FROM transactions
    WHERE user_id = p_user_id 
    AND date >= DATE_TRUNC('month', CURRENT_DATE)
    AND status = 'completed';

    -- Get today's income and expenses
    SELECT 
        COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0)
    INTO today_income, today_expenses
    FROM transactions
    WHERE user_id = p_user_id 
    AND date = CURRENT_DATE
    AND status = 'completed';

    -- Get borrow amounts
    SELECT 
        COALESCE(SUM(CASE WHEN type = 'given' THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN type = 'taken' THEN amount ELSE 0 END), 0)
    INTO borrow_given, borrow_taken
    FROM borrow
    WHERE user_id = p_user_id 
    AND status IN ('pending', 'partial');

    -- Get total investments
    SELECT COALESCE(SUM(current_price * quantity), 0)
    INTO total_investments
    FROM investments
    WHERE user_id = p_user_id 
    AND status = 'active';

    -- Get credit card outstanding
    SELECT COALESCE(SUM(outstanding), 0)
    INTO credit_card_outstanding
    FROM credit_cards
    WHERE user_id = p_user_id;

    -- Calculate totals
    total_balance := cash_balance + bank_balance;
    net_worth := total_balance + total_investments - credit_card_outstanding;
    monthly_profit := total_income - total_expenses;

    -- Get pending borrow collection
    SELECT COALESCE(SUM(amount), 0)
    INTO pending_borrow_collection
    FROM borrow
    WHERE user_id = p_user_id 
    AND type = 'given' 
    AND status IN ('pending', 'partial')
    AND due_date < CURRENT_DATE + INTERVAL '7 days';

    -- Get upcoming payments (borrow taken due within 7 days)
    SELECT COALESCE(SUM(amount), 0)
    INTO upcoming_payments
    FROM borrow
    WHERE user_id = p_user_id 
    AND type = 'taken' 
    AND status IN ('pending', 'partial')
    AND due_date < CURRENT_DATE + INTERVAL '7 days'
    AND due_date >= CURRENT_DATE;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;