// src/components/TransactionForm.tsx
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { useTransactions } from '@/hooks/useTransactions'
import { toast } from 'sonner'

const transactionSchema = z.object({
  type: z.enum(['income', 'expense', 'investment', 'borrow_given', 'borrow_taken', 'transfer', 'savings']),
  category: z.string().min(1, 'Category is required'),
  amount: z.number().positive('Amount must be positive'),
  payment_method: z.string().min(1, 'Payment method is required'),
  description: z.string().optional(),
  date: z.string().min(1, 'Date is required'),
})

type TransactionFormData = z.infer<typeof transactionSchema>

export const TransactionForm = () => {
  const { addTransaction } = useTransactions()
  const [loading, setLoading] = useState(false)

  const { register, handleSubmit, formState: { errors }, reset } = useForm<TransactionFormData>({
    resolver: zodResolver(transactionSchema),
    defaultValues: {
      date: new Date().toISOString().split('T')[0],
    },
  })

  const onSubmit = async (data: TransactionFormData) => {
    setLoading(true)
    try {
      const { error } = await addTransaction({
        ...data,
        status: 'completed',
      })
      
      if (error) {
        toast.error('Failed to add transaction')
      } else {
        toast.success('Transaction added successfully')
        reset()
      }
    } catch (error) {
      toast.error('An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Type</label>
          <select {...register('type')} className="w-full mt-1">
            <option value="income">Income</option>
            <option value="expense">Expense</option>
            <option value="investment">Investment</option>
            <option value="borrow_given">Borrow Given</option>
            <option value="borrow_taken">Borrow Taken</option>
            <option value="transfer">Transfer</option>
            <option value="savings">Savings</option>
          </select>
        </div>
        <div>
          <label className="text-sm font-medium">Category</label>
          <Input {...register('category')} placeholder="Enter category" />
          {errors.category && <p className="text-red-500 text-xs mt-1">{errors.category.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Amount</label>
          <Input {...register('amount', { valueAsNumber: true })} type="number" step="0.01" placeholder="0.00" />
          {errors.amount && <p className="text-red-500 text-xs mt-1">{errors.amount.message}</p>}
        </div>
        <div>
          <label className="text-sm font-medium">Payment Method</label>
          <select {...register('payment_method')} className="w-full mt-1">
            <option value="cash">Cash</option>
            <option value="bank">Bank</option>
            <option value="credit_card">Credit Card</option>
            <option value="debit_card">Debit Card</option>
            <option value="upi">UPI</option>
            <option value="cheque">Cheque</option>
            <option value="online_transfer">Online Transfer</option>
            <option value="wallet">Wallet</option>
          </select>
        </div>
      </div>

      <div>
        <label className="text-sm font-medium">Description</label>
        <Input {...register('description')} placeholder="Enter description" />
      </div>

      <div>
        <label className="text-sm font-medium">Date</label>
        <Input {...register('date')} type="date" />
        {errors.date && <p className="text-red-500 text-xs mt-1">{errors.date.message}</p>}
      </div>

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? 'Adding...' : 'Add Transaction'}
      </Button>
    </form>
  )
}