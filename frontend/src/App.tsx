import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AgentsPage from './pages/AgentsPage'
import ChatPage from './pages/ChatPage'
import CampaignsPage from './pages/CampaignsPage'
import LeadsPage from './pages/LeadsPage'
import CompliancePage from './pages/CompliancePage'
import WorkflowsPage from './pages/WorkflowsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import PhasesPage from './pages/PhasesPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="agents" element={<AgentsPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="chat/:agentName" element={<ChatPage />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="leads" element={<LeadsPage />} />
          <Route path="compliance" element={<CompliancePage />} />
          <Route path="workflows" element={<WorkflowsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="phases" element={<PhasesPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
