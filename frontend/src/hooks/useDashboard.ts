// src/hooks/useDashboard.ts
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { DashboardData } from '@/types'
import { useAuth } from './useAuth'

export const useDashboard = () => {
  const { user } = useAuth()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) {
      fetchDashboardData()
    }
  }, [user])

  const fetchDashboardData = async () => {
    if (!user) return

    const { data, error } = await supabase
      .rpc('get_dashboard_data', { p_user_id: user.id })

    if (!error && data) {
      setData(data[0])
    }
    setLoading(false)
  }

  return { data, loading, fetchDashboardData }
}