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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Box,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  Stack,
  Paper,
  IconButton,
  Tooltip
} from '@mui/material'
import {
  Add as AddIcon,
  FilterList as FilterIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material'
import axios from 'axios'

interface Project {
  id: string
  project_number: string
  title: string
  description: string
  validation_type: string
  methodology: string
  gamp_category: string
  risk_level: string
  risk_score: number
  status: string
  department: string
  planned_start_date: string | null
  planned_end_date: string | null
  created_at: string
}

function ValidationProjects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterType, setFilterType] = useState('all')
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    validation_type: 'CSV',
    methodology: 'Waterfall',
    gamp_category: '5',
    risk_level: 'Medium',
    department: 'Quality Assurance'
  })

  useEffect(() => {
    fetchProjects()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [projects, filterStatus, filterType])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('access_token')
      const response = await axios.get('/api/validation/projects', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setProjects(response.data.projects || [])
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...projects]

    if (filterStatus !== 'all') {
      filtered = filtered.filter(p => p.status === filterStatus)
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(p => p.validation_type === filterType)
    }

    setFilteredProjects(filtered)
  }

  const handleCreate = async () => {
    try {
      const token = localStorage.getItem('access_token')
      await axios.post('/api/validation/projects', formData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setOpen(false)
      fetchProjects()
      setFormData({
        title: '',
        description: '',
        validation_type: 'CSV',
        methodology: 'Waterfall',
        gamp_category: '5',
        risk_level: 'Medium',
        department: 'Quality Assurance'
      })
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  const getStatusColor = (status: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    const colors: Record<string, "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"> = {
      'Planning': 'info',
      'In Progress': 'primary',
      'Testing': 'warning',
      'Review': 'secondary',
      'Approved': 'success',
      'Closed': 'default'
    }
    return colors[status] || 'default'
  }

  const getRiskColor = (level: string): "default" | "error" | "warning" | "info" => {
    const colors: Record<string, "default" | "error" | "warning" | "info"> = {
      'Low': 'info',
      'Medium': 'warning',
      'High': 'error',
      'Critical': 'error'
    }
    return colors[level] || 'default'
  }

  const getProgress = (status: string): number => {
    const progress: Record<string, number> = {
      'Planning': 15,
      'In Progress': 50,
      'Testing': 70,
      'Review': 85,
      'Approved': 100,
      'Closed': 100
    }
    return progress[status] || 0
  }

  const stats = {
    total: projects.length,
    planning: projects.filter(p => p.status === 'Planning').length,
    inProgress: projects.filter(p => p.status === 'In Progress').length,
    review: projects.filter(p => p.status === 'Review').length,
    approved: projects.filter(p => p.status === 'Approved').length
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Validation Projects
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
            size="large"
          >
            New Project
          </Button>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={2.4}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.main', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{stats.total}</Typography>
              <Typography variant="body2">Total Projects</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'info.main', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{stats.planning}</Typography>
              <Typography variant="body2">Planning</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.dark', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{stats.inProgress}</Typography>
              <Typography variant="body2">In Progress</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'secondary.main', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{stats.review}</Typography>
              <Typography variant="body2">In Review</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.main', color: 'white' }}>
              <Typography variant="h3" fontWeight="bold">{stats.approved}</Typography>
              <Typography variant="body2">Approved</Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <FilterIcon />
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="all">All Statuses</MenuItem>
                <MenuItem value="Planning">Planning</MenuItem>
                <MenuItem value="In Progress">In Progress</MenuItem>
                <MenuItem value="Testing">Testing</MenuItem>
                <MenuItem value="Review">Review</MenuItem>
                <MenuItem value="Approved">Approved</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Validation Type</InputLabel>
              <Select
                value={filterType}
                label="Validation Type"
                onChange={(e) => setFilterType(e.target.value)}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="CSV">Computer System (CSV)</MenuItem>
                <MenuItem value="Lab">Laboratory Systems</MenuItem>
                <MenuItem value="Equipment">Equipment Qualification</MenuItem>
                <MenuItem value="Cleaning">Cleaning Validation</MenuItem>
                <MenuItem value="Process">Process Validation</MenuItem>
              </Select>
            </FormControl>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
              Showing {filteredProjects.length} of {projects.length} projects
            </Typography>
          </Stack>
        </Paper>
      </Box>

      {/* Projects Grid */}
      {loading ? (
        <LinearProgress />
      ) : (
        <Grid container spacing={3}>
          {filteredProjects.map((project) => (
            <Grid item xs={12} md={6} lg={4} key={project.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 6
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Chip
                      label={project.project_number}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      label={project.status}
                      color={getStatusColor(project.status)}
                      size="small"
                    />
                  </Box>

                  <Typography variant="h6" component="h2" gutterBottom>
                    {project.title}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
                    {project.description?.substring(0, 100)}...
                  </Typography>

                  <Stack spacing={1}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">Type:</Typography>
                      <Typography variant="caption" fontWeight="bold">{project.validation_type}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">Methodology:</Typography>
                      <Typography variant="caption" fontWeight="bold">{project.methodology}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">GAMP:</Typography>
                      <Typography variant="caption" fontWeight="bold">Category {project.gamp_category}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">Risk:</Typography>
                      <Chip
                        label={project.risk_level}
                        color={getRiskColor(project.risk_level)}
                        size="small"
                        sx={{ height: 20 }}
                      />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">Department:</Typography>
                      <Typography variant="caption" fontWeight="bold">{project.department}</Typography>
                    </Box>
                  </Stack>

                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">Progress</Typography>
                      <Typography variant="caption" fontWeight="bold">{getProgress(project.status)}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={getProgress(project.status)}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                </CardContent>

                <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
                  <Tooltip title="View Details">
                    <IconButton size="small" color="primary">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton size="small" color="secondary">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Reports">
                    <IconButton size="small" color="info">
                      <AssessmentIcon />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Project Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Validation Project</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Title"
            margin="normal"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
          />
          <TextField
            fullWidth
            label="Description"
            margin="normal"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Validation Type"
                value={formData.validation_type}
                onChange={(e) => setFormData({ ...formData, validation_type: e.target.value })}
              >
                <MenuItem value="CSV">Computer System Validation</MenuItem>
                <MenuItem value="Lab">Laboratory Systems</MenuItem>
                <MenuItem value="Cleaning">Cleaning Validation</MenuItem>
                <MenuItem value="Process">Process Validation</MenuItem>
                <MenuItem value="Equipment">Equipment Qualification</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Methodology"
                value={formData.methodology}
                onChange={(e) => setFormData({ ...formData, methodology: e.target.value })}
              >
                <MenuItem value="Waterfall">Waterfall (V-Model)</MenuItem>
                <MenuItem value="Agile">Agile</MenuItem>
                <MenuItem value="CSA">Computer Software Assurance</MenuItem>
                <MenuItem value="Hybrid">Hybrid</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="GAMP Category"
                value={formData.gamp_category}
                onChange={(e) => setFormData({ ...formData, gamp_category: e.target.value })}
              >
                <MenuItem value="1">Category 1 - Operating Systems</MenuItem>
                <MenuItem value="3">Category 3 - Non-configured</MenuItem>
                <MenuItem value="4">Category 4 - Configured</MenuItem>
                <MenuItem value="5">Category 5 - Custom</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Risk Level"
                value={formData.risk_level}
                onChange={(e) => setFormData({ ...formData, risk_level: e.target.value })}
              >
                <MenuItem value="Low">Low</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Critical">Critical</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Department"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create Project</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default ValidationProjects