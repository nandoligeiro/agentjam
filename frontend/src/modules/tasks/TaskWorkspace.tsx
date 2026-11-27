import {useEffect,useRef,useState,type FormEvent} from "react";
import type {Agent} from "../agents/api";
import {listTasks,runTask,type Task} from "./api";
import {errorMessage} from "../../shared/api";
import {Icon} from "../../shared/ui/Icon";
export function TaskWorkspace({agent,provider,busy,onBusy}:{agent:Agent;provider:string;busy:boolean;onBusy:(busy:boolean)=>void}){
  const [tasks,setTasks]=useState<Task[]>([]);
  const [prompt,setPrompt]=useState("");
  const [error,setError]=useState("");
  const [loading,setLoading]=useState(true);
  const [retry,setRetry]=useState(0);
  const bottom=useRef<HTMLDivElement>(null);
  const mounted=useRef(false);
  useEffect(()=>{mounted.current=true;return()=>{mounted.current=false}},[]);
  useEffect(()=>{
    let active=true;setLoading(true);setError("");
    listTasks(agent.id).then(data=>{if(active)setTasks(data)}).catch(e=>{if(active)setError(errorMessage(e))}).finally(()=>{if(active)setLoading(false)});
    return()=>{active=false};
  },[agent.id,retry]);
  useEffect(()=>{bottom.current?.scrollIntoView({block:"end"});},[tasks]);
  async function submit(e:FormEvent){
    e.preventDefault(); if(busy||loading||!prompt.trim())return;
    onBusy(true);setError("");
    try{const task=await runTask(agent.id,prompt.trim());if(mounted.current){setTasks(old=>[...old.filter(t=>t.id!==task.id),task]);setPrompt("");}}
    catch(e){if(mounted.current)setError(errorMessage(e));}finally{onBusy(false);}
  }
  return <main className="workspace">
    <header className="workspace-header"><div><span className="eyebrow">Agent workspace / Tasks</span><h1>{agent.name}</h1><p>{agent.instructions||"No custom instructions"}</p></div><span className="tag">{provider} provider</span></header>
    <section className="timeline" aria-label="Task history" aria-live="polite">
      {loading?<p>Loading history…</p>:tasks.length===0?<div className="empty"><span className="empty-icon"><Icon name="tasks" size={28}/></span><h2>What shall we work on?</h2><p>Send an instruction to your agent. Each task runs independently; previous messages are not automatically included.</p></div>:tasks.map(task=><article key={task.id} className="turn"><div className="message user"><small className="message-label">You</small><p>{task.prompt}</p></div><div className="message agent"><small className="message-label"><Icon name="bot" size={16}/>{agent.name}</small><pre>{task.result}</pre></div></article>)}
      {busy&&<p role="status">Running task… switching agents is disabled until completion.</p>}
      <div ref={bottom}/>
    </section>
    <form className="composer" onSubmit={submit}>
      {error&&<div role="alert" className="error">{error} <button type="button" disabled={busy} onClick={()=>setRetry(v=>v+1)}>Refresh history</button></div>}
      <label htmlFor="task-prompt">New task</label><textarea id="task-prompt" rows={3} required maxLength={20000} value={prompt} onChange={e=>setPrompt(e.target.value)} disabled={busy} placeholder="Describe the task…"/>
      <div className="composer-footer"><small>Manual execution · no automatic scheduling</small><button className="primary-button" type="submit" disabled={busy||loading||!prompt.trim()}>{busy?"Running…":"Run task"}<Icon name="arrow" size={16}/></button></div>
    </form>
  </main>
}
