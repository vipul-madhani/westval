import {
  Container,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Button,
  Paper,
  Grid,
  List,
  ListItem,
  ListItemText
} from '@mui/material'
import { useNavigate } from 'react-router-dom'

function Compliance() {
  const navigate = useNavigate()

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Compliance Dashboard
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>Dashboard</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>Regulatory Compliance</Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>21 CFR Part 11 Compliance</Typography>
              <List>
                <ListItem>
                  <ListItemText primary="Electronic Signatures" secondary="Implemented" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Audit Trails" secondary="Complete" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Version Control" secondary="Active" />
                </ListItem>
              </List>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>GAMP 5 Guidelines</Typography>
              <List>
                <ListItem>
                  <ListItemText primary="Risk-Based Approach" secondary="Supported" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Category Assessment" secondary="Available" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Lifecycle Management" secondary="Complete" />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}

export default Compliance