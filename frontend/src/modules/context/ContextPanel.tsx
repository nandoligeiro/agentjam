import {useEffect,useState,type FormEvent} from "react";
import {listSkills,selectedSkills,saveSkills,listMemory,addMemory,deleteMemory,type Skill,type Memory} from "./api";
import {errorMessage} from "../../shared/api";

export function ContextPanel({agentId}:{agentId:string}){
  const [skills,setSkills]=useState<Skill[]>([]);
  const [selected,setSelected]=useState<string[]>([]);
  const [memory,setMemory]=useState<Memory[]>([]);
  const [note,setNote]=useState("");
  const [loading,setLoading]=useState(true);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const [notice,setNotice]=useState("");
  useEffect(()=>{
    let active=true;setLoading(true);
    Promise.all([listSkills(),selectedSkills(agentId),listMemory(agentId)])
      .then(([s,ids,m])=>{if(active){setSkills(s);setSelected(ids);setMemory(m);}})
      .catch(e=>{if(active)setError(errorMessage(e));})
      .finally(()=>{if(active)setLoading(false);});
    return()=>{active=false;};
  },[agentId]);
  async function save(){
    setBusy(true);setError("");setNotice("");
    try{setSelected(await saveSkills(agentId,selected));setNotice("Skills saved.");}
    catch(e){setError(errorMessage(e));}finally{setBusy(false);}
  }
  async function remember(e:FormEvent){
    e.preventDefault();if(busy||!note.trim())return;setBusy(true);setError("");setNotice("");
    try{const item=await addMemory(agentId,note.trim());setMemory(old=>[item,...old]);setNote("");}
    catch(e){setError(errorMessage(e));}finally{setBusy(false);}
  }
  async function forget(id:string){
    setBusy(true);setError("");setNotice("");
    try{await deleteMemory(agentId,id);setMemory(old=>old.filter(m=>m.id!==id));}
    catch(e){setError(errorMessage(e));}finally{setBusy(false);}
  }
  const missing=selected.filter(id=>!skills.some(s=>s.id===id));
  return <section className="runtime-panel" aria-label="Agent context">
    <span className="eyebrow">Knowledge / Context</span><h2>Skills &amp; Memory</h2><p>Selected skills and the ten most recent notes are included in task context. Content may be sent to the configured provider. Never store secrets.</p>
    {error&&<p role="alert" className="error">{error}</p>}
    {notice&&<p role="status">{notice}</p>}
    {loading?<p>Loading context…</p>:<>
    <h3>Skills</h3>
    {skills.length===0&&<p>No configured skills. Set AGENTJAM_SKILLS_PATHS and restart both backend and worker.</p>}
    {skills.map(s=><label className="skill-option" key={s.id}><input type="checkbox" checked={selected.includes(s.id)} disabled={busy||(!selected.includes(s.id)&&selected.length>=8)} onChange={e=>setSelected(old=>e.target.checked?[...old,s.id]:old.filter(id=>id!==s.id))}/><span>{s.name} <small>{s.source}</small></span></label>)}
    {missing.map(id=><label className="skill-option" key={id}><input type="checkbox" checked disabled={busy} onChange={()=>setSelected(old=>old.filter(v=>v!==id))}/>Unavailable skill ({id}) — uncheck to remove</label>)}
    <button className="primary-button" disabled={busy} onClick={()=>void save()}>Save selected skills ({selected.length}/8)</button>
    <h3>Memory ({memory.length}/100)</h3>
    <form onSubmit={remember}><label>New note<textarea required maxLength={4000} value={note} onChange={e=>setNote(e.target.value)}/></label><button className="primary-button" disabled={busy||!note.trim()||memory.length>=100}>Remember</button></form>
    {memory.map((m,i)=><article className="runtime-item" key={m.id}><small>{i<10?"Included in context":"Stored only"} · {new Date(m.created_at*1000).toLocaleString()}</small><p>{m.text}</p><button disabled={busy} onClick={()=>void forget(m.id)}>Delete note</button></article>)}
    <small>Deleting a note does not erase earlier task results or provider records.</small>
    </>}
  </section>
}
