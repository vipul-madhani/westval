import { useEffect, useState } from 'react'
import {
  Container,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Button,
  Paper,
  Grid,
  Card,
  CardContent
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function TestManagement() {
  const [stats, setStats] = useState<any>(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('/api/tests/statistics', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch test statistics:', error)
    }
  }

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Test Management
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>Dashboard</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>Test Execution</Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Total Tests</Typography>
                <Typography variant="h3">{stats?.total || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Passed</Typography>
                <Typography variant="h3" color="success.main">{stats?.passed || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Failed</Typography>
                <Typography variant="h3" color="error.main">{stats?.failed || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Pass Rate</Typography>
                <Typography variant="h3">{stats?.pass_rate || 0}%</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}

export default TestManagement