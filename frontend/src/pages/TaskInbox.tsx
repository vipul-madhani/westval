import { useEffect, useState } from 'react'
import {
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tabs,
  Tab,
  Badge
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function TaskInbox() {
  const navigate = useNavigate()
  const [tasks, setTasks] = useState<any[]>([])
  const [tabValue, setTabValue] = useState(0)
  const [selectedTask, setSelectedTask] = useState<any>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [comments, setComments] = useState('')

  useEffect(() => {
    fetchTasks()
  }, [tabValue])

  const fetchTasks = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const status = tabValue === 0 ? 'PENDING' : 'COMPLETED'
      const response = await axios.get(`/api/workflow/tasks/my-tasks?status=${status}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setTasks(response.data.tasks || [])
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    }
  }

  const handleTaskAction = async (action: string) => {
    try {
      const token = localStorage.getItem('access_token')
      await axios.post(
        `/api/workflow/tasks/${selectedTask.id}/complete`,
        { action, comments },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      setDialogOpen(false)
      setComments('')
      fetchTasks()
      alert(`Task ${action.toLowerCase()} successfully!`)
    } catch (error) {
      console.error('Failed to complete task:', error)
    }
  }

  const pendingCount = tasks.filter(t => t.status === 'PENDING').length

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            My Task Inbox
            {pendingCount > 0 && (
              <Badge badgeContent={pendingCount} color="error" sx={{ ml: 2 }} />
            )}
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>Dashboard</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Paper>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label={`Pending (${pendingCount})`} />
            <Tab label="Completed" />
          </Tabs>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Task</TableCell>
                  <TableCell>Entity</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tasks.map((task) => (
                  <TableRow key={task.id} hover>
                    <TableCell>{task.stage_name}</TableCell>
                    <TableCell>
                      {task.entity_type}
                      <br />
                      <Typography variant="caption" color="text.secondary">
                        ID: {task.entity_id.substring(0, 8)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {new Date(task.due_date).toLocaleString()}
                      {task.is_overdue && (
                        <Chip label="OVERDUE" color="error" size="small" sx={{ ml: 1 }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip label={task.status} color="primary" size="small" />
                    </TableCell>
                    <TableCell>
                      {task.status === 'PENDING' && (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => {
                            setSelectedTask(task)
                            setDialogOpen(true)
                          }}
                        >
                          Review
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Container>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Review Task: {selectedTask?.stage_name}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Comments"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            sx={{ mt: 2 }}
            placeholder="Add your review comments..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="outlined"
            color="error"
            onClick={() => handleTaskAction('REJECTED')}
          >
            Reject
          </Button>
          <Button
            variant="contained"
            color="success"
            onClick={() => handleTaskAction('APPROVED')}
          >
            Approve
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default TaskInbox