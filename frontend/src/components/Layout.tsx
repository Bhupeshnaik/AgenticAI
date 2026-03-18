import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
  HomeIcon,
  CpuChipIcon,
  ChatBubbleLeftRightIcon,
  MegaphoneIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ArrowPathIcon,
  ChartBarIcon,
  Bars3Icon,
  XMarkIcon,
  SparklesIcon,
  MapIcon,
} from '@heroicons/react/24/outline'

const navItems = [
  { to: '/dashboard',  label: 'Dashboard',    icon: HomeIcon },
  { to: '/phases',     label: 'Phase Map',     icon: MapIcon },
  { to: '/agents',     label: 'Agents',        icon: CpuChipIcon },
  { to: '/chat',       label: 'AI Chat',       icon: ChatBubbleLeftRightIcon },
  { to: '/workflows',  label: 'Workflows',     icon: ArrowPathIcon },
  { to: '/campaigns',  label: 'Campaigns',     icon: MegaphoneIcon },
  { to: '/leads',      label: 'Leads',         icon: UserGroupIcon },
  { to: '/compliance', label: 'Compliance',    icon: ShieldCheckIcon },
  { to: '/analytics',  label: 'Analytics',     icon: ChartBarIcon },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 border-r border-gray-800
        transform transition-transform duration-200 ease-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:relative lg:translate-x-0 lg:block flex flex-col
      `}>
        {/* Logo */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="text-sm font-bold text-white leading-tight">Marketing AI</div>
              <div className="text-xs text-gray-500">Bank Platform</div>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-white"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-brand-600/20 text-brand-400 border border-brand-800/50'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                }`
              }
            >
              <Icon className="w-4.5 h-4.5 flex-shrink-0 w-5 h-5" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-800">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse-slow" />
            <span className="text-xs text-gray-500">9 agents online</span>
          </div>
          <div className="text-xs text-gray-600 mt-1">Powered by Azure OpenAI</div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center justify-between px-4 py-3 bg-gray-900 border-b border-gray-800 lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-gray-400 hover:text-white"
          >
            <Bars3Icon className="w-6 h-6" />
          </button>
          <div className="flex items-center gap-2">
            <SparklesIcon className="w-5 h-5 text-brand-400" />
            <span className="text-sm font-semibold text-white">Marketing AI</span>
          </div>
          <div className="w-6" />
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-950 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
