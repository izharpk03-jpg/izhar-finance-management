import { ReactNode, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "@/hooks/useAuth"
import { useTheme } from "@/components/ThemeProvider"
import { Button } from "@/components/ui/button"
import {
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  Wallet,
  Users,
  ArrowLeftRight,
  CreditCard,
  PiggyBank,
  FileText,
  Settings,
  User,
  LogOut,
  Moon,
  Sun,
  Menu,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Transactions", href: "/transactions", icon: TrendingUp },
  { name: "Investments", href: "/investments", icon: Wallet },
  { name: "Borrow", href: "/borrow", icon: Users },
  { name: "Transfers", href: "/transfers", icon: ArrowLeftRight },
  { name: "Credit Cards", href: "/credit-cards", icon: CreditCard },
  { name: "Savings", href: "/savings", icon: PiggyBank },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Settings", href: "/settings", icon: Settings },
  { name: "Profile", href: "/profile", icon: User },
]

export const Layout = ({ children }: LayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { signOut } = useAuth()
  const { theme, setTheme } = useTheme()

  const handleLogout = async () => {
    await signOut()
    navigate("/login")
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Mobile sidebar */}
      <div className="lg:hidden">
        <div className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between p-4 bg-white dark:bg-gray-900 border-b">
          <h1 className="text-xl font-bold">IZHAR Finance</h1>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X /> : <Menu />}
          </Button>
        </div>

        {sidebarOpen && (
          <div className="fixed inset-0 z-40 bg-black/50" onClick={() => setSidebarOpen(false)} />
        )}

        <div
          className={cn(
            "fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 transform transition-transform duration-300 ease-in-out",
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <div className="flex flex-col h-full">
            <div className="p-4 border-b">
              <h1 className="text-2xl font-bold">IZHAR Finance</h1>
            </div>
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                    location.pathname === item.href
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-gray-100 dark:hover:bg-gray-800"
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              ))}
            </nav>
            <div className="p-4 border-t space-y-2">
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              >
                {theme === "dark" ? <Sun className="h-5 w-5 mr-2" /> : <Moon className="h-5 w-5 mr-2" />}
                Toggle Theme
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
                onClick={handleLogout}
              >
                <LogOut className="h-5 w-5 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 min-h-0 bg-white dark:bg-gray-900 border-r">
          <div className="flex items-center h-16 px-4 border-b">
            <h1 className="text-2xl font-bold">IZHAR Finance</h1>
          </div>
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                  location.pathname === item.href
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-gray-100 dark:hover:bg-gray-800"
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </nav>
          <div className="p-4 border-t space-y-2">
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? <Sun className="h-5 w-5 mr-2" /> : <Moon className="h-5 w-5 mr-2" />}
              Toggle Theme
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
              onClick={handleLogout}
            >
              <LogOut className="h-5 w-5 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        <div className="lg:pt-0 pt-16">
          <main>{children}</main>
        </div>
      </div>
    </div>
  )
}