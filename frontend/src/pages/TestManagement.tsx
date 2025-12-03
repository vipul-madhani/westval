import { useEffect, useState } from 'react'
import {
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Box,
  Paper,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  IconButton,
  Tooltip,
  Stack
} from '@mui/material'
import {
  Add as AddIcon,
  PlayArrow as ExecuteIcon,
  Visibility as ViewIcon,
  Assessment as ReportIcon,
  CheckCircle as PassIcon,
  Cancel as FailIcon
} from '@mui/icons-material'
import axios from 'axios'

interface TestPlan {
  id: string
  name: string
  description: string
  status: string
  test_cases_count: number
  test_sets_count: number
  created_at: string
}

interface TestCase {
  id: string
  name: string
  description: string
  test_type: string
  priority: number
  status: string
  steps_count: number
  executions_count: number
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

function TestManagement() {
  const [tabValue, setTabValue] = useState(0)
  const [testPlans, setTestPlans] = useState<TestPlan[]>([])
  const [testCases, setTestCases] = useState<TestCase[]>([])
  const [statistics, setStatistics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('access_token')
      const headers = { Authorization: `Bearer ${token}` }

      const [plansRes, casesRes, statsRes] = await Promise.all([
        axios.get('/api/tests/plans', { headers }),
        axios.get('/api/tests/cases', { headers }),
        axios.get('/api/tests/statistics', { headers })
      ])

      setTestPlans(plansRes.data.plans || [])
      setTestCases(casesRes.data.cases || [])
      setStatistics(statsRes.data)
    } catch (error) {
      console.error('Failed to fetch test data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string): "default" | "primary" | "secondary" | "success" | "warning" => {
    const colors: Record<string, "default" | "primary" | "secondary" | "success" | "warning"> = {
      'Draft': 'default',
      'Active': 'primary',
      'Completed': 'success',
      'Archived': 'warning'
    }
    return colors[status] || 'default'
  }

  const getPriorityLabel = (priority: number): string => {
    const labels: Record<number, string> = {
      1: 'Critical',
      2: 'High',
      3: 'Medium',
      4: 'Low'
    }
    return labels[priority] || 'Unknown'
  }

  const getPriorityColor = (priority: number): "error" | "warning" | "info" | "default" => {
    const colors: Record<number, "error" | "warning" | "info" | "default"> = {
      1: 'error',
      2: 'warning',
      3: 'info',
      4: 'default'
    }
    return colors[priority] || 'default'
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Test Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            size="large"
          >
            New Test Plan
          </Button>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.main', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{statistics?.total_plans || 0}</Typography>
              <Typography variant="body2">Test Plans</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'info.main', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{statistics?.total_cases || 0}</Typography>
              <Typography variant="body2">Test Cases</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.main', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{statistics?.passed_executions || 0}</Typography>
              <Typography variant="body2">Passed</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'error.main', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{statistics?.failed_executions || 0}</Typography>
              <Typography variant="body2">Failed</Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Pass Rate */}
        {statistics && statistics.total_executions > 0 && (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="h6">Overall Pass Rate</Typography>
              <Typography variant="h6" fontWeight="bold" color="primary">
                {statistics.pass_rate}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={statistics.pass_rate}
              sx={{ height: 10, borderRadius: 5 }}
              color={statistics.pass_rate >= 80 ? 'success' : statistics.pass_rate >= 60 ? 'warning' : 'error'}
            />
          </Paper>
        )}
      </Box>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Test Plans" />
          <Tab label="Test Cases" />
          <Tab label="Executions" />
        </Tabs>
      </Paper>

      {/* Test Plans Tab */}
      <TabPanel value={tabValue} index={0}>
        {loading ? (
          <LinearProgress />
        ) : (
          <Grid container spacing={3}>
            {testPlans.map((plan) => (
              <Grid item xs={12} md={6} lg={4} key={plan.id}>
                <Card
                  sx={{
                    height: '100%',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 6
                    }
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Chip
                        label={plan.status}
                        color={getStatusColor(plan.status)}
                        size="small"
                      />
                    </Box>

                    <Typography variant="h6" component="h3" gutterBottom>
                      {plan.name}
                    </Typography>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
                      {plan.description?.substring(0, 100)}...
                    </Typography>

                    <Stack spacing={1}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" color="text.secondary">Test Cases:</Typography>
                        <Typography variant="caption" fontWeight="bold">{plan.test_cases_count}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" color="text.secondary">Test Sets:</Typography>
                        <Typography variant="caption" fontWeight="bold">{plan.test_sets_count}</Typography>
                      </Box>
                    </Stack>
                  </CardContent>

                  <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
                    <Tooltip title="View Details">
                      <IconButton size="small" color="primary">
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Execute Tests">
                      <IconButton size="small" color="success">
                        <ExecuteIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Reports">
                      <IconButton size="small" color="info">
                        <ReportIcon />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      {/* Test Cases Tab */}
      <TabPanel value={tabValue} index={1}>
        {loading ? (
          <LinearProgress />
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Test Case ID</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Steps</TableCell>
                  <TableCell>Executions</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {testCases.map((testCase) => (
                  <TableRow key={testCase.id} hover>
                    <TableCell>{testCase.id.substring(0, 8)}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {testCase.name}
                      </Typography>
                    </TableCell>
                    <TableCell>{testCase.test_type}</TableCell>
                    <TableCell>
                      <Chip
                        label={getPriorityLabel(testCase.priority)}
                        color={getPriorityColor(testCase.priority)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{testCase.steps_count}</TableCell>
                    <TableCell>{testCase.executions_count}</TableCell>
                    <TableCell>
                      <Chip
                        label={testCase.status}
                        color={getStatusColor(testCase.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Execute">
                        <IconButton size="small" color="primary">
                          <ExecuteIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="View">
                        <IconButton size="small">
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </TabPanel>

      {/* Executions Tab */}
      <TabPanel value={tabValue} index={2}>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            Test Execution History
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {statistics?.total_executions || 0} executions completed
          </Typography>
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 4 }}>
            <Box>
              <PassIcon sx={{ fontSize: 48, color: 'success.main' }} />
              <Typography variant="h4" color="success.main">{statistics?.passed_executions || 0}</Typography>
              <Typography variant="caption">Passed</Typography>
            </Box>
            <Box>
              <FailIcon sx={{ fontSize: 48, color: 'error.main' }} />
              <Typography variant="h4" color="error.main">{statistics?.failed_executions || 0}</Typography>
              <Typography variant="caption">Failed</Typography>
            </Box>
          </Box>
        </Paper>
      </TabPanel>
    </Container>
  )
}

export default TestManagement