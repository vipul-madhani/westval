import React, { useState, useRef } from 'react';
import axios from 'axios';
import './AIAutomationDMS.css';

const AIAutomationDMS = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [documents, setDocuments] = useState([]);
  const [extractions, setExtractions] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [extractionQuality, setExtractionQuality] = useState({});
  const [templates, setTemplates] = useState([]);
  const [dmsDocuments, setDmsDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDocumentUpload = async (event) => {
    const files = event.target.files;
    if (!files) return;

    setLoading(true);
    setError(null);
    try {
      for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', 'SOP');
        const response = await axios.post('/api/ai-dms/documents/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setDocuments([...documents, response.data]);
      }
    } catch (err) {
      setError(`Upload failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleExtractAI = async (documentId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`/api/ai-dms/extractions/extract`, {
        qms_document_id: documentId,
        extraction_type: 'Requirements',
        confidence_threshold: 0.75
      });
      setExtractions([...extractions, response.data]);
      setExtractionQuality({ ...extractionQuality, [documentId]: response.data.quality_score });
    } catch (err) {
      setError(`Extraction failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveExtraction = async (extractionId) => {
    setLoading(true);
    setError(null);
    try {
      await axios.put(`/api/ai-dms/extractions/${extractionId}/approve`, {
        approval_status: 'Approved'
      });
      setExtractions(extractions.map(e => e.id === extractionId ? { ...e, manual_review_status: 'Approved' } : e));
    } catch (err) {
      setError(`Approval failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTemplate = async (extractionId, templateType) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`/api/ai-dms/templates/generate`, {
        extraction_id: extractionId,
        template_type: templateType,
        document_format: 'PDF'
      });
      setTemplates([...templates, response.data]);
    } catch (err) {
      setError(`Template generation failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleMigrateToDMS = async (templateId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`/api/ai-dms/migrate`, {
        template_id: templateId,
        dms_repository: 'Production'
      });
      setDmsDocuments([...dmsDocuments, response.data]);
    } catch (err) {
      setError(`Migration failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTraceability = async (dmsDocId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/ai-dms/traceability/${dmsDocId}`);
      alert(`Traceability Chain:\n${JSON.stringify(response.data.traceability_chain, null, 2)}`);
    } catch (err) {
      setError(`Traceability retrieval failed: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-dms-container">
      <h1>AI Automation & DMS Integration</h1>
      
      <div className="tabs">
        <button className={`tab ${activeTab === 'upload' ? 'active' : ''}`} onClick={() => setActiveTab('upload')}>
          Document Upload
        </button>
        <button className={`tab ${activeTab === 'extraction' ? 'active' : ''}`} onClick={() => setActiveTab('extraction')}>
          AI Extraction
        </button>
        <button className={`tab ${activeTab === 'templates' ? 'active' : ''}`} onClick={() => setActiveTab('templates')}>
          Templates
        </button>
        <button className={`tab ${activeTab === 'migration' ? 'active' : ''}`} onClick={() => setActiveTab('migration')}>
          DMS Migration
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading">Processing...</div>}

      {activeTab === 'upload' && (
        <div className="section">
          <h2>Upload QMS Documents</h2>
          <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
            <p>Drag and drop files here or click to select</p>
            <input ref={fileInputRef} type="file" multiple onChange={handleDocumentUpload} accept=".pdf,.docx,.txt" hidden />
          </div>
          <div className="documents-list">
            {documents.map(doc => (
              <div key={doc.id} className="document-card">
                <h3>{doc.document_name}</h3>
                <p>Type: {doc.document_type} | Size: {(doc.file_size_bytes / 1024).toFixed(2)} KB</p>
                <p>Status: {doc.compliance_status}</p>
                <button onClick={() => handleExtractAI(doc.id)}>Extract with AI</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'extraction' && (
        <div className="section">
          <h2>AI Extraction Results</h2>
          <div className="extractions-list">
            {extractions.map(ext => (
              <div key={ext.id} className="extraction-card">
                <div className="quality-score">
                  <span>Quality: {(ext.quality_score * 100).toFixed(1)}%</span>
                  <div className="score-bar" style={{ width: `${ext.quality_score * 100}%` }}></div>
                </div>
                <p>Confidence: {(ext.extraction_confidence * 100).toFixed(1)}%</p>
                <p>Type: {ext.extraction_type}</p>
                <p>Status: {ext.manual_review_status}</p>
                {ext.manual_review_status !== 'Approved' && (
                  <button onClick={() => handleApproveExtraction(ext.id)} className="approve-btn">Approve</button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="section">
          <h2>Generate Validation Templates</h2>
          <div className="templates-container">
            {extractions.filter(e => e.manual_review_status === 'Approved').map(ext => (
              <div key={ext.id} className="template-options">
                <p>From Extraction: {ext.extraction_type}</p>
                <button onClick={() => handleGenerateTemplate(ext.id, 'Validation Plan')}>Generate Validation Plan</button>
                <button onClick={() => handleGenerateTemplate(ext.id, 'Test Plan')}>Generate Test Plan</button>
                <button onClick={() => handleGenerateTemplate(ext.id, 'Risk Assessment')}>Generate Risk Assessment</button>
              </div>
            ))}
          </div>
          <div className="templates-list">
            {templates.map(tmpl => (
              <div key={tmpl.id} className="template-card">
                <h3>{tmpl.template_name}</h3>
                <p>Type: {tmpl.template_type} | Format: {tmpl.document_format}</p>
                <p>Approval: {tmpl.approval_status}</p>
                {tmpl.approval_status === 'Approved' && (
                  <button onClick={() => handleMigrateToDMS(tmpl.id)}>Migrate to DMS</button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'migration' && (
        <div className="section">
          <h2>DMS Migration Status</h2>
          <div className="migration-list">
            {dmsDocuments.map(dms => (
              <div key={dms.id} className="migration-card">
                <h3>{dms.dms_document_id}</h3>
                <p>Repository: {dms.dms_repository_name}</p>
                <p>Status: {dms.migration_status}</p>
                <p>Validation: {dms.validation_status}</p>
                <p>CFR Compliant: {dms.cfr_21_compliant ? 'Yes' : 'No'}</p>
                <button onClick={() => handleTraceability(dms.id)}>View Traceability Chain</button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAutomationDMS;
