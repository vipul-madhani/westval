import React,{useState,useEffect} from 'react';
import axios from 'axios';
import './AdminConfig.css';

const AdminConfig=()=>{
  const[tab,setTab]=useState('workflow');
  const[workflows,setWorkflows]=useState([]);
  const[users,setUsers]=useState([]);
  const[roles,setRoles]=useState([]);
  const[loading,setLoading]=useState(false);
  const[newWf,setNewWf]=useState({name:'',stages:[],approvers:[],sla_days:5,parallel:false});
  const[newUser,setNewUser]=useState({email:'',name:'',role:''});
  const[newRole,setNewRole]=useState({name:'',permissions:[]});
  const[auditLogs,setAuditLogs]=useState([]);

  useEffect(()=>{loadData()},[tab]);

  const loadData=async()=>{
    setLoading(true);
    try{
      if(tab==='workflow'){
        const res=await axios.get('/api/admin/workflow',{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
        setWorkflows(res.data);
      }else if(tab==='users'){
        const res=await axios.get('/api/admin/users',{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
        setUsers(res.data);
      }else if(tab==='roles'){
        const res=await axios.get('/api/admin/roles',{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
        setRoles(res.data);
      }else if(tab==='audit'){
        const res=await axios.get('/api/admin/audit',{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
        setAuditLogs(res.data);
      }
    }catch(e){console.error(e);}
    setLoading(false);
  };

  const createWorkflow=async()=>{
    try{
      const res=await axios.post('/api/admin/workflow',newWf,{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
      setWorkflows([...workflows,res.data]);
      setNewWf({name:'',stages:[],approvers:[],sla_days:5,parallel:false});
    }catch(e){console.error(e);}
  };

  const createUser=async()=>{
    try{
      const res=await axios.post('/api/admin/users',newUser,{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
      setUsers([...users,res.data]);
      setNewUser({email:'',name:'',role:''});
    }catch(e){console.error(e);}
  };

  const createRole=async()=>{
    try{
      const res=await axios.post('/api/admin/roles',newRole,{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
      setRoles([...roles,res.data]);
      setNewRole({name:'',permissions:[]});
    }catch(e){console.error(e);}
  };

  const deleteWorkflow=async(id)=>{
    try{
      await axios.delete(`/api/admin/workflow/${id}`,{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
      setWorkflows(workflows.filter(w=>w.id!==id));
    }catch(e){console.error(e);}
  };

  const deleteUser=async(id)=>{
    try{
      await axios.delete(`/api/admin/users/${id}`,{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
      setUsers(users.filter(u=>u.id!==id));
    }catch(e){console.error(e);}
  };

  const deleteRole=async(id)=>{
    try{
      await axios.delete(`/api/admin/roles/${id}`,{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}});
      setRoles(roles.filter(r=>r.id!==id));
    }catch(e){console.error(e);}
  };

  return(
    <div className='admin-config'>
      <h1>System Administration</h1>
      <div className='tabs'>
        <button className={tab==='workflow'?'active':''}onClick={()=>setTab('workflow')}>Workflows</button>
        <button className={tab==='users'?'active':''}onClick={()=>setTab('users')}>Users</button>
        <button className={tab==='roles'?'active':''}onClick={()=>setTab('roles')}>Roles</button>
        <button className={tab==='audit'?'active':''}onClick={()=>setTab('audit')}>Audit Logs</button>
      </div>

      {tab==='workflow'&&<div className='tab-content'>
        <h2>Workflow Configuration</h2>
        <div className='form-group'>
          <input placeholder='Workflow Name'value={newWf.name}onChange={e=>setNewWf({...newWf,name:e.target.value})}/>
          <input placeholder='Stages (comma-separated)'value={newWf.stages.join(',')}onChange={e=>setNewWf({...newWf,stages:e.target.value.split(',')})}/>
          <input placeholder='Approvers (comma-separated)'value={newWf.approvers.join(',')}onChange={e=>setNewWf({...newWf,approvers:e.target.value.split(',')})}/>
          <input type='number'placeholder='SLA Days'value={newWf.sla_days}onChange={e=>setNewWf({...newWf,sla_days:parseInt(e.target.value)})}/>
          <label><input type='checkbox'checked={newWf.parallel}onChange={e=>setNewWf({...newWf,parallel:e.target.checked})}/>Allow Parallel Approvals</label>
          <button onClick={createWorkflow}>Create Workflow</button>
        </div>
        <table>
          <thead><tr><th>Name</th><th>Stages</th><th>Approvers</th><th>SLA</th><th>Parallel</th><th>Action</th></tr></thead>
          <tbody>{workflows.map(wf=><tr key={wf.id}><td>{wf.name}</td><td>{wf.stages.join(', ')}</td><td>{wf.approvers.join(', ')}</td><td>{wf.sla_days}d</td><td>{wf.parallel?'Yes':'No'}</td><td><button onClick={()=>deleteWorkflow(wf.id)}>Delete</button></td></tr>)}</tbody>
        </table>
      </div>}

      {tab==='users'&&<div className='tab-content'>
        <h2>User Management</h2>
        <div className='form-group'>
          <input placeholder='Email'value={newUser.email}onChange={e=>setNewUser({...newUser,email:e.target.value})}/>
          <input placeholder='Name'value={newUser.name}onChange={e=>setNewUser({...newUser,name:e.target.value})}/>
          <select value={newUser.role}onChange={e=>setNewUser({...newUser,role:e.target.value})}><option value=''>Select Role</option>{roles.map(r=><option key={r.id}value={r.name}>{r.name}</option>)}</select>
          <button onClick={createUser}>Add User</button>
        </div>
        <table>
          <thead><tr><th>Email</th><th>Name</th><th>Role</th><th>Created</th><th>Action</th></tr></thead>
          <tbody>{users.map(u=><tr key={u.id}><td>{u.email}</td><td>{u.name}</td><td>{u.role}</td><td>{new Date(u.created_at).toLocaleDateString()}</td><td><button onClick={()=>deleteUser(u.id)}>Delete</button></td></tr>)}</tbody>
        </table>
      </div>}

      {tab==='roles'&&<div className='tab-content'>
        <h2>Role Management</h2>
        <div className='form-group'>
          <input placeholder='Role Name'value={newRole.name}onChange={e=>setNewRole({...newRole,name:e.target.value})}/>
          <textarea placeholder='Permissions (comma-separated)'value={newRole.permissions.join(',')}onChange={e=>setNewRole({...newRole,permissions:e.target.value.split(',')})}></textarea>
          <button onClick={createRole}>Create Role</button>
        </div>
        <table>
          <thead><tr><th>Role Name</th><th>Permissions</th><th>Action</th></tr></thead>
          <tbody>{roles.map(r=><tr key={r.id}><td>{r.name}</td><td>{r.permissions.join(', ')}</td><td><button onClick={()=>deleteRole(r.id)}>Delete</button></td></tr>)}</tbody>
        </table>
      </div>}

      {tab==='audit'&&<div className='tab-content'>
        <h2>Audit Logs</h2>
        <table>
          <thead><tr><th>User</th><th>Action</th><th>Resource</th><th>Details</th><th>Timestamp</th></tr></thead>
          <tbody>{auditLogs.map(log=><tr key={log.id}><td>{log.user_id}</td><td>{log.action}</td><td>{log.resource}</td><td>{log.details}</td><td>{new Date(log.created_at).toLocaleString()}</td></tr>)}</tbody>
        </table>
      </div>}

      {loading&&<p>Loading...</p>}
    </div>
  );
};

export default AdminConfig;
