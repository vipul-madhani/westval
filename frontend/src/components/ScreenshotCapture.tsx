import { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  IconButton,
  Toolbar,
  Tooltip,
  TextField
} from '@mui/material'
import {
  CameraAlt,
  ArrowForward,
  Circle,
  Square,
  Create,
  TextFields,
  Highlight,
  Undo,
  Save,
  Close
} from '@mui/icons-material'

interface Props {
  open: boolean
  onClose: () => void
  onSave: (screenshot: string, annotations: any) => void
}

function ScreenshotCapture({ open, onClose, onSave }: Props) {
  const [screenshot, setScreenshot] = useState<string | null>(null)
  const [isAnnotating, setIsAnnotating] = useState(false)
  const [tool, setTool] = useState('arrow')
  const [annotations, setAnnotations] = useState<any[]>([])
  const [isDrawing, setIsDrawing] = useState(false)
  const [currentAnnotation, setCurrentAnnotation] = useState<any>(null)
  const [notes, setNotes] = useState('')

  const captureScreen = async () => {
    try {
      // Use browser screenshot API
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { mediaSource: 'screen' }
      })

      const video = document.createElement('video')
      video.srcObject = stream
      video.play()

      // Wait for video to be ready
      await new Promise(resolve => {
        video.onloadedmetadata = resolve
      })

      // Capture frame
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx?.drawImage(video, 0, 0)

      // Stop stream
      stream.getTracks().forEach(track => track.stop())

      // Get image data
      const imageData = canvas.toDataURL('image/png')
      setScreenshot(imageData)
      setIsAnnotating(true)
    } catch (error) {
      console.error('Failed to capture screenshot:', error)
      alert('Screenshot capture failed. Please try again.')
    }
  }

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isAnnotating) return

    const canvas = e.currentTarget
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    setIsDrawing(true)
    setCurrentAnnotation({
      tool,
      startX: x,
      startY: y,
      endX: x,
      endY: y,
      color: 'red',
      width: 3
    })
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !currentAnnotation) return

    const canvas = e.currentTarget
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    setCurrentAnnotation({
      ...currentAnnotation,
      endX: x,
      endY: y
    })

    // Redraw canvas
    drawAnnotations(canvas)
  }

  const handleMouseUp = () => {
    if (currentAnnotation) {
      setAnnotations([...annotations, currentAnnotation])
      setCurrentAnnotation(null)
    }
    setIsDrawing(false)
  }

  const drawAnnotations = (canvas: HTMLCanvasElement) => {
    const ctx = canvas.getContext('2d')
    if (!ctx || !screenshot) return

    // Clear and redraw
    const img = new Image()
    img.src = screenshot
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

      // Draw saved annotations
      annotations.forEach(ann => drawAnnotation(ctx, ann))

      // Draw current annotation
      if (currentAnnotation) {
        drawAnnotation(ctx, currentAnnotation)
      }
    }
  }

  const drawAnnotation = (ctx: CanvasRenderingContext2D, ann: any) => {
    ctx.strokeStyle = ann.color
    ctx.lineWidth = ann.width
    ctx.fillStyle = 'rgba(255, 0, 0, 0.2)'

    switch (ann.tool) {
      case 'arrow':
        drawArrow(ctx, ann.startX, ann.startY, ann.endX, ann.endY)
        break
      case 'circle':
        const radius = Math.sqrt(
          Math.pow(ann.endX - ann.startX, 2) + Math.pow(ann.endY - ann.startY, 2)
        )
        ctx.beginPath()
        ctx.arc(ann.startX, ann.startY, radius, 0, 2 * Math.PI)
        ctx.stroke()
        break
      case 'rectangle':
        ctx.strokeRect(
          ann.startX,
          ann.startY,
          ann.endX - ann.startX,
          ann.endY - ann.startY
        )
        break
      case 'highlight':
        ctx.fillRect(
          ann.startX,
          ann.startY,
          ann.endX - ann.startX,
          ann.endY - ann.startY
        )
        break
    }
  }

  const drawArrow = (
    ctx: CanvasRenderingContext2D,
    x1: number,
    y1: number,
    x2: number,
    y2: number
  ) => {
    const headlen = 15
    const angle = Math.atan2(y2 - y1, x2 - x1)

    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.lineTo(
      x2 - headlen * Math.cos(angle - Math.PI / 6),
      y2 - headlen * Math.sin(angle - Math.PI / 6)
    )
    ctx.moveTo(x2, y2)
    ctx.lineTo(
      x2 - headlen * Math.cos(angle + Math.PI / 6),
      y2 - headlen * Math.sin(angle + Math.PI / 6)
    )
    ctx.stroke()
  }

  const handleSave = () => {
    if (screenshot) {
      onSave(screenshot, { annotations, notes })
      handleClose()
    }
  }

  const handleClose = () => {
    setScreenshot(null)
    setIsAnnotating(false)
    setAnnotations([])
    setNotes('')
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        Screenshot Capture & Annotation
        <IconButton
          onClick={handleClose}
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        {!screenshot ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<CameraAlt />}
              onClick={captureScreen}
            >
              Capture Screen
            </Button>
          </Box>
        ) : (
          <Box>
            {isAnnotating && (
              <Toolbar sx={{ mb: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Tooltip title="Arrow">
                  <IconButton
                    color={tool === 'arrow' ? 'primary' : 'default'}
                    onClick={() => setTool('arrow')}
                  >
                    <ArrowForward />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Circle">
                  <IconButton
                    color={tool === 'circle' ? 'primary' : 'default'}
                    onClick={() => setTool('circle')}
                  >
                    <Circle />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Rectangle">
                  <IconButton
                    color={tool === 'rectangle' ? 'primary' : 'default'}
                    onClick={() => setTool('rectangle')}
                  >
                    <Square />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Highlight">
                  <IconButton
                    color={tool === 'highlight' ? 'primary' : 'default'}
                    onClick={() => setTool('highlight')}
                  >
                    <Highlight />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Undo">
                  <IconButton
                    onClick={() => setAnnotations(annotations.slice(0, -1))}
                    disabled={annotations.length === 0}
                  >
                    <Undo />
                  </IconButton>
                </Tooltip>
              </Toolbar>
            )}

            <canvas
              width={800}
              height={600}
              style={{
                border: '1px solid #ccc',
                width: '100%',
                cursor: isAnnotating ? 'crosshair' : 'default'
              }}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
            />

            <TextField
              fullWidth
              multiline
              rows={3}
              label="Notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              sx={{ mt: 2 }}
              placeholder="Add notes about this screenshot..."
            />
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        {screenshot && (
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSave}
          >
            Save Evidence
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}

export default ScreenshotCapture