import { useEffect, useState } from 'react'
import {
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Box,
  AppBar,
  Toolbar
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function ValidationProjects() {
  const [projects, setProjects] = useState<any[]>([])
  const [open, setOpen] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    validation_type: 'CSV',
    methodology: 'Waterfall',
    gamp_category: '5',
    risk_level: 'Medium'
  })
  const navigate = useNavigate()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('/api/validation/projects', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setProjects(response.data.projects || [])
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    }
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
        risk_level: 'Medium'
      })
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: any = {
      Planning: 'default',
      'In Progress': 'primary',
      Testing: 'warning',
      Approved: 'success',
      Closed: 'default'
    }
    return colors[status] || 'default'
  }

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Validation Projects
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>Dashboard</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Validation Projects</Typography>
          <Button variant="contained" onClick={() => setOpen(true)}>
            New Project
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Project Number</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Methodology</TableCell>
                <TableCell>GAMP</TableCell>
                <TableCell>Risk Level</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id} hover>
                  <TableCell>{project.project_number}</TableCell>
                  <TableCell>{project.title}</TableCell>
                  <TableCell>{project.validation_type}</TableCell>
                  <TableCell>{project.methodology}</TableCell>
                  <TableCell>{project.gamp_category}</TableCell>
                  <TableCell>
                    <Chip label={project.risk_level} size="small" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={project.status}
                      color={getStatusColor(project.status)}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Create New Validation Project</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Title"
              margin="normal"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
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
            <TextField
              fullWidth
              select
              label="Validation Type"
              margin="normal"
              value={formData.validation_type}
              onChange={(e) => setFormData({ ...formData, validation_type: e.target.value })}
            >
              <MenuItem value="CSV">Computer System Validation</MenuItem>
              <MenuItem value="Lab">Laboratory Systems</MenuItem>
              <MenuItem value="Cleaning">Cleaning Validation</MenuItem>
              <MenuItem value="Process">Process Validation</MenuItem>
              <MenuItem value="Equipment">Equipment Qualification</MenuItem>
            </TextField>
            <TextField
              fullWidth
              select
              label="Methodology"
              margin="normal"
              value={formData.methodology}
              onChange={(e) => setFormData({ ...formData, methodology: e.target.value })}
            >
              <MenuItem value="Waterfall">Waterfall (Traditional V-Model)</MenuItem>
              <MenuItem value="Agile">Agile</MenuItem>
              <MenuItem value="CSA">Computer Software Assurance (CSA)</MenuItem>
              <MenuItem value="Hybrid">Hybrid</MenuItem>
            </TextField>
            <TextField
              fullWidth
              select
              label="GAMP Category"
              margin="normal"
              value={formData.gamp_category}
              onChange={(e) => setFormData({ ...formData, gamp_category: e.target.value })}
            >
              <MenuItem value="1">Category 1 - Operating Systems</MenuItem>
              <MenuItem value="3">Category 3 - Non-configured</MenuItem>
              <MenuItem value="4">Category 4 - Configured</MenuItem>
              <MenuItem value="5">Category 5 - Custom</MenuItem>
            </TextField>
            <TextField
              fullWidth
              select
              label="Risk Level"
              margin="normal"
              value={formData.risk_level}
              onChange={(e) => setFormData({ ...formData, risk_level: e.target.value })}
            >
              <MenuItem value="Low">Low</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="High">High</MenuItem>
              <MenuItem value="Critical">Critical</MenuItem>
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancel</Button>
            <Button onClick={handleCreate} variant="contained">Create</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  )
}

export default ValidationProjects