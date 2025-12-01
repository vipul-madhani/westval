import {
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Paper,
  TextField,
  MenuItem
} from '@mui/material'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TraceabilityMatrix from '../components/TraceabilityMatrix'

function TraceabilityPage() {
  const navigate = useNavigate()
  const [selectedProject, setSelectedProject] = useState('proj-001')

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Requirements Traceability Matrix
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>Dashboard</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <TextField
            select
            label="Select Project"
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            sx={{ minWidth: 300 }}
          >
            <MenuItem value="proj-001">ERP System Validation</MenuItem>
            <MenuItem value="proj-002">LIMS Implementation</MenuItem>
            <MenuItem value="proj-003">Laboratory Equipment Qualification</MenuItem>
          </TextField>
        </Paper>

        <TraceabilityMatrix projectId={selectedProject} />
      </Container>
    </Box>
  )
}

export default TraceabilityPage