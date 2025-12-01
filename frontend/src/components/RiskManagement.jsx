import React,{useState,useEffect} from 'react';
import axios from 'axios';
const RiskManagement=({projectId,token})=>{
  const[risks,setRisks]=useState([]);
  const[loading,setLoading]=useState(false);
Sprint 10: React Risk Management Component  const fetchRisks=async()=>{
    try{
      setLoading(true);
      const res=await axios.get(`/api/risk/project/${projectId}/high`,{headers:{Authorization:`Bearer ${token}`}});
      setRisks(res.data);
    }catch(err){
      console.error('Error');
    }finally{
      setLoading(false);
    }
  };
  const getRPNColor=(rpn)=>{return rpn>=100?'red':rpn>=50?'orange':'green';};
  return(
    <div style={{padding:'20px'}}>
      <h2>Risk Management</h2>
      {loading?<p>Loading...</p>:(
        <div>
          <h3>High Priority Risks ({risks.length})</h3>
          {risks.map(r=>(
            <div key={r.id} style={{border:'1px solid #ddd',padding:'10px',borderLeft:`5px solid ${getRPNColor(r.rpn)}`}}>
              <strong>RPN:{r.rpn}</strong><p>{r.category}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
export default RiskManagement;
