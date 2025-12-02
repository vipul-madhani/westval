import React, { useState } from 'react';
import axios from 'axios';
import './DataEncryptionUI.css';

const DataEncryptionUI = ({ token }) => {
  const [activeTab, setActiveTab] = useState('encrypt');
  const [plaintext, setPlaintext] = useState('');
  const [keyId, setKeyId] = useState('');
  const [encryptionResult, setEncryptionResult] = useState(null);
  const [decryptionResult, setDecryptionResult] = useState(null);
  const [backupData, setBackupData] = useState('');
  const [backupLocation, setBackupLocation] = useState('LOCAL');
  const [backupResult, setBackupResult] = useState(null);
  const [selectedBackupId, setSelectedBackupId] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleEncrypt = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('/api/encryption/encrypt', {
        plaintext,
        key_id: keyId
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setEncryptionResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Encryption failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDecrypt = async (encryptionId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`/api/encryption/decrypt/${encryptionId}`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setDecryptionResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Decryption failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('/api/backup/create', {
        backup_data: backupData,
        location: backupLocation
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setBackupResult(response.data);
      setBackupData('');
    } catch (err) {
      setError(err.response?.data?.error || 'Backup creation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyBackup = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/backup/${selectedBackupId}/verify`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setVerificationResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRotateKey = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('/api/encryption/rotate-key', {
        old_key_id: keyId
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      alert(`Key rotated. New Key ID: ${response.data.new_key_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Key rotation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="data-encryption-container">
      <h2>Data Encryption & Backup Management</h2>
      
      <div className="tabs">
        <button className={activeTab === 'encrypt' ? 'active' : ''} onClick={() => setActiveTab('encrypt')}>
          Encrypt Data
        </button>
        <button className={activeTab === 'backup' ? 'active' : ''} onClick={() => setActiveTab('backup')}>
          Backup Management
        </button>
        <button className={activeTab === 'verify' ? 'active' : ''} onClick={() => setActiveTab('verify')}>
          Verify Integrity
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {loading && <div className="loading">Processing...</div>}

      {activeTab === 'encrypt' && (
        <div className="tab-content">
          <div className="form-group">
            <label>Data to Encrypt:</label>
            <textarea value={plaintext} onChange={(e) => setPlaintext(e.target.value)} rows="5" />
          </div>
          <div className="form-group">
            <label>Encryption Key ID:</label>
            <input type="number" value={keyId} onChange={(e) => setKeyId(e.target.value)} />
          </div>
          <button onClick={handleEncrypt} className="btn-primary" disabled={loading}>
            Encrypt
          </button>
          {encryptionResult && (
            <div className="result">
              <h4>Encryption Result:</h4>
              <p>ID: {encryptionResult.encryption_id}</p>
              <p>Ciphertext: {encryptionResult.ciphertext.substring(0, 100)}...</p>
              <button onClick={() => handleDecrypt(encryptionResult.encryption_id)} className="btn-secondary">
                Decrypt This
              </button>
            </div>
          )}
          {decryptionResult && (
            <div className="result">
              <h4>Decrypted Data:</h4>
              <p>{decryptionResult.plaintext}</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'backup' && (
        <div className="tab-content">
          <div className="form-group">
            <label>Backup Data:</label>
            <textarea value={backupData} onChange={(e) => setBackupData(e.target.value)} rows="5" />
          </div>
          <div className="form-group">
            <label>Backup Location:</label>
            <select value={backupLocation} onChange={(e) => setBackupLocation(e.target.value)}>
              <option value="LOCAL">Local Storage</option>
              <option value="CLOUD">Cloud Storage</option>
              <option value="HYBRID">Hybrid</option>
            </select>
          </div>
          <button onClick={handleCreateBackup} className="btn-primary" disabled={loading}>
            Create Backup
          </button>
          {backupResult && (
            <div className="result">
              <h4>Backup Created:</h4>
              <p>ID: {backupResult.backup_id}</p>
              <p>Status: {backupResult.status}</p>
              <p>Checksum: {backupResult.checksum.substring(0, 64)}...</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'verify' && (
        <div className="tab-content">
          <div className="form-group">
            <label>Backup ID:</label>
            <input type="number" value={selectedBackupId} onChange={(e) => setSelectedBackupId(e.target.value)} />
          </div>
          <button onClick={handleVerifyBackup} className="btn-primary" disabled={loading}>
            Verify Backup
          </button>
          {verificationResult && (
            <div className="result">
              <h4>Verification Result:</h4>
              <p>Integrity Verified: {verificationResult.integrity_verified ? 'Yes' : 'No'}</p>
              <p>Files Checked: {verificationResult.files_checked || 'N/A'}</p>
              <p>Recovery Possible: {verificationResult.recovery_possible ? 'Yes' : 'No'}</p>
            </div>
          )}
          <div className="form-group">
            <label>Rotate Key ID:</label>
            <input type="number" value={keyId} onChange={(e) => setKeyId(e.target.value)} />
          </div>
          <button onClick={handleRotateKey} className="btn-secondary" disabled={loading}>
            Rotate Encryption Key
          </button>
        </div>
      )}
    </div>
  );
};

export default DataEncryptionUI;
