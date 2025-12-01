import {
  Container,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Button
} from '@mui/material'
import { useNavigate } from 'react-router-dom'

function RiskAssessment() {
  const navigate = useNavigate()

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Risk Assessment
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>Dashboard</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>Risk Assessment Module</Typography>
        <Typography>Risk assessment features coming soon...</Typography>
      </Container>
    </Box>
  )
}

export default RiskAssessment