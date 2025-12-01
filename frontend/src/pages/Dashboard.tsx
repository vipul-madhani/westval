import { useEffect, useState } from 'react'
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Button
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const response = await axios.get('/api/validation/statistics', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setStats(response.data)
      } catch (error) {
        console.error('Failed to fetch statistics:', error)
      }
    }

    fetchStats()
  }, [])

  const handleLogout = () => {
    localStorage.clear()
    navigate('/login')
  }

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Westval - Dashboard
          </Typography>
          <Button color="inherit" onClick={() => navigate('/validation')}>Projects</Button>
          <Button color="inherit" onClick={() => navigate('/documents')}>Documents</Button>
          <Button color="inherit" onClick={() => navigate('/requirements')}>Requirements</Button>
          <Button color="inherit" onClick={() => navigate('/tests')}>Tests</Button>
          <Button color="inherit" onClick={() => navigate('/compliance')}>Compliance</Button>
          <Button color="inherit" onClick={handleLogout}>Logout</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard Overview
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Projects
                </Typography>
                <Typography variant="h3">
                  {stats?.total_projects || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  In Progress
                </Typography>
                <Typography variant="h3">
                  {stats?.by_status?.['In Progress'] || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Completed
                </Typography>
                <Typography variant="h3">
                  {stats?.by_status?.Approved || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item>
                  <Button variant="contained" onClick={() => navigate('/validation')}>New Validation Project</Button>
                </Grid>
                <Grid item>
                  <Button variant="outlined" onClick={() => navigate('/documents')}>Create Document</Button>
                </Grid>
                <Grid item>
                  <Button variant="outlined" onClick={() => navigate('/requirements')}>Add Requirement</Button>
                </Grid>
                <Grid item>
                  <Button variant="outlined" onClick={() => navigate('/tests')}>Create Test Case</Button>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                Validation Types Distribution
              </Typography>
              {stats?.by_type && Object.entries(stats.by_type).map(([type, count]: [string, any]) => (
                <Box key={type} sx={{ mt: 2 }}>
                  <Typography>{type}: {count}</Typography>
                </Box>
              ))}
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}

export default Dashboard