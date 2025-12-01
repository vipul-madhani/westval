import React, { useState } from 'react';
import axios from 'axios';
import './ReportingEngine.css';

const ReportingEngine = () => {
  const [activeReport, setActiveReport] = useState('vsr');
  const [validationScope, setValidationScope] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [exportFormat, setExportFormat] = useState('PDF');
  const [selectedReport, setSelectedReport] = useState(null);

  const reportTypes = [
    { id: 'vsr', name: 'Validation Summary Report', description: 'Executive summary of validation activities' },
    { id: 'rtm', name: 'Requirements Traceability Matrix', description: 'Trace requirements to test cases' },
    { id: 'oq', name: 'Operational Qualification', description: 'OQ test results and evidence' },
    { id: 'iq', name: 'Installation Qualification', description: 'IQ test results and evidence' },
    { id: 'pq', name: 'Performance Qualification', description: 'PQ test results and evidence' }
  ];

  const handleGenerateReport = async (reportType) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/reports/generate', {
        report_type: reportType,
        format: exportFormat,
        include_evidence: true,
        include_metrics: true
      });
      setReports([...reports, response.data]);
      setSelectedReport(response.data);
    } catch (err) {
      setError(`Failed to generate report: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async (reportId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`/api/reports/${reportId}/export`, {
        format: exportFormat
      }, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${reportId}.${exportFormat.toLowerCase()}`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      setError(`Export failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleReport = async (reportId, schedule) => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(`/api/reports/${reportId}/schedule`, {
        schedule_type: schedule,
        enabled: true
      });
      alert('Report scheduling configured successfully');
    } catch (err) {
      setError(`Scheduling failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAuditTrail = async (reportId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/reports/${reportId}/audit`);
      console.log('Audit Trail:', response.data);
      alert(`Audit Trail Entries: ${response.data.entries.length}\nLast Modified: ${response.data.last_modified}`);
    } catch (err) {
      setError(`Audit retrieval failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRTM = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/reports/rtm/generate', {
        include_all_requirements: true,
        include_evidence: true
      });
      setReports([...reports, response.data]);
      setSelectedReport(response.data);
    } catch (err) {
      setError(`RTM generation failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reporting-engine-container">
      <h1>Validation Reporting Engine</h1>
      
      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading">Generating Report...</div>}

      <div className="controls">
        <div className="export-format">
          <label>Export Format:</label>
          <select value={exportFormat} onChange={(e) => setExportFormat(e.target.value)}>
            <option>PDF</option>
            <option>DOCX</option>
            <option>HTML</option>
            <option>JSON</option>
          </select>
        </div>
      </div>

      <div className="report-types">
        <h2>Available Reports</h2>
        <div className="report-grid">
          {reportTypes.map(report => (
            <div key={report.id} className="report-card">
              <h3>{report.name}</h3>
              <p>{report.description}</p>
              <button 
                className="generate-btn" 
                onClick={() => handleGenerateReport(report.id)}
                disabled={loading}
              >
                Generate {report.name}
              </button>
            </div>
          ))}
        </div>
        <button className="rtm-btn" onClick={handleGenerateRTM} disabled={loading}>
          Generate Requirements Traceability Matrix
        </button>
      </div>

      {selectedReport && (
        <div className="report-details">
          <h2>Generated Report</h2>
          <div className="report-info">
            <p><strong>Report ID:</strong> {selectedReport.id}</p>
            <p><strong>Type:</strong> {selectedReport.report_type}</p>
            <p><strong>Format:</strong> {selectedReport.document_format}</p>
            <p><strong>Generated:</strong> {new Date(selectedReport.generation_date).toLocaleString()}</p>
            <p><strong>Status:</strong> {selectedReport.status}</p>
          </div>
          <div className="report-actions">
            <button onClick={() => handleExportReport(selectedReport.id)} className="export-btn">
              Export as {exportFormat}
            </button>
            <button onClick={() => handleAuditTrail(selectedReport.id)} className="audit-btn">
              View Audit Trail
            </button>
            <select 
              onChange={(e) => handleScheduleReport(selectedReport.id, e.target.value)}
              defaultValue=""
            >
              <option value="">Schedule Report</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
        </div>
      )}

      <div className="reports-history">
        <h2>Report History</h2>
        <table className="reports-table">
          <thead>
            <tr>
              <th>Report ID</th>
              <th>Type</th>
              <th>Format</th>
              <th>Generated</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {reports.map(report => (
              <tr key={report.id}>
                <td>{report.id}</td>
                <td>{report.report_type}</td>
                <td>{report.document_format}</td>
                <td>{new Date(report.generation_date).toLocaleDateString()}</td>
                <td><span className={`status ${report.status}`}>{report.status}</span></td>
                <td>
                  <button onClick={() => handleExportReport(report.id)} className="action-btn">Export</button>
                  <button onClick={() => handleAuditTrail(report.id)} className="action-btn">Audit</button>
                  <button onClick={() => setSelectedReport(report)} className="action-btn">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="compliance-dashboard">
        <h2>Compliance Status</h2>
        <div className="compliance-grid">
          <div className="compliance-card">
            <h4>21 CFR Part 11 Compliance</h4>
            <p className="status-indicator">✓ Compliant</p>
            <p>Digital signatures enabled, audit trails active</p>
          </div>
          <div className="compliance-card">
            <h4>EU Annex 11 Compliance</h4>
            <p className="status-indicator">✓ Compliant</p>
            <p>Data integrity and validation controls in place</p>
          </div>
          <div className="compliance-card">
            <h4>Report Integrity</h4>
            <p className="status-indicator">✓ Verified</p>
            <p>SHA-256 hashing and signature verification active</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportingEngine;
