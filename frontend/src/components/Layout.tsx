import { Outlet, NavLink } from 'react-router-dom'
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

// Barclays Eagle SVG logo
function BarclaysLogo({ className = '' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 180 50" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Eagle */}
      <path d="M10 8 C10 8 6 10 5 14 C4 18 6 22 10 24 C8 22 8 18 10 16 C12 20 14 22 14 26 C16 24 16 20 14 16 C18 18 20 22 18 26 C20 24 22 20 20 14 C18 10 14 8 10 8Z" fill="#00AEEF"/>
      <path d="M10 26 C10 26 8 30 10 34 C12 38 16 40 20 38 C16 38 14 36 14 32 C16 34 18 36 20 38 C20 34 18 30 16 28 C18 30 22 32 22 36 C24 32 22 28 20 26 C18 24 14 24 10 26Z" fill="#00AEEF"/>
      <path d="M8 14 C6 14 4 16 4 18 C4 20 6 22 8 22 C6 20 6 18 8 16 C8 18 8 20 8 22 C10 20 10 18 8 16Z" fill="#00AEEF"/>
      {/* BARCLAYS text */}
      <text x="32" y="34" fontFamily="Arial, sans-serif" fontWeight="700" fontSize="22" fill="#00AEEF" letterSpacing="1">BARCLAYS</text>
    </svg>
  )
}

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200
        transform transition-transform duration-200 ease-out shadow-lg
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:relative lg:translate-x-0 lg:block flex flex-col
      `}>
        {/* Barclays Logo */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200 bg-white">
          <BarclaysLogo className="h-8 w-auto" />
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* App subtitle */}
        <div className="px-5 py-2 border-b border-gray-200">
          <p className="text-xs font-semibold text-gray-500 tracking-wide uppercase">Marketing AI Platform</p>
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
                    ? 'bg-white text-black border border-brand-500 shadow-sm'
                    : 'text-black hover:bg-gray-50 hover:border hover:border-gray-200'
                }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse-slow" />
            <span className="text-xs text-gray-500">9 agents online</span>
          </div>
          <div className="text-xs text-gray-400 mt-1">Powered by Azure OpenAI</div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top bar — mobile only */}
        <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 lg:hidden shadow-sm">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-gray-500 hover:text-brand-800"
          >
            <Bars3Icon className="w-6 h-6" />
          </button>
          <BarclaysLogo className="h-7 w-auto" />
          <div className="w-6" />
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-50 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
