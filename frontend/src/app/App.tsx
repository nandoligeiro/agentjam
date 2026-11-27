import {useEffect,useState} from "react";
import {AgentSidebar} from "../modules/agents/AgentSidebar";
import {listAgents,type Agent} from "../modules/agents/api";
import {RuntimePanel} from "../modules/runtime/RuntimePanel";
import {ContextPanel} from "../modules/context/ContextPanel";
import {TaskWorkspace} from "../modules/tasks/TaskWorkspace";
import {request,errorMessage} from "../shared/api";
export function App(){
  const [agents,setAgents]=useState<Agent[]>([]);
  const [selected,setSelected]=useState<string|null>(null);
  const [provider,setProvider]=useState("unknown");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const [view,setView]=useState<"tasks"|"runtime"|"context">("tasks");
  const [retry,setRetry]=useState(0);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{let active=true;setLoading(true);setError("");
    Promise.all([listAgents(),request<{provider:string}>("/health")]).then(([data,health])=>{
      if(!active)return;setAgents(data);setProvider(health.provider);setSelected(old=>data.some(a=>a.id===old)?old:data[0]?.id??null);
    }).catch(e=>{if(active)setError(errorMessage(e));}).finally(()=>{if(active)setLoading(false)});
    return()=>{active=false};
  },[retry]);
  const agent=agents.find(a=>a.id===selected);
  return <div className="shell">
    <AgentSidebar agents={agents} selected={selected} onSelect={id=>{if(!busy)setSelected(id)}} onCreated={a=>{setAgents(old=>[...old,a]);if(!busy)setSelected(a.id)}}/>
    <div className="content">
      <div className="statusbar"><span>Agent Workspace</span><div className="view-tabs"><button disabled={busy} aria-pressed={view==="tasks"} onClick={()=>setView("tasks")}>Tasks</button><button disabled={busy} aria-pressed={view==="runtime"} onClick={()=>setView("runtime")}>Runtime</button><button disabled={busy} aria-pressed={view==="context"} onClick={()=>setView("context")}>Context</button></div><span className="tag">{loading?"Connecting…":error?"API unavailable":provider==="mock"?"Mock mode":"Provider: "+provider}</span></div>
      {error?<div className="empty" role="alert"><h2>Cannot connect to AgentJam</h2><p>{error}</p><button onClick={()=>setRetry(v=>v+1)}>Retry</button></div>:loading?<div className="empty">Loading workspace…</div>:agent?(view==="context"?<ContextPanel key={agent.id} agentId={agent.id}/>:view==="runtime"?<RuntimePanel key={agent.id} agentId={agent.id}/>:<TaskWorkspace key={agent.id} agent={agent} provider={provider} busy={busy} onBusy={setBusy}/>):<div className="empty"><h1>Your AI workspace</h1><p>Create an agent to run your first task.</p></div>}
    </div>
  </div>
}
