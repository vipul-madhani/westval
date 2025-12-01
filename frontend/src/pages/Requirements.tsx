import { useEffect, useState } from 'react'
import {
  Container,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function Requirements() {
  const [requirements, setRequirements] = useState<any[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    fetchRequirements()
  }, [])

  const fetchRequirements = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('/api/requirements/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setRequirements(response.data.requirements || [])
    } catch (error) {
      console.error('Failed to fetch requirements:', error)
    }
  }

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Requirements Management
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>Dashboard</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>Requirements</Typography>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Requirement ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Criticality</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requirements.map((req) => (
                <TableRow key={req.id} hover>
                  <TableCell>{req.requirement_id}</TableCell>
                  <TableCell>{req.title}</TableCell>
                  <TableCell>{req.requirement_type}</TableCell>
                  <TableCell><Chip label={req.priority} size="small" /></TableCell>
                  <TableCell><Chip label={req.criticality} size="small" /></TableCell>
                  <TableCell><Chip label={req.status} size="small" color="primary" /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>
    </Box>
  )
}

export default Requirements