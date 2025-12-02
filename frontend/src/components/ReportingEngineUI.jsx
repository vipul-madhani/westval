import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ReportingEngineUI = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [reports, setReports] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [templateId, setTemplateId] = useState('');
  const [frequency, setFrequency] = useState('DAILY');
  const [selectedReport, setSelectedReport] = useState(null);

  const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` };

  const createReport = async () => {
    try {
      setLoading(true);
      const res = await axios.post('/api/reporting/reports', 
        { template_id: templateId, filters: {} }, { headers }
      );
      setReports([...reports, res.data]);
      setTemplateId('');
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Error creating report');
    } finally {
      setLoading(false);
    }
  };

  const scheduleReport = async (reportId) => {
    try {
      setLoading(true);
      const res = await axios.post(`/api/reporting/reports/${reportId}/schedule`,
        { frequency }, { headers }
      );
      setSchedules([...schedules, res.data]);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Error scheduling report');
    } finally {
      setLoading(false);
    }
  };

  const executeSchedule = async (scheduleId) => {
    try {
      setLoading(true);
      const res = await axios.post(`/api/reporting/schedules/${scheduleId}/execute`, {}, { headers });
      setError(null);
      alert('Report executed successfully');
    } catch (err) {
      setError(err.response?.data?.error || 'Error executing report');
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async (reportId) => {
    try {
      const res = await axios.get(`/api/reporting/reports/${reportId}/export?format=csv`, { headers, responseType: 'blob' });
      const url = window.URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${reportId}.csv`;
      a.click();
    } catch (err) {
      setError('Error exporting report');
    }
  };

  return (
    <div className="reporting-container">
      <h1>Reporting Engine</h1>
      {error && <div className="alert alert-error">{error}</div>}
      
      <div className="tabs">
        <button onClick={() => setActiveTab('create')} className={activeTab === 'create' ? 'active' : ''}>Create Report</button>
        <button onClick={() => setActiveTab('manage')} className={activeTab === 'manage' ? 'active' : ''}>Manage Reports</button>
        <button onClick={() => setActiveTab('schedules')} className={activeTab === 'schedules' ? 'active' : ''}>Schedules</button>
      </div>

      {activeTab === 'create' && (
        <div className="tab-content">
          <input type="number" value={templateId} onChange={(e) => setTemplateId(e.target.value)} placeholder="Template ID" />
          <button onClick={createReport} disabled={loading}>Create Report</button>
        </div>
      )}

      {activeTab === 'manage' && (
        <div className="tab-content">
          <table>
            <thead><tr><th>ID</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              {reports.map(r => (
                <tr key={r.id}><td>{r.id}</td><td>{r.status}</td>
                <td><button onClick={() => scheduleReport(r.id)}>Schedule</button><button onClick={() => exportReport(r.id)}>Export</button></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'schedules' && (
        <div className="tab-content">
          <table>
            <thead><tr><th>ID</th><th>Frequency</th><th>Actions</th></tr></thead>
            <tbody>
              {schedules.map(s => (
                <tr key={s.schedule_id}><td>{s.schedule_id}</td><td>{s.frequency}</td>
                <td><button onClick={() => executeSchedule(s.schedule_id)}>Execute</button></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ReportingEngineUI;
