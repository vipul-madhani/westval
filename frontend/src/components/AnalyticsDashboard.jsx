import React,{useState,useEffect} from 'react';
import axios from 'axios';
const AnalyticsDashboard=({projectId,token})=>{
  const[metrics,setMetrics]=useState([]);
  const[loading,setLoading]=useState(false);
  useEffect(()=>{fetchMetrics();},[projectId]);
  const fetchMetrics=async()=>{
    try{
      setLoading(true);
      const res=await axios.get(`/api/analytics/project/${projectId}/metrics`,{headers:{Authorization:`Bearer ${token}`}});
      setMetrics(res.data);
    }catch(err){
      console.error('Error');
    }finally{
      setLoading(false);
    }
  };
  const avgMetric=(metricName)=>{
    const vals=metrics.filter(m=>m.name===metricName).map(m=>m.value);
    return vals.length?vals.reduce((a,b)=>a+b)/vals.length:0;
  };
  return(
    <div style={{padding:'20px'}}>
      <h2>Analytics Dashboard</h2>
      {loading?<p>Loading...</p>:(
        <div>
          <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:'20px'}}>
            {['Validation Rate','Completion Rate','Error Count'].map(m=>(
              <div key={m} style={{border:'1px solid #ddd',padding:'20px',borderRadius:'8px'}}>
                <h3>{m}</h3>
                <p style={{fontSize:'24px',fontWeight:'bold'}}>{avgMetric(m).toFixed(2)}</p>
              </div>
            ))}
          </div>
          <h3 style={{marginTop:'20px'}}>Recent Metrics</h3>
          <table style={{width:'100%',borderCollapse:'collapse'}}>
            <thead><tr><th style={{border:'1px solid #ddd',padding:'10px'}}>Metric</th><th style={{border:'1px solid #ddd',padding:'10px'}}>Value</th><th style={{border:'1px solid #ddd',padding:'10px'}}>Time</th></tr></thead>
            <tbody>
              {metrics.slice(0,10).map(m=>(
                <tr key={m.name+m.ts}>
                  <td style={{border:'1px solid #ddd',padding:'10px'}}>{m.name}</td>
                  <td style={{border:'1px solid #ddd',padding:'10px'}}>{m.value}</td>
                  <td style={{border:'1px solid #ddd',padding:'10px'}}>{new Date(m.ts).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
export default AnalyticsDashboard;
