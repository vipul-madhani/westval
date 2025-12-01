import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TestManagement.css';

const TestManagement = ({ validationId }) => {
  const [testPlans, setTestPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showNewPlanModal, setShowNewPlanModal] = useState(false);
  const [showExecuteModal, setShowExecuteModal] = useState(false);
  const [selectedTestCase, setSelectedTestCase] = useState(null);
  const [coverage, setCoverage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
  const AUTH_TOKEN = localStorage.getItem('authToken');

  const headers = { Authorization: `Bearer ${AUTH_TOKEN}` };

  // Fetch test coverage
  useEffect(() => {
    const fetchCoverage = async () => {
      try {
        const response = await axios.get(
          `${API_BASE}/test-management/validations/${validationId}/coverage`,
          { headers }
        );
        setCoverage(response.data);
      } catch (err) {
        console.error('Error fetching coverage:', err);
      }
    };

    if (validationId) fetchCoverage();
  }, [validationId]);

  // Create new test plan
  const createTestPlan = async (planData) => {
    try {
      setLoading(true);
      const response = await axios.post(
        `${API_BASE}/test-management/plans`,
        {
          ...planData,
          validation_id: validationId
        },
        { headers }
      );
      setTestPlans([...testPlans, response.data]);
      setShowNewPlanModal(false);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create test plan');
    } finally {
      setLoading(false);
    }
  };

  // Execute test case
  const executeTestCase = async (testCaseId, executedBy) => {
    try {
      setLoading(true);
      const response = await axios.post(
        `${API_BASE}/test-management/cases/${testCaseId}/execute`,
        { executed_by: executedBy },
        { headers }
      );
      setShowExecuteModal(false);
      setError(null);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to execute test');
    } finally {
      setLoading(false);
    }
  };

  // Record step result
  const recordStepResult = async (executionId, stepId, status, actualResult) => {
    try {
      await axios.post(
        `${API_BASE}/test-management/executions/${executionId}/steps/${stepId}/result`,
        {
          status,
          actual_result: actualResult,
          screenshots: []
        },
        { headers }
      );
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to record step result');
    }
  };

  return (
    <div className="test-management-container">
      <div className="test-management-header">
        <h1>Test Management</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowNewPlanModal(true)}
        >
          Create Test Plan
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {/* Coverage Metrics */}
      {coverage && (
        <div className="coverage-metrics">
          <div className="metric-card">
            <h3>Total Test Cases</h3>
            <p className="metric-value">{coverage.total_test_cases}</p>
          </div>
          <div className="metric-card">
            <h3>Coverage</h3>
            <p className="metric-value">{coverage.coverage_percentage}%</p>
          </div>
          <div className="metric-card">
            <h3>Pass Rate</h3>
            <p className="metric-value">{coverage.pass_rate}%</p>
          </div>
          <div className="metric-card">
            <h3>Executed</h3>
            <p className="metric-value">{coverage.executed_test_cases}</p>
          </div>
        </div>
      )}

      {/* Test Plans List */}
      <div className="test-plans-section">
        <h2>Test Plans</h2>
        {testPlans.length === 0 ? (
          <p className="empty-state">No test plans yet. Create one to get started.</p>
        ) : (
          <div className="test-plans-list">
            {testPlans.map(plan => (
              <div key={plan.id} className="test-plan-card">
                <div className="plan-header">
                  <h3>{plan.name}</h3>
                  <span className={`status status-${plan.status.toLowerCase()}`}>
                    {plan.status}
                  </span>
                </div>
                <p className="plan-description">{plan.description}</p>
                <div className="plan-actions">
                  <button 
                    className="btn btn-sm btn-outline"
                    onClick={() => setSelectedPlan(plan)}
                  >
                    View Details
                  </button>
                  <button className="btn btn-sm btn-secondary">
                    Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Test Execution Modal */}
      {showExecuteModal && selectedTestCase && (
        <div className="modal">
          <div className="modal-content">
            <h3>Execute Test Case</h3>
            <p>{selectedTestCase.name}</p>
            <div className="form-group">
              <label>Executed By</label>
              <input type="text" placeholder="Enter user ID" />
            </div>
            <div className="modal-actions">
              <button className="btn btn-primary">Execute</button>
              <button 
                className="btn btn-secondary"
                onClick={() => setShowExecuteModal(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Plan Modal */}
      {showNewPlanModal && (
        <div className="modal">
          <div className="modal-content">
            <h3>Create Test Plan</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              createTestPlan({
                name: formData.get('name'),
                description: formData.get('description'),
                project_id: formData.get('project_id'),
                created_by: formData.get('created_by')
              });
            }}>
              <div className="form-group">
                <label>Plan Name</label>
                <input type="text" name="name" required />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea name="description" rows="3"></textarea>
              </div>
              <div className="form-group">
                <label>Project ID</label>
                <input type="text" name="project_id" required />
              </div>
              <div className="form-group">
                <label>Created By</label>
                <input type="text" name="created_by" required />
              </div>
              <div className="modal-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Creating...' : 'Create'}
                </button>
                <button 
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowNewPlanModal(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestManagement;
