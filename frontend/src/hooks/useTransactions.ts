// src/hooks/useTransactions.ts
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { Transaction } from '@/types'
import { useAuth } from './useAuth'

export const useTransactions = () => {
  const { user } = useAuth()
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) {
      fetchTransactions()
    }
  }, [user])

  const fetchTransactions = async () => {
    if (!user) return

    const { data, error } = await supabase
      .from('transactions')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (!error && data) {
      setTransactions(data)
    }
    setLoading(false)
  }

  const addTransaction = async (transaction: Omit<Transaction, 'id' | 'user_id' | 'created_at'>) => {
    if (!user) return { error: 'User not authenticated' }

    const { data, error } = await supabase
      .from('transactions')
      .insert([{ ...transaction, user_id: user.id }])
      .select()
      .single()

    if (!error && data) {
      setTransactions(prev => [data, ...prev])
      await updateAccountBalances(transaction)
    }

    return { data, error }
  }

  const updateAccountBalances = async (transaction: Omit<Transaction, 'id' | 'user_id' | 'created_at'>) => {
    // This would be handled by database triggers in production
    // For now, we'll update the accounts table directly
    const { error } = await supabase.rpc('update_account_balance', {
      p_user_id: user?.id,
      p_transaction_type: transaction.type,
      p_amount: transaction.amount,
      p_payment_method: transaction.payment_method,
    })

    return { error }
  }

  return {
    transactions,
    loading,
    addTransaction,
    fetchTransactions,
  }
}