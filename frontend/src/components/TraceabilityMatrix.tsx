import { useEffect, useRef, useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  ToggleButton,
  ToggleButtonGroup,
  Alert
} from '@mui/material'
import {
  AccountTree,
  TableChart,
  Download
} from '@mui/icons-material'
import * as d3 from 'd3'

interface Props {
  projectId: string
}

function TraceabilityMatrix({ projectId }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [viewMode, setViewMode] = useState<'graph' | 'table'>('graph')
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    fetchTraceabilityData()
  }, [projectId])

  useEffect(() => {
    if (data && viewMode === 'graph') {
      renderGraph()
    }
  }, [data, viewMode])

  const fetchTraceabilityData = async () => {
    // Mock data - replace with actual API call
    const mockData = {
      requirements: [
        { id: 'REQ-001', title: 'User Login', status: 'Verified', criticality: 'Critical' },
        { id: 'REQ-002', title: 'Data Export', status: 'Verified', criticality: 'High' },
        { id: 'REQ-003', title: 'Password Reset', status: 'Not Tested', criticality: 'Medium' },
        { id: 'REQ-004', title: 'User Profile', status: 'Verified', criticality: 'Low' },
        { id: 'REQ-005', title: 'Admin Dashboard', status: 'Failed', criticality: 'Critical' }
      ],
      testCases: [
        { id: 'TC-001', title: 'Login Test', status: 'Passed', linkedReqs: ['REQ-001'] },
        { id: 'TC-002', title: 'Export Test', status: 'Passed', linkedReqs: ['REQ-002'] },
        { id: 'TC-003', title: 'Profile Test', status: 'Passed', linkedReqs: ['REQ-004'] },
        { id: 'TC-004', title: 'Admin Test', status: 'Failed', linkedReqs: ['REQ-005'] }
      ],
      links: [
        { source: 'REQ-001', target: 'TC-001', status: 'passed' },
        { source: 'REQ-002', target: 'TC-002', status: 'passed' },
        { source: 'REQ-004', target: 'TC-003', status: 'passed' },
        { source: 'REQ-005', target: 'TC-004', status: 'failed' }
      ]
    }
    setData(mockData)
  }

  const renderGraph = () => {
    if (!svgRef.current || !data) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 800
    const height = 600
    const margin = { top: 20, right: 20, bottom: 20, left: 20 }

    // Create nodes array
    const nodes: any[] = []
    
    data.requirements.forEach((req: any) => {
      nodes.push({
        id: req.id,
        title: req.title,
        type: 'requirement',
        status: req.status,
        criticality: req.criticality
      })
    })
    
    data.testCases.forEach((tc: any) => {
      nodes.push({
        id: tc.id,
        title: tc.title,
        type: 'test',
        status: tc.status
      })
    })

    // Create links array
    const links = data.links.map((link: any) => ({
      source: link.source,
      target: link.target,
      status: link.status
    }))

    // Color scale
    const getNodeColor = (node: any) => {
      if (node.type === 'requirement') {
        if (node.status === 'Not Tested') return '#ff9800'
        if (node.status === 'Failed') return '#f44336'
        return '#4caf50'
      } else {
        if (node.status === 'Failed') return '#f44336'
        if (node.status === 'Passed') return '#4caf50'
        return '#9e9e9e'
      }
    }

    // Create simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50))

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Add zoom
    const zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom as any)

    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', (d: any) => d.status === 'passed' ? '#4caf50' : '#f44336')
      .attr('stroke-width', 2)
      .attr('opacity', 0.6)

    // Draw nodes
    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any)

    // Add circles
    node.append('circle')
      .attr('r', (d: any) => d.type === 'requirement' ? 25 : 20)
      .attr('fill', (d: any) => getNodeColor(d))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)

    // Add labels
    node.append('text')
      .text((d: any) => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .attr('fill', '#fff')
      .style('font-size', '10px')
      .style('font-weight', 'bold')

    // Add tooltips
    node.append('title')
      .text((d: any) => `${d.id}: ${d.title}\nStatus: ${d.status}`)

    // Update positions
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
    })

    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      event.subject.fx = event.subject.x
      event.subject.fy = event.subject.y
    }

    function dragged(event: any) {
      event.subject.fx = event.x
      event.subject.fy = event.y
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0)
      event.subject.fx = null
      event.subject.fy = null
    }

    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 150}, 20)`)

    const legendData = [
      { label: 'Requirement', color: '#4caf50', shape: 'circle' },
      { label: 'Test Case', color: '#2196f3', shape: 'circle' },
      { label: 'Passed', color: '#4caf50', shape: 'line' },
      { label: 'Failed', color: '#f44336', shape: 'line' },
      { label: 'Not Tested', color: '#ff9800', shape: 'circle' }
    ]

    legendData.forEach((item, i) => {
      const legendItem = legend.append('g')
        .attr('transform', `translate(0, ${i * 25})`)

      if (item.shape === 'circle') {
        legendItem.append('circle')
          .attr('r', 8)
          .attr('fill', item.color)
      } else {
        legendItem.append('line')
          .attr('x1', -8)
          .attr('x2', 8)
          .attr('stroke', item.color)
          .attr('stroke-width', 3)
      }

      legendItem.append('text')
        .attr('x', 15)
        .attr('y', 5)
        .text(item.label)
        .style('font-size', '12px')
    })
  }

  const calculateCoverage = () => {
    if (!data) return { total: 0, tested: 0, passed: 0, failed: 0, percentage: 0 }

    const total = data.requirements.length
    const tested = data.requirements.filter((r: any) => r.status !== 'Not Tested').length
    const passed = data.requirements.filter((r: any) => r.status === 'Verified').length
    const failed = data.requirements.filter((r: any) => r.status === 'Failed').length
    const percentage = Math.round((passed / total) * 100)

    return { total, tested, passed, failed, percentage }
  }

  const coverage = calculateCoverage()

  const exportToExcel = () => {
    alert('Exporting traceability matrix to Excel...')
    // Implementation would generate Excel file
  }

  return (
    <Box>
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Requirements
              </Typography>
              <Typography variant="h3">{coverage.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Tested
              </Typography>
              <Typography variant="h3" color="primary">
                {coverage.tested}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Coverage
              </Typography>
              <Typography variant="h3" color="success.main">
                {coverage.percentage}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Gaps
              </Typography>
              <Typography variant="h3" color="warning.main">
                {coverage.total - coverage.tested}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {data && data.requirements.filter((r: any) => r.status === 'Not Tested').length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Untested Requirements Found:
          </Typography>
          {data.requirements
            .filter((r: any) => r.status === 'Not Tested')
            .map((r: any) => (
              <Chip key={r.id} label={r.id} size="small" sx={{ mr: 1, mt: 1 }} />
            ))}
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Requirements Traceability Matrix</Typography>
          <Box>
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={(e, newMode) => newMode && setViewMode(newMode)}
              size="small"
              sx={{ mr: 2 }}
            >
              <ToggleButton value="graph">
                <AccountTree sx={{ mr: 1 }} /> Graph
              </ToggleButton>
              <ToggleButton value="table">
                <TableChart sx={{ mr: 1 }} /> Table
              </ToggleButton>
            </ToggleButtonGroup>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={exportToExcel}
            >
              Export
            </Button>
          </Box>
        </Box>
      </Paper>

      {viewMode === 'graph' ? (
        <Paper sx={{ p: 2, overflow: 'auto' }}>
          <svg
            ref={svgRef}
            width="100%"
            height="600"
            style={{ border: '1px solid #e0e0e0' }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            Interactive Graph: Drag nodes to reposition • Scroll to zoom • Hover for details
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Requirement ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Criticality</TableCell>
                <TableCell>Test Cases</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Coverage</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data?.requirements.map((req: any) => {
                const linkedTests = data.testCases.filter((tc: any) =>
                  tc.linkedReqs.includes(req.id)
                )
                return (
                  <TableRow key={req.id}>
                    <TableCell>{req.id}</TableCell>
                    <TableCell>{req.title}</TableCell>
                    <TableCell>
                      <Chip label={req.criticality} size="small" />
                    </TableCell>
                    <TableCell>
                      {linkedTests.map((tc: any) => (
                        <Chip
                          key={tc.id}
                          label={tc.id}
                          size="small"
                          sx={{ mr: 0.5 }}
                        />
                      ))}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={req.status}
                        color={
                          req.status === 'Verified'
                            ? 'success'
                            : req.status === 'Failed'
                            ? 'error'
                            : 'warning'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {linkedTests.length > 0 ? (
                        <Chip label="Complete" color="success" size="small" />
                      ) : (
                        <Chip label="Gap" color="warning" size="small" />
                      )}
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}

export default TraceabilityMatrix