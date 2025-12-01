import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DigitalSignatureUI.css';

const DigitalSignatureUI = () => {
  const [certificates, setCertificates] = useState([]);
  const [signatures, setSignatures] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('certificates');
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [formData, setFormData] = useState({
    subject_cn: '',
    days_valid: 365,
    document_id: '',
    document_data: '',
    certificate_id: '',
    reason: ''
  });

  const api = axios.create({
    baseURL: '/api/signatures',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });

  useEffect(() => {
    if (activeTab === 'certificates') {
      fetchCertificates();
    } else if (activeTab === 'signatures') {
      fetchSignatures();
    }
  }, [activeTab]);

  const fetchCertificates = async () => {
    setLoading(true);
    try {
      const response = await api.get('/certificate');
      setCertificates(response.data.data || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch certificates: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSignatures = async () => {
    setLoading(true);
    try {
      const response = await api.get('/signature');
      setSignatures(response.data.data || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch signatures: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCertificate = async () => {
    setLoading(true);
    try {
      const response = await api.post('/certificate/generate', {
        subject_cn: formData.subject_cn,
        days_valid: parseInt(formData.days_valid)
      });
      setCertificates([...certificates, response.data]);
      setFormData({ ...formData, subject_cn: '', days_valid: 365 });
      setShowGenerateForm(false);
      setError(null);
    } catch (err) {
      setError('Failed to generate certificate: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignDocument = async () => {
    setLoading(true);
    try {
      const response = await api.post('/sign', {
        document_id: formData.document_id,
        document_data: formData.document_data,
        certificate_id: formData.certificate_id
      });
      setSignatures([...signatures, response.data]);
      setFormData({ ...formData, document_id: '', document_data: '', certificate_id: '' });
      setError(null);
    } catch (err) {
      setError('Failed to sign document: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeCertificate = async (certId) => {
    setLoading(true);
    try {
      await api.post(`/certificate/${certId}/revoke`, {
        reason: formData.reason
      });
      setCertificates(certificates.map(c => c.id === certId ? { ...c, status: 'REVOKED' } : c));
      setFormData({ ...formData, reason: '' });
      setError(null);
    } catch (err) {
      setError('Failed to revoke certificate: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySignature = async (sigId) => {
    setLoading(true);
    try {
      const response = await api.post(`/${sigId}/verify`, {
        document_data: formData.document_data
      });
      alert(`Signature Valid: ${response.data.valid}`);
      setError(null);
    } catch (err) {
      setError('Failed to verify signature: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="digital-signature-container">
      <h1>Digital Signature Management</h1>
      {error && <div className="alert alert-error">{error}</div>}
      
      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'certificates' ? 'active' : ''}`}
          onClick={() => setActiveTab('certificates')}
        >
          Certificates
        </button>
        <button 
          className={`tab-btn ${activeTab === 'signatures' ? 'active' : ''}`}
          onClick={() => setActiveTab('signatures')}
        >
          Signatures
        </button>
      </div>

      {activeTab === 'certificates' && (
        <div className="tab-content">
          <button 
            className="btn btn-primary"
            onClick={() => setShowGenerateForm(!showGenerateForm)}
          >
            {showGenerateForm ? 'Cancel' : 'Generate Certificate'}
          </button>

          {showGenerateForm && (
            <div className="form-group">
              <input 
                type="text" 
                placeholder="Subject CN"
                value={formData.subject_cn}
                onChange={(e) => setFormData({...formData, subject_cn: e.target.value})}
              />
              <input 
                type="number" 
                placeholder="Days Valid"
                value={formData.days_valid}
                onChange={(e) => setFormData({...formData, days_valid: e.target.value})}
              />
              <button 
                className="btn btn-success"
                onClick={handleGenerateCertificate}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate'}
              </button>
            </div>
          )}

          <div className="list">
            {loading && <p>Loading...</p>}
            {certificates.map(cert => (
              <div key={cert.id} className="item">
                <div className="item-header">
                  <h3>{cert.subject_dn}</h3>
                  <span className={`badge badge-${cert.status.toLowerCase()}`}>{cert.status}</span>
                </div>
                <p><strong>Thumbprint:</strong> {cert.thumbprint}</p>
                <p><strong>Serial:</strong> {cert.serial_number}</p>
                <p><strong>Expiry:</strong> {new Date(cert.expiry_date).toLocaleDateString()}</p>
                {cert.status === 'VALID' && (
                  <div className="item-actions">
                    <input 
                      type="text" 
                      placeholder="Revocation reason"
                      value={formData.reason}
                      onChange={(e) => setFormData({...formData, reason: e.target.value})}
                    />
                    <button 
                      className="btn btn-danger"
                      onClick={() => handleRevokeCertificate(cert.id)}
                      disabled={loading || !formData.reason}
                    >
                      Revoke
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'signatures' && (
        <div className="tab-content">
          <div className="form-group">
            <h3>Sign Document</h3>
            <input 
              type="text" 
              placeholder="Document ID"
              value={formData.document_id}
              onChange={(e) => setFormData({...formData, document_id: e.target.value})}
            />
            <textarea 
              placeholder="Document Data"
              value={formData.document_data}
              onChange={(e) => setFormData({...formData, document_data: e.target.value})}
            />
            <select 
              value={formData.certificate_id}
              onChange={(e) => setFormData({...formData, certificate_id: e.target.value})}
            >
              <option value="">Select Certificate</option>
              {certificates.filter(c => c.status === 'VALID').map(c => (
                <option key={c.id} value={c.id}>{c.subject_dn}</option>
              ))}
            </select>
            <button 
              className="btn btn-success"
              onClick={handleSignDocument}
              disabled={loading || !formData.document_id || !formData.document_data || !formData.certificate_id}
            >
              {loading ? 'Signing...' : 'Sign'}
            </button>
          </div>

          <div className="list">
            {loading && <p>Loading...</p>}
            {signatures.map(sig => (
              <div key={sig.id} className="item">
                <div className="item-header">
                  <h3>Document: {sig.document_id}</h3>
                  <span className={`badge badge-${sig.is_valid ? 'success' : 'error'}`}>
                    {sig.is_valid ? 'Valid' : 'Invalid'}
                  </span>
                </div>
                <p><strong>Hash:</strong> {sig.signature_hash}</p>
                <p><strong>Signed:</strong> {new Date(sig.signed_at).toLocaleString()}</p>
                <button 
                  className="btn btn-info"
                  onClick={() => handleVerifySignature(sig.id)}
                  disabled={loading}
                >
                  Verify
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DigitalSignatureUI;
