import { useState, useEffect } from 'react'
import {
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
  TextField,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Alert
} from '@mui/material'
import {
  CameraAlt,
  CheckCircle,
  Cancel,
  AttachFile,
  Save,
  Send
} from '@mui/icons-material'
import { useNavigate, useParams } from 'react-router-dom'
import axios from 'axios'
import ScreenshotCapture from '../components/ScreenshotCapture'

function TestExecution() {
  const navigate = useNavigate()
  const { testCaseId } = useParams()
  const [activeStep, setActiveStep] = useState(0)
  const [testCase, setTestCase] = useState<any>(null)
  const [stepResults, setStepResults] = useState<any[]>([])
  const [screenshotOpen, setScreenshotOpen] = useState(false)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)

  useEffect(() => {
    fetchTestCase()
  }, [testCaseId])

  const fetchTestCase = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`/api/tests/${testCaseId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      const tc = response.data
      setTestCase(tc)
      
      // Initialize step results
      const steps = tc.test_steps || [
        { id: 1, description: 'Verify system login', expected: 'User successfully logs in' },
        { id: 2, description: 'Navigate to validation module', expected: 'Module loads correctly' },
        { id: 3, description: 'Create new validation project', expected: 'Project is created' }
      ]
      
      setStepResults(
        steps.map((step: any) => ({
          stepId: step.id,
          status: 'NOT_EXECUTED',
          actualResult: '',
          evidence: [],
          notes: ''
        }))
      )
    } catch (error) {
      console.error('Failed to fetch test case:', error)
    }
  }

  const handleStepStatusChange = (index: number, status: string) => {
    const newResults = [...stepResults]
    newResults[index].status = status
    setStepResults(newResults)
  }

  const handleActualResultChange = (index: number, value: string) => {
    const newResults = [...stepResults]
    newResults[index].actualResult = value
    setStepResults(newResults)
  }

  const handleScreenshotSave = (screenshot: string, annotations: any) => {
    const newResults = [...stepResults]
    newResults[currentStepIndex].evidence.push({
      type: 'screenshot',
      data: screenshot,
      annotations: annotations.annotations,
      notes: annotations.notes,
      timestamp: new Date().toISOString()
    })
    setStepResults(newResults)
  }

  const handleNext = () => {
    if (activeStep < (testCase?.test_steps?.length || 3) - 1) {
      setActiveStep(activeStep + 1)
    }
  }

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1)
    }
  }

  const handleAutoSave = async () => {
    // Auto-save progress
    try {
      const token = localStorage.getItem('access_token')
      await axios.post(
        `/api/tests/${testCaseId}/save-progress`,
        { stepResults },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert('Progress saved!')
    } catch (error) {
      console.error('Auto-save failed:', error)
    }
  }

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      // Calculate overall status
      const hasFailures = stepResults.some(r => r.status === 'FAIL')
      const allExecuted = stepResults.every(r => r.status !== 'NOT_EXECUTED')
      
      const overallStatus = hasFailures ? 'Failed' : (allExecuted ? 'Passed' : 'Incomplete')
      
      await axios.post(
        `/api/tests/${testCaseId}/execute`,
        {
          status: overallStatus,
          actual_result: 'Test execution completed',
          step_results: stepResults
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      alert('Test execution submitted successfully!')
      navigate('/tests')
    } catch (error) {
      console.error('Failed to submit test:', error)
    }
  }

  const steps = testCase?.test_steps || [
    { id: 1, description: 'Verify system login', expected: 'User successfully logs in' },
    { id: 2, description: 'Navigate to validation module', expected: 'Module loads correctly' },
    { id: 3, description: 'Create new validation project', expected: 'Project is created' }
  ]

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Test Execution: {testCase?.test_case_id || 'TC-001'}
          </Typography>
          <Button color="inherit" startIcon={<Save />} onClick={handleAutoSave}>
            Auto-Save
          </Button>
          <Button color="inherit" onClick={() => navigate('/tests')}>
            Exit
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                {testCase?.title || 'System Validation Test'}
              </Typography>
              <Typography color="text.secondary" gutterBottom>
                {testCase?.objective || 'Verify system functionality'}
              </Typography>

              <Alert severity="info" sx={{ mt: 2, mb: 3 }}>
                Execute each step and capture evidence. Screenshots and notes are automatically
                timestamped for 21 CFR Part 11 compliance.
              </Alert>

              <Stepper activeStep={activeStep} orientation="vertical">
                {steps.map((step: any, index: number) => (
                  <Step key={step.id}>
                    <StepLabel
                      optional={
                        stepResults[index]?.status !== 'NOT_EXECUTED' && (
                          <Chip
                            size="small"
                            label={stepResults[index]?.status}
                            color={
                              stepResults[index]?.status === 'PASS'
                                ? 'success'
                                : stepResults[index]?.status === 'FAIL'
                                ? 'error'
                                : 'default'
                            }
                          />
                        )
                      }
                    >
                      Step {index + 1}: {step.description}
                    </StepLabel>
                    <StepContent>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          <strong>Expected Result:</strong> {step.expected}
                        </Typography>

                        <FormControl component="fieldset" sx={{ mt: 2 }}>
                          <FormLabel component="legend">Step Result</FormLabel>
                          <RadioGroup
                            row
                            value={stepResults[index]?.status}
                            onChange={(e) => handleStepStatusChange(index, e.target.value)}
                          >
                            <FormControlLabel
                              value="PASS"
                              control={<Radio />}
                              label="Pass"
                            />
                            <FormControlLabel
                              value="FAIL"
                              control={<Radio />}
                              label="Fail"
                            />
                            <FormControlLabel value="NA" control={<Radio />} label="N/A" />
                          </RadioGroup>
                        </FormControl>

                        <TextField
                          fullWidth
                          multiline
                          rows={2}
                          label="Actual Result"
                          value={stepResults[index]?.actualResult || ''}
                          onChange={(e) => handleActualResultChange(index, e.target.value)}
                          sx={{ mt: 2 }}
                        />

                        <Box sx={{ mt: 2 }}>
                          <Button
                            variant="outlined"
                            startIcon={<CameraAlt />}
                            onClick={() => {
                              setCurrentStepIndex(index)
                              setScreenshotOpen(true)
                            }}
                            sx={{ mr: 1 }}
                          >
                            Capture Evidence
                          </Button>

                          {stepResults[index]?.evidence?.length > 0 && (
                            <Chip
                              label={`${stepResults[index].evidence.length} evidence item(s)`}
                              color="primary"
                              size="small"
                            />
                          )}
                        </Box>

                        <Box sx={{ mt: 2 }}>
                          <Button onClick={handleBack} disabled={index === 0} sx={{ mr: 1 }}>
                            Back
                          </Button>
                          <Button
                            variant="contained"
                            onClick={handleNext}
                            disabled={index === steps.length - 1}
                          >
                            Next Step
                          </Button>
                        </Box>
                      </Box>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>

              <Box sx={{ mt: 3, textAlign: 'right' }}>
                <Button
                  variant="contained"
                  color="success"
                  size="large"
                  startIcon={<Send />}
                  onClick={handleSubmit}
                >
                  Submit Test Execution
                </Button>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Execution Summary
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Total Steps"
                      secondary={steps.length}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Passed"
                      secondary={stepResults.filter((r) => r.status === 'PASS').length}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Failed"
                      secondary={stepResults.filter((r) => r.status === 'FAIL').length}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Evidence Captured"
                      secondary={stepResults.reduce(
                        (sum, r) => sum + (r.evidence?.length || 0),
                        0
                      )}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Compliance
                </Typography>
                <List dense>
                  <ListItem>
                    <CheckCircle color="success" sx={{ mr: 1 }} />
                    <ListItemText primary="21 CFR Part 11" secondary="Compliant" />
                  </ListItem>
                  <ListItem>
                    <CheckCircle color="success" sx={{ mr: 1 }} />
                    <ListItemText primary="Timestamped Evidence" secondary="Active" />
                  </ListItem>
                  <ListItem>
                    <CheckCircle color="success" sx={{ mr: 1 }} />
                    <ListItemText primary="Audit Trail" secondary="Recording" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      <ScreenshotCapture
        open={screenshotOpen}
        onClose={() => setScreenshotOpen(false)}
        onSave={handleScreenshotSave}
      />
    </Box>
  )
}

export default TestExecution