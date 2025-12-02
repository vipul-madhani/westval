import React, { useState } from 'react';
import axios from 'axios';
import './SystemValidationUI.css';

const SystemValidationUI = ({ token }) => {
  const [activeTab, setActiveTab] = useState('protocol');
  const [protocolName, setProtocolName] = useState('');
  const [phase, setPhase] = useState('IQ');
  const [scope, setScope] = useState('');
  const [criteria, setCriteria] = useState('');
  const [testCase, setTestCase] = useState('');
  const [expected, setExpected] = useState('');
  const [actual, setActual] = useState('');
  const [protocolId, setProtocolId] = useState('');
  const [protocolResult, setProtocolResult] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [summary, setSummary] = useState(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [auditReport, setAuditReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCreateProtocol = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('/api/validation/protocol', {
        protocol_name: protocolName,
        phase,
        scope,
        acceptance_criteria: criteria
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setProtocolResult(response.data);
      setProtocolName('');
      setScope('');
      setCriteria('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create protocol');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteTest = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`/api/validation/test/${protocolId}`, {
        test_case: testCase,
        expected_outcome: expected,
        actual_outcome: actual
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setTestResult(response.data);
      setTestCase('');
      setExpected('');
      setActual('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to execute test');
    } finally {
      setLoading(false);
    }
  };

  const handleGetSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/validation/summary/${protocolId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setSummary(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get summary');
    } finally {
      setLoading(false);
    }
  };

  const handleGetAuditReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      const response = await axios.get(`/api/validation/audit-report?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setAuditReport(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get audit report');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveProtocol = async () => {
    try {
      setLoading(true);
      setError(null);
      await axios.post(`/api/validation/approve/${protocolId}`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      alert('Protocol approved successfully!');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to approve protocol');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="system-validation-container">
      <h2>System Validation & Comprehensive Audit</h2>
      
      <div className="tabs">
        <button className={activeTab === 'protocol' ? 'active' : ''} onClick={() => setActiveTab('protocol')}>
          Create Protocol
        </button>
        <button className={activeTab === 'test' ? 'active' : ''} onClick={() => setActiveTab('test')}>
          Execute Tests
        </button>
        <button className={activeTab === 'summary' ? 'active' : ''} onClick={() => setActiveTab('summary')}>
          Protocol Summary
        </button>
        <button className={activeTab === 'audit' ? 'active' : ''} onClick={() => setActiveTab('audit')}>
          Audit Report
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {loading && <div className="loading">Processing...</div>}

      {activeTab === 'protocol' && (
        <div className="tab-content">
          <div className="form-group">
            <label>Protocol Name:</label>
            <input type="text" value={protocolName} onChange={(e) => setProtocolName(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Phase:</label>
            <select value={phase} onChange={(e) => setPhase(e.target.value)}>
              <option value="IQ">Installation Qualification (IQ)</option>
              <option value="OQ">Operational Qualification (OQ)</option>
              <option value="PQ">Performance Qualification (PQ)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Scope:</label>
            <textarea value={scope} onChange={(e) => setScope(e.target.value)} rows="4" />
          </div>
          <div className="form-group">
            <label>Acceptance Criteria:</label>
            <textarea value={criteria} onChange={(e) => setCriteria(e.target.value)} rows="4" />
          </div>
          <button onClick={handleCreateProtocol} className="btn-primary" disabled={loading}>
            Create Protocol
          </button>
          {protocolResult && (
            <div className="result">
              <h4>Protocol Created:</h4>
              <p>ID: {protocolResult.protocol_id}</p>
              <p>Name: {protocolResult.name}</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'test' && (
        <div className="tab-content">
          <div className="form-group">
            <label>Protocol ID:</label>
            <input type="number" value={protocolId} onChange={(e) => setProtocolId(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Test Case:</label>
            <input type="text" value={testCase} onChange={(e) => setTestCase(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Expected Outcome:</label>
            <textarea value={expected} onChange={(e) => setExpected(e.target.value)} rows="3" />
          </div>
          <div className="form-group">
            <label>Actual Outcome:</label>
            <textarea value={actual} onChange={(e) => setActual(e.target.value)} rows="3" />
          </div>
          <button onClick={handleExecuteTest} className="btn-primary" disabled={loading}>
            Execute Test
          </button>
          {testResult && (
            <div className="result">
              <h4>Test Result:</h4>
              <p>Result ID: {testResult.result_id}</p>
              <p>Status: {testResult.passed ? 'PASSED' : 'FAILED'}</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'summary' && (
        <div className="tab-content">
          <div className="form-group">
            <label>Protocol ID:</label>
            <input type="number" value={protocolId} onChange={(e) => setProtocolId(e.target.value)} />
          </div>
          <button onClick={handleGetSummary} className="btn-primary" disabled={loading}>
            Get Summary
          </button>
          <button onClick={handleApproveProtocol} className="btn-secondary" disabled={loading}>
            Approve Protocol
          </button>
          {summary && (
            <div className="result">
              <h4>Validation Summary:</h4>
              <p>Protocol: {summary.protocol_name}</p>
              <p>Phase: {summary.phase}</p>
              <p>Total Tests: {summary.total_tests}</p>
              <p>Passed: {summary.passed_tests}</p>
              <p>Pass Rate: {summary.pass_rate.toFixed(2)}%</p>
              <p>Status: {summary.status}</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="tab-content">
          <div className="form-group">
            <label>Start Date:</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label>End Date:</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <button onClick={handleGetAuditReport} className="btn-primary" disabled={loading}>
            Generate Report
          </button>
          {auditReport && (
            <div className="result">
              <h4>Audit Report:</h4>
              <p>Total Records: {auditReport.total_audit_records}</p>
              <p>Audit Types: {Object.keys(auditReport.audit_types).length}</p>
              <p>By User: {Object.keys(auditReport.by_user).length} users</p>
              <p>By Entity: {Object.keys(auditReport.by_entity).length} entities</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SystemValidationUI;
