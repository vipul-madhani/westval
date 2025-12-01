import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertCircle, CheckCircle, Lock, Unlock, Settings, FileText, RefreshCw, ChevronDown } from 'lucide-react';

const GlobalSiteValidation = () => {
  const [scopes, setScopes] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedScope, setSelectedScope] = useState(null);
  const [expandedSites, setExpandedSites] = useState({});
  const [showScopeModal, setShowScopeModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showCustomizeModal, setShowCustomizeModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [customizations, setCustomizations] = useState({});

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  const fetchScopes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/global-site/scopes`);
      setScopes(response.data.scopes || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch scopes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/global-site/templates`);
      setTemplates(response.data.templates || []);
    } catch (err) {
      console.error('Failed to fetch templates', err);
    }
  };

  const fetchCustomizations = async (scopeId) => {
    try {
      const response = await axios.get(`${API_BASE}/global-site/scopes/${scopeId}/customizations`);
      setCustomizations(response.data.customizations || {});
    } catch (err) {
      console.error('Failed to fetch customizations', err);
    }
  };

  useEffect(() => {
    fetchScopes();
    fetchTemplates();
  }, []);

  const handleCreateScope = async (formData) => {
    try {
      const response = await axios.post(`${API_BASE}/global-site/scopes`, formData);
      setScopes([...scopes, response.data.scope]);
      setShowScopeModal(false);
      setError(null);
    } catch (err) {
      setError('Failed to create scope');
      console.error(err);
    }
  };

  const handleDeployTemplate = async (scopeId, templateId) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/global-site/templates/${templateId}/customize`, {
        scope_id: scopeId,
        customizations: {}
      });
      fetchCustomizations(scopeId);
      setError(null);
    } catch (err) {
      setError('Failed to deploy template');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncTemplates = async (scopeId) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/global-site/scopes/${scopeId}/sync`, {});
      fetchCustomizations(scopeId);
      setError(null);
    } catch (err) {
      setError('Failed to sync templates');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLockScope = async (scopeId) => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE}/global-site/scopes/${scopeId}/lock`, {});
      fetchScopes();
      setError(null);
    } catch (err) {
      setError('Failed to lock scope');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUnlockScope = async (scopeId) => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE}/global-site/scopes/${scopeId}/unlock`, {});
      fetchScopes();
      setError(null);
    } catch (err) {
      setError('Failed to unlock scope');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSiteExpanded = (siteId) => {
    setExpandedSites(prev => ({
      ...prev,
      [siteId]: !prev[siteId]
    }));
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Global vs Site Validation</h1>
          <p className="text-gray-600">Manage validation scopes, templates, and site-specific customizations</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="text-red-600" size={20} />
            <span className="text-red-800">{error}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mb-6 flex gap-3 flex-wrap">
          <button
            onClick={() => setShowScopeModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            + Create New Scope
          </button>
          <button
            onClick={() => setShowTemplateModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
          >
            + Create Template
          </button>
          <button
            onClick={fetchScopes}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium flex items-center gap-2"
          >
            <RefreshCw size={16} /> Refresh
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin inline-block w-6 h-6 border-3 border-blue-600 border-t-transparent rounded-full"></div>
            <p className="mt-2 text-gray-600">Loading...</p>
          </div>
        )}

        {/* Scopes List */}
        {!loading && scopes.length > 0 && (
          <div className="space-y-4">
            {scopes.map(scope => (
              <div key={scope.id} className="bg-white rounded-lg border border-gray-200 shadow-sm">
                {/* Scope Header */}
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <button
                      onClick={() => toggleSiteExpanded(scope.id)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <ChevronDown
                        size={20}
                        className={`transform transition ${expandedSites[scope.id] ? 'rotate-0' : '-rotate-90'}`}
                      />
                    </button>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{scope.name}</h3>
                      <p className="text-sm text-gray-600">{scope.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {scope.is_locked ? (
                      <button
                        onClick={() => handleUnlockScope(scope.id)}
                        className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded flex items-center gap-1 text-sm hover:bg-yellow-200"
                      >
                        <Lock size={14} /> Locked
                      </button>
                    ) : (
                      <button
                        onClick={() => handleLockScope(scope.id)}
                        className="px-3 py-1 bg-green-100 text-green-800 rounded flex items-center gap-1 text-sm hover:bg-green-200"
                      >
                        <Unlock size={14} /> Unlocked
                      </button>
                    )}
                  </div>
                </div>

                {/* Scope Content */}
                {expandedSites[scope.id] && (
                  <div className="p-4 space-y-4">
                    {/* Scope Stats */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-blue-50 p-3 rounded">
                        <p className="text-sm text-gray-600">Global Tests</p>
                        <p className="text-2xl font-bold text-blue-600">{scope.global_test_coverage || 0}</p>
                      </div>
                      <div className="bg-purple-50 p-3 rounded">
                        <p className="text-sm text-gray-600">Site Instances</p>
                        <p className="text-2xl font-bold text-purple-600">{scope.site_instances?.length || 0}</p>
                      </div>
                      <div className="bg-green-50 p-3 rounded">
                        <p className="text-sm text-gray-600">Customizations</p>
                        <p className="text-2xl font-bold text-green-600">{Object.keys(customizations).length}</p>
                      </div>
                    </div>

                    {/* Template Deployment */}
                    <div className="border-t pt-4">
                      <h4 className="font-semibold text-gray-900 mb-3">Deploy Templates</h4>
                      <div className="flex flex-wrap gap-2">
                        {templates.map(template => (
                          <button
                            key={template.id}
                            onClick={() => handleDeployTemplate(scope.id, template.id)}
                            className="px-3 py-2 bg-indigo-100 text-indigo-800 rounded hover:bg-indigo-200 text-sm font-medium"
                          >
                            {template.name}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Site Instances */}
                    {scope.site_instances && scope.site_instances.length > 0 && (
                      <div className="border-t pt-4">
                        <h4 className="font-semibold text-gray-900 mb-3">Site Instances</h4>
                        <div className="space-y-2">
                          {scope.site_instances.map(site => (
                            <div key={site.id} className="bg-gray-50 p-3 rounded border border-gray-200 flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900">{site.site_name}</p>
                                <p className="text-sm text-gray-600">Coverage: {site.site_test_coverage || 0}%</p>
                              </div>
                              {site.is_customized && (
                                <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded font-medium">Customized</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="border-t pt-4 flex gap-2">
                      <button
                        onClick={() => handleSyncTemplates(scope.id)}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium flex items-center gap-2"
                      >
                        <RefreshCw size={14} /> Sync All Templates
                      </button>
                      <button
                        onClick={() => {
                          setSelectedScope(scope);
                          setShowCustomizeModal(true);
                        }}
                        className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm font-medium flex items-center gap-2"
                      >
                        <Settings size={14} /> Manage Customizations
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && scopes.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <FileText size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-600">No validation scopes yet. Create one to get started.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default GlobalSiteValidation;
