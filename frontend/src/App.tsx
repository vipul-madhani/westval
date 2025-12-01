import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import ValidationProjects from './pages/ValidationProjects'
import Documents from './pages/Documents'
import Requirements from './pages/Requirements'
import TestManagement from './pages/TestManagement'
import TestExecution from './pages/TestExecution'
import RiskAssessment from './pages/RiskAssessment'
import Compliance from './pages/Compliance'
import TaskInbox from './pages/TaskInbox'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Dashboard />} />
          <Route path="/validation" element={<ValidationProjects />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/requirements" element={<Requirements />} />
          <Route path="/tests" element={<TestManagement />} />
          <Route path="/tests/execute/:testCaseId" element={<TestExecution />} />
          <Route path="/tasks" element={<TaskInbox />} />
          <Route path="/risk" element={<RiskAssessment />} />
          <Route path="/compliance" element={<Compliance />} />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App