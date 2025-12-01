import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AccessControlUI.css';

const AccessControlUI = () => {
  const [activeTab, setActiveTab] = useState('password');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [accessLogs, setAccessLogs] = useState([]);
  const [mfaUri, setMfaUri] = useState(null);
  const [formData, setFormData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
    mfa_token: ''
  });

  const api = axios.create({
    baseURL: '/api/auth',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });

  useEffect(() => {
    if (activeTab === 'access-log') {
      fetchAccessLogs();
    } else if (activeTab === 'mfa') {
      setMfaUri(null);
    }
  }, [activeTab]);

  const fetchAccessLogs = async () => {
    setLoading(true);
    try {
      const response = await api.get('/access-log');
      setAccessLogs(response.data.logs || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch access logs: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (formData.new_password !== formData.confirm_password) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.new_password.length < 12) {
      setError('Password must be at least 12 characters');
      return;
    }

    setLoading(true);
    try {
      await api.post('/password/change', {
        old_password: formData.old_password,
        new_password: formData.new_password
      });
      setSuccess('Password changed successfully');
      setFormData({
        old_password: '',
        new_password: '',
        confirm_password: '',
        mfa_token: ''
      });
      setError(null);
    } catch (err) {
      setError('Password change failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSetupMFA = async () => {
    setLoading(true);
    try {
      const response = await api.post('/mfa/setup');
      setMfaUri(response.data.provisioning_uri);
      setSuccess('MFA Setup initiated. Scan the QR code with your authenticator app.');
      setError(null);
    } catch (err) {
      setError('Failed to setup MFA: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="access-control-container">
      <h1>Access Control & Security</h1>
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      
      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'password' ? 'active' : ''}`}
          onClick={() => setActiveTab('password')}
        >
          Password Management
        </button>
        <button 
          className={`tab-btn ${activeTab === 'mfa' ? 'active' : ''}`}
          onClick={() => setActiveTab('mfa')}
        >
          Multi-Factor Authentication
        </button>
        <button 
          className={`tab-btn ${activeTab === 'access-log' ? 'active' : ''}`}
          onClick={() => setActiveTab('access-log')}
        >
          Access Audit Log
        </button>
      </div>

      {activeTab === 'password' && (
        <div className="tab-content">
          <h2>Change Password</h2>
          <p className="info-text">Password Requirements:</p>
          <ul className="requirements">
            <li>Minimum 12 characters</li>
            <li>At least one uppercase letter</li>
            <li>At least one lowercase letter</li>
            <li>At least one number</li>
            <li>At least one special character (@$!%*?&)</li>
          </ul>
          
          <div className="form-group">
            <label>Current Password</label>
            <input 
              type="password" 
              placeholder="Enter current password"
              value={formData.old_password}
              onChange={(e) => setFormData({...formData, old_password: e.target.value})}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>New Password</label>
            <input 
              type="password" 
              placeholder="Enter new password"
              value={formData.new_password}
              onChange={(e) => setFormData({...formData, new_password: e.target.value})}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input 
              type="password" 
              placeholder="Confirm new password"
              value={formData.confirm_password}
              onChange={(e) => setFormData({...formData, confirm_password: e.target.value})}
              disabled={loading}
            />
          </div>

          <button 
            className="btn btn-primary"
            onClick={handleChangePassword}
            disabled={loading || !formData.old_password || !formData.new_password}
          >
            {loading ? 'Updating...' : 'Update Password'}
          </button>
        </div>
      )}

      {activeTab === 'mfa' && (
        <div className="tab-content">
          <h2>Multi-Factor Authentication (TOTP)</h2>
          {!mfaUri ? (
            <div>
              <p>Enable two-factor authentication for enhanced security.</p>
              <button 
                className="btn btn-success"
                onClick={handleSetupMFA}
                disabled={loading}
              >
                {loading ? 'Setting up...' : 'Setup MFA'}
              </button>
            </div>
          ) : (
            <div className="mfa-setup">
              <p>Scan this QR code with your authenticator app:</p>
              <div className="qr-code">
                <img src={mfaUri} alt="MFA QR Code" />
              </div>
              <p className="info-text">After scanning, enter the 6-digit code from your app to verify.</p>
              <div className="form-group">
                <input 
                  type="text" 
                  placeholder="Enter 6-digit code"
                  value={formData.mfa_token}
                  onChange={(e) => setFormData({...formData, mfa_token: e.target.value})}
                  maxLength="6"
                />
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'access-log' && (
        <div className="tab-content">
          <h2>Access Audit Log</h2>
          <p className="info-text">Your recent account activities and access attempts</p>
          
          <div className="access-log-list">
            {loading && <p>Loading logs...</p>}
            {accessLogs.length === 0 && !loading && <p>No access logs available</p>}
            {accessLogs.map((log, idx) => (
              <div key={idx} className="log-entry">
                <div className="log-header">
                  <span className="action">{log.action}</span>
                  <span className={`status status-${log.status.toLowerCase()}`}>{log.status}</span>
                </div>
                <div className="log-details">
                  <p><strong>Resource:</strong> {log.resource_type}</p>
                  <p><strong>IP Address:</strong> {log.ip_address}</p>
                  <p><strong>Time:</strong> {new Date(log.timestamp).toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AccessControlUI;
