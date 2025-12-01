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
  Box,
  AppBar,
  Toolbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function Documents() {
  const [documents, setDocuments] = useState<any[]>([])
  const [open, setOpen] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    document_type: 'Protocol',
    description: ''
  })
  const navigate = useNavigate()

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('/api/documents/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setDocuments(response.data.documents || [])
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    }
  }

  const handleCreate = async () => {
    try {
      const token = localStorage.getItem('access_token')
      await axios.post('/api/documents/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setOpen(false)
      fetchDocuments()
      setFormData({ title: '', document_type: 'Protocol', description: '' })
    } catch (error) {
      console.error('Failed to create document:', error)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: any = {
      Draft: 'default',
      Review: 'warning',
      Approved: 'success',
      Obsolete: 'error'
    }
    return colors[status] || 'default'
  }

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Documents
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>Dashboard</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Document Management</Typography>
          <Button variant="contained" onClick={() => setOpen(true)}>
            New Document
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Document Number</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.id} hover>
                  <TableCell>{doc.document_number}</TableCell>
                  <TableCell>{doc.title}</TableCell>
                  <TableCell>{doc.document_type}</TableCell>
                  <TableCell>{doc.version}</TableCell>
                  <TableCell>
                    <Chip
                      label={doc.status}
                      color={getStatusColor(doc.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{doc.category || 'N/A'}</TableCell>
                  <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Create New Document</DialogTitle>
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
              label="Document Type"
              margin="normal"
              value={formData.document_type}
              onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
            />
            <TextField
              fullWidth
              label="Description"
              margin="normal"
              multiline
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
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

export default Documents