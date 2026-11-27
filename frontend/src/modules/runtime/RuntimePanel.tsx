import {useEffect,useState,type FormEvent} from "react";
import {addSchedule,disableSchedule,enqueue,listJobs,listSchedules,type Job,type Schedule} from "./api";
import {errorMessage} from "../../shared/api";

import {Status,jobTone} from "../../shared/ui/Status";
export function RuntimePanel({agentId}:{agentId:string}){
  const [jobs,setJobs]=useState<Job[]>([]);
  const [schedules,setSchedules]=useState<Schedule[]>([]);
  const [prompt,setPrompt]=useState("");
  const [mode,setMode]=useState("once");
  const [seconds,setSeconds]=useState(60);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const [pollError,setPollError]=useState("");
  useEffect(()=>{
    let active=true;
    let timer:ReturnType<typeof setTimeout>;
    async function refresh(){
      try{const [j,s]=await Promise.all([listJobs(agentId),listSchedules(agentId)]);if(active){setJobs(j);setSchedules(s);setPollError("");}}
      catch(e){if(active)setPollError(errorMessage(e));}
      finally{if(active)timer=setTimeout(refresh,2000);}
    }
    void refresh();return()=>{active=false;clearTimeout(timer)};
  },[agentId]);
  async function submit(e:FormEvent){
    e.preventDefault();if(busy||!prompt.trim())return;setBusy(true);setError("");
    try{if(mode==="once"){const j=await enqueue(agentId,prompt.trim(),seconds);setJobs(old=>old.some(v=>v.id===j.id)?old:[...old,j]);}
    else{const s=await addSchedule(agentId,prompt.trim(),seconds);setSchedules(old=>old.some(v=>v.id===s.id)?old:[...old,s]);}setPrompt("");}
    catch(e){setError(errorMessage(e));}finally{setBusy(false);}
  }
  async function disable(sid:string){setBusy(true);setError("");try{await disableSchedule(agentId,sid);setSchedules(old=>old.map(s=>s.id===sid?{...s,enabled:false}:s));}catch(e){setError(errorMessage(e));}finally{setBusy(false);}}
  return <section className="runtime-panel" aria-label="Background runtime">
    <span className="eyebrow">Execution / Automation</span><h2>Background runtime</h2><p>Requires a separate worker process. Disabling a schedule does not cancel existing jobs.</p>
    {(error||pollError)&&<p role="alert" className="error">{error||pollError}</p>}
    <div className="metric-strip"><div><small>Queued</small><strong>{jobs.filter(j=>j.status==="queued").length}</strong></div><div><small>Running</small><strong>{jobs.filter(j=>j.status==="running").length}</strong></div><div><small>Schedules enabled</small><strong>{schedules.filter(s=>s.enabled).length}</strong></div></div><form onSubmit={submit}>
      <label>Task<textarea required maxLength={20000} value={prompt} onChange={e=>setPrompt(e.target.value)}/></label>
      <label>Execution<select value={mode} onChange={e=>{setMode(e.target.value);setSeconds(60)}}><option value="once">Once, after delay</option><option value="repeat">Recurring interval</option></select></label>
      <label>Seconds<input type="number" required min={mode==="once"?0:60} max={2592000} step={1} value={seconds} onChange={e=>setSeconds(Number(e.target.value))}/></label>
      <button className="primary-button" disabled={busy||!prompt.trim()}>{mode==="once"?"Queue task":"Create schedule"}</button>
    </form>
    <h3>Jobs</h3>{jobs.length===0&&<p>No jobs.</p>}{[...jobs].reverse().map(j=><article key={j.id} className="runtime-item"><Status tone={jobTone(j.status)}>{j.status}</Status><p>{j.prompt}</p><small>Due: {new Date(j.due_at*1000).toLocaleString()}</small>{j.result!==null&&<pre>{j.result}</pre>}{j.error&&<p className="error">{j.error}</p>}</article>)}
    <h3>Schedules</h3>{schedules.length===0&&<p>No schedules.</p>}{schedules.map(s=><article key={s.id} className="runtime-item"><Status tone={s.enabled?"success":"neutral"}>{s.enabled?"Enabled":"Disabled"}</Status><p>{s.prompt}</p><small>Every {s.interval_seconds}s · Next: {new Date(s.next_at*1000).toLocaleString()}</small>{s.enabled&&<button disabled={busy} onClick={()=>void disable(s.id)}>Disable</button>}</article>)}
  </section>
}
