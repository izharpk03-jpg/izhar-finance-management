// src/pages/Dashboard.tsx
import { useEffect } from 'react'
import { useDashboard } from '@/hooks/useDashboard'
import { DashboardCard } from '@/components/DashboardCard'
import { TransactionForm } from '@/components/TransactionForm'
import { 
  Wallet, 
  CreditCard, 
  TrendingUp, 
  TrendingDown, 
  PiggyBank,
  Users,
  Calendar,
  DollarSign
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts'
import { motion } from 'framer-motion'

export const Dashboard = () => {
  const { data, loading, fetchDashboardData } = useDashboard()

  useEffect(() => {
    fetchDashboardData()
  }, [])

  if (loading || !data) {
    return <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>
  }

  const monthlyData = [
    { month: 'Jan', income: 4500, expense: 3200, savings: 1300 },
    { month: 'Feb', income: 5200, expense: 2800, savings: 2400 },
    { month: 'Mar', income: 4800, expense: 3500, savings: 1300 },
    { month: 'Apr', income: 6100, expense: 3800, savings: 2300 },
    { month: 'May', income: 5800, expense: 3100, savings: 2700 },
    { month: 'Jun', income: 6300, expense: 3400, savings: 2900 },
  ]

  const expenseCategories = [
    { name: 'Food', value: 1200 },
    { name: 'Transport', value: 800 },
    { name: 'Utilities', value: 600 },
    { name: 'Entertainment', value: 400 },
    { name: 'Shopping', value: 900 },
  ]

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto p-4 space-y-6"
    >
      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Balance"
          value={formatCurrency(data.total_balance)}
          icon={<Wallet className="h-4 w-4" />}
          trend={{ value: 12, isPositive: true }}
        />
        <DashboardCard
          title="Total Income"
          value={formatCurrency(data.total_income)}
          icon={<TrendingUp className="h-4 w-4" />}
          trend={{ value: 8, isPositive: true }}
        />
        <DashboardCard
          title="Total Expenses"
          value={formatCurrency(data.total_expenses)}
          icon={<TrendingDown className="h-4 w-4" />}
          trend={{ value: 5, isPositive: false }}
        />
        <DashboardCard
          title="Net Worth"
          value={formatCurrency(data.net_worth)}
          icon={<DollarSign className="h-4 w-4" />}
          trend={{ value: 15, isPositive: true }}
        />
      </div>

      {/* Secondary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Cash Balance"
          value={formatCurrency(data.cash_balance)}
          icon={<Wallet className="h-4 w-4" />}
        />
        <DashboardCard
          title="Bank Balance"
          value={formatCurrency(data.bank_balance)}
          icon={<CreditCard className="h-4 w-4" />}
        />
        <DashboardCard
          title="Savings"
          value={formatCurrency(data.savings)}
          icon={<PiggyBank className="h-4 w-4" />}
        />
        <DashboardCard
          title="Investments"
          value={formatCurrency(data.total_investments)}
          icon={<TrendingUp className="h-4 w-4" />}
        />
        <DashboardCard
          title="Borrow Given"
          value={formatCurrency(data.borrow_given)}
          icon={<Users className="h-4 w-4" />}
        />
        <DashboardCard
          title="Borrow Taken"
          value={formatCurrency(data.borrow_taken)}
          icon={<Users className="h-4 w-4" />}
        />
        <DashboardCard
          title="Credit Card Outstanding"
          value={formatCurrency(data.credit_card_outstanding)}
          icon={<CreditCard className="h-4 w-4" />}
        />
        <DashboardCard
          title="Upcoming Payments"
          value={formatCurrency(data.upcoming_payments)}
          icon={<Calendar className="h-4 w-4" />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-900 p-4 rounded-lg shadow-lg backdrop-blur-sm bg-white/80 dark:bg-gray-900/80"
        >
          <h3 className="text-lg font-semibold mb-4">Monthly Income & Expenses</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="income" fill="#8884d8" />
              <Bar dataKey="expense" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-900 p-4 rounded-lg shadow-lg backdrop-blur-sm bg-white/80 dark:bg-gray-900/80"
        >
          <h3 className="text-lg font-semibold mb-4">Expense Categories</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={expenseCategories}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {expenseCategories.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Quick Actions & Recent Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-900 p-4 rounded-lg shadow-lg backdrop-blur-sm bg-white/80 dark:bg-gray-900/80"
        >
          <h3 className="text-lg font-semibold mb-4">Quick Add Transaction</h3>
          <TransactionForm />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-900 p-4 rounded-lg shadow-lg backdrop-blur-sm bg-white/80 dark:bg-gray-900/80"
        >
          <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
          <div className="space-y-2">
            {/* This would be populated with real data */}
            <div className="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded">
              <div>
                <p className="font-medium">Salary</p>
                <p className="text-sm text-gray-500">Today</p>
              </div>
              <span className="text-green-500 font-semibold">+$3,500</span>
            </div>
            <div className="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded">
              <div>
                <p className="font-medium">Groceries</p>
                <p className="text-sm text-gray-500">Yesterday</p>
              </div>
              <span className="text-red-500 font-semibold">-$250</span>
            </div>
            <div className="flex justify-between items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded">
              <div>
                <p className="font-medium">Stock Investment</p>
                <p className="text-sm text-gray-500">2 days ago</p>
              </div>
              <span className="text-blue-500 font-semibold">-$1,000</span>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}