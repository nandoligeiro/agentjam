import {useEffect,useState,type FormEvent} from "react";
import type {Agent} from "../agents/api";
import {listJobs,type Job} from "../runtime/api";
import {delegate,listDelegations,type Delegation} from "./api";
import {errorMessage} from "../../shared/api";
export function TeamPanel({agent,agents}:{agent:Agent;agents:Agent[]}){
  const [jobs,setJobs]=useState<Job[]>([]);
  const [links,setLinks]=useState<Delegation[]>([]);
  const [parent,setParent]=useState("");
  const [target,setTarget]=useState("");
  const [prompt,setPrompt]=useState("");
  const [busy,setBusy]=useState(false);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");
  const [revision,setRevision]=useState(0);
  useEffect(()=>{let active=true;setLoading(true);
    Promise.all([listJobs(agent.id),listDelegations(agent.id)]).then(([j,l])=>{
      if(active){setJobs(j);setLinks(l);setError("");}
    }).catch(e=>{if(active)setError(errorMessage(e));}).finally(()=>{if(active)setLoading(false);});
    return()=>{active=false};
  },[agent.id,revision]);
  async function submit(e:FormEvent){
    e.preventDefault();if(busy||loading||!parent||!target||!prompt.trim())return;
    setBusy(true);setError("");
    try{const link=await delegate(agent.id,parent,target,prompt.trim());setLinks(old=>[...old.filter(l=>l.job_id!==link.job_id),link]);setPrompt("");}
    catch(e){setError(errorMessage(e));}finally{setBusy(false);}
  }
  const name=(id:string)=>agents.find(a=>a.id===id)?.name??id;
  const eligible=jobs.filter(j=>j.status==="succeeded");
  return <section className="runtime-panel" aria-label="Team delegations">
    <span className="eyebrow">Collaboration / Delegation</span><h2>Team · {agent.name}</h2>
    <p>Operator-directed delegation from completed background jobs. A separate worker executes each child task. Results and memory are not automatically shared.</p>
    {error&&<p role="alert" className="error">{error}</p>}
    <button disabled={busy||loading} onClick={()=>setRevision(v=>v+1)}>Refresh team</button>
    <h3>Delegate a task</h3>
    {loading?<p>Loading jobs…</p>:eligible.length===0?<p>Complete a background job in Runtime before delegating.</p>:<form onSubmit={submit}>
      <label>Parent job<select required value={parent} onChange={e=>setParent(e.target.value)}><option value="">Choose completed job</option>{eligible.map(j=><option key={j.id} value={j.id}>{j.prompt.slice(0,100)} · {j.id.slice(0,8)}</option>)}</select></label>
      <label>Target agent<select required value={target} onChange={e=>setTarget(e.target.value)}><option value="">Choose teammate</option>{agents.filter(a=>a.id!==agent.id).map(a=><option key={a.id} value={a.id}>{a.name}</option>)}</select></label>
      <label>Explicit task<textarea required maxLength={20000} value={prompt} onChange={e=>setPrompt(e.target.value)}/></label>
      <button className="primary-button" disabled={busy||!parent||!target||!prompt.trim()}>Queue delegated task</button>
    </form>}
    <h3>Delegation history</h3>
    {links.length===0&&<p>No delegations yet.</p>}
    {links.map(l=><article className="runtime-item" key={l.job_id}><strong>{name(l.source_agent_id)} → {name(l.target_agent_id)}</strong><p>Depth {l.depth} · {l.source_agent_id===agent.id?"Outgoing":"Incoming"}</p><small>Parent: {l.parent_job_id}</small><br/><small>Child: {l.job_id}</small><p><small>Track execution in the target agent's Runtime tab.</small></p></article>)}
    <small>Limits: three levels, five children per parent, twenty descendants per root. Repeated ancestor agents are rejected.</small>
  </section>
}
