import { useEffect, useState } from 'react'
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress
} from '@mui/material'
import {
  Assignment,
  CheckCircle,
  Warning,
  TrendingUp,
  AccountTree,
  Description,
  Science
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import axios from 'axios'

function Dashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState<any>(null)
  const [notifications, setNotifications] = useState<any[]>([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token')

      // Mock data - replace with actual API calls
      setStats({
        activeProjects: 5,
        totalTests: 245,
        testsPass: 198,
        testsFailed: 12,
        pendingApprovals: 8,
        complianceScore: 96
      })

      const notifResponse = await axios.get('/api/workflow/notifications', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setNotifications(notifResponse.data.notifications || [])
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    }
  }

  const testData = [
    { name: 'Passed', value: 198, color: '#4caf50' },
    { name: 'Failed', value: 12, color: '#f44336' },
    { name: 'Pending', value: 35, color: '#ff9800' }
  ]

  const projectData = [
    { name: 'ERP CSV', progress: 85 },
    { name: 'LIMS Validation', progress: 60 },
    { name: 'Equipment IQ', progress: 95 },
    { name: 'Lab OQ', progress: 40 }
  ]

  return (
    <Box>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Quick Stats */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h3">{stats?.activeProjects || 0}</Typography>
                    <Typography variant="body2">Active Projects</Typography>
                  </Box>
                  <Assignment sx={{ fontSize: 60, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h3">{stats?.testsPass || 0}</Typography>
                    <Typography variant="body2">Tests Passed</Typography>
                  </Box>
                  <CheckCircle sx={{ fontSize: 60, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'warning.main', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h3">{stats?.pendingApprovals || 0}</Typography>
                    <Typography variant="body2">Pending Tasks</Typography>
                  </Box>
                  <Warning sx={{ fontSize: 60, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'info.main', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h3">{stats?.complianceScore || 0}%</Typography>
                    <Typography variant="body2">Compliance Score</Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 60, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              startIcon={<Assignment />}
              onClick={() => navigate('/validation')}
            >
              New Validation Project
            </Button>
            <Button
              variant="outlined"
              startIcon={<Science />}
              onClick={() => navigate('/tests')}
            >
              Execute Tests
            </Button>
            <Button
              variant="outlined"
              startIcon={<AccountTree />}
              onClick={() => navigate('/traceability')}
            >
              View Traceability
            </Button>
            <Button
              variant="outlined"
              startIcon={<Description />}
              onClick={() => navigate('/documents')}
            >
              Documents
            </Button>
          </Box>
        </Paper>

        <Grid container spacing={3}>
          {/* Test Results Chart */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Test Execution Summary
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={testData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {testData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Project Progress */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Project Progress
              </Typography>
              <List>
                {projectData.map((project) => (
                  <ListItem key={project.name}>
                    <ListItemText
                      primary={project.name}
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={project.progress}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {project.progress}% Complete
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Recent Notifications */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recent Notifications
              </Typography>
              <List>
                {notifications.slice(0, 5).map((notif) => (
                  <ListItem key={notif.id}>
                    <ListItemText
                      primary={notif.title}
                      secondary={new Date(notif.created_at).toLocaleString()}
                    />
                    {notif.priority === 'URGENT' && (
                      <Chip label="Urgent" color="error" size="small" />
                    )}
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Compliance Status */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Compliance Status
              </Typography>
              <List>
                <ListItem>
                  <CheckCircle color="success" sx={{ mr: 2 }} />
                  <ListItemText
                    primary="21 CFR Part 11"
                    secondary="Fully Compliant"
                  />
                  <Chip label="Active" color="success" size="small" />
                </ListItem>
                <ListItem>
                  <CheckCircle color="success" sx={{ mr: 2 }} />
                  <ListItemText
                    primary="EU Annex 11"
                    secondary="Fully Compliant"
                  />
                  <Chip label="Active" color="success" size="small" />
                </ListItem>
                <ListItem>
                  <CheckCircle color="success" sx={{ mr: 2 }} />
                  <ListItemText
                    primary="GAMP 5"
                    secondary="Aligned"
                  />
                  <Chip label="Active" color="success" size="small" />
                </ListItem>
                <ListItem>
                  <CheckCircle color="success" sx={{ mr: 2 }} />
                  <ListItemText
                    primary="Audit Trail"
                    secondary="Recording All Activities"
                  />
                  <Chip label="Active" color="success" size="small" />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}

export default Dashboard