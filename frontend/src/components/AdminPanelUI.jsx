import React, {useState} from 'react';
import axios from 'axios';

const AdminPanelUI = ({token}) => {
  const [activeTab, setActiveTab] = useState('roles');
  const [roleName, setRoleName] = useState('');
  const [permType, setPermType] = useState('');
  const [resource, setResource] = useState('');
  const [configKey, setConfigKey] = useState('');
  const [configValue, setConfigValue] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCreateRole = async () => {
    try {
      setLoading(true);
      const resp = await axios.post('/api/admin/role', {name: roleName}, {headers: {'Authorization': `Bearer ${token}`}});
      setResult(resp.data);
      setRoleName('');
    } catch (e) {
      setError(e.response?.data?.error || 'Error');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignPermission = async () => {
    try {
      setLoading(true);
      const resp = await axios.post('/api/admin/permission', {type: permType, resource}, {headers: {'Authorization': `Bearer ${token}`}});
      setResult(resp.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Error');
    } finally {
      setLoading(false);
    }
  };

  const handleSetConfig = async () => {
    try {
      setLoading(true);
      const resp = await axios.post('/api/admin/config', {key: configKey, value: configValue}, {headers: {'Authorization': `Bearer ${token}`}});
      setResult(resp.data);
      setConfigKey('');
      setConfigValue('');
    } catch (e) {
      setError(e.response?.data?.error || 'Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{padding: '20px'}}>
      <h2>Admin Panel</h2>
      <div>
        <button onClick={() => setActiveTab('roles')} style={{marginRight: '10px'}}>Roles</button>
        <button onClick={() => setActiveTab('perms')} style={{marginRight: '10px'}}>Permissions</button>
        <button onClick={() => setActiveTab('config')}>Config</button>
      </div>
      {error && <div style={{color: 'red'}}>{error}</div>}
      {loading && <div>Processing...</div>}
      {activeTab === 'roles' && (
        <div style={{marginTop: '20px'}}>
          <input type="text" placeholder="Role Name" value={roleName} onChange={(e) => setRoleName(e.target.value)} />
          <button onClick={handleCreateRole} disabled={loading}>Create Role</button>
          {result && <div><p>Role ID: {result.role_id}</p></div>}
        </div>
      )}
      {activeTab === 'perms' && (
        <div style={{marginTop: '20px'}}>
          <select value={permType} onChange={(e) => setPermType(e.target.value)}>
            <option>SELECT</option>
            <option value="READ">READ</option>
            <option value="WRITE">WRITE</option>
            <option value="ADMIN">ADMIN</option>
          </select>
          <input type="text" placeholder="Resource" value={resource} onChange={(e) => setResource(e.target.value)} />
          <button onClick={handleAssignPermission} disabled={loading}>Assign</button>
        </div>
      )}
      {activeTab === 'config' && (
        <div style={{marginTop: '20px'}}>
          <input type="text" placeholder="Key" value={configKey} onChange={(e) => setConfigKey(e.target.value)} />
          <input type="text" placeholder="Value" value={configValue} onChange={(e) => setConfigValue(e.target.value)} />
          <button onClick={handleSetConfig} disabled={loading}>Set Config</button>
          {result && <div><p>Config ID: {result.config_id}</p></div>}
        </div>
      )}
    </div>
  );
};
export default AdminPanelUI;
