import {useEffect,useState,type CSSProperties} from "react";
import {AgentSidebar} from "../modules/agents/AgentSidebar";
import {listAgents,type Agent} from "../modules/agents/api";
import {RuntimePanel} from "../modules/runtime/RuntimePanel";
import {ContextPanel} from "../modules/context/ContextPanel";
import {TeamPanel} from "../modules/orchestration/TeamPanel";
import {TaskWorkspace} from "../modules/tasks/TaskWorkspace";
import {request,errorMessage} from "../shared/api";
import {Icon,type IconName} from "../shared/ui/Icon";
import {Status} from "../shared/ui/Status";
import {accentTokens} from "../shared/ui/theme";
import {AgentInspector} from "./AgentInspector";
const tabs: {id:IconName & ("tasks"|"runtime"|"context"|"team");label:string}[]=[{id:"tasks",label:"Tasks"},{id:"runtime",label:"Runtime"},{id:"context",label:"Context"},{id:"team",label:"Team"}];
type Distribution = {name:string;branding:{name:string;tagline:string;initials:string;primaryColor:string}};
const community:Distribution={name:"community",branding:{name:"AgentJam",tagline:"Open Agent Workspace",initials:"AJ",primaryColor:"#5eead4"}};
export function App(){
  const [distribution,setDistribution]=useState<Distribution>(community);
  const [agents,setAgents]=useState<Agent[]>([]);
  const [selected,setSelected]=useState<string|null>(null);
  const [provider,setProvider]=useState("unknown");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);
  const [inspector,setInspector]=useState(false);
  const [view,setView]=useState<"tasks"|"runtime"|"context"|"team">("tasks");
  const [retry,setRetry]=useState(0);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{let active=true;setLoading(true);setError("");
    Promise.all([listAgents(),request<{provider:string}>("/health"),request<Distribution>("/distribution")]).then(([data,health,edition])=>{
      if(!active)return;setAgents(data);setProvider(health.provider);setDistribution(edition);document.title=edition.branding.name;setSelected(old=>data.some(a=>a.id===old)?old:data[0]?.id??null);
    }).catch(e=>{if(active)setError(errorMessage(e));}).finally(()=>{if(active)setLoading(false)});
    return()=>{active=false};
  },[retry]);
  const agent=agents.find(a=>a.id===selected);
  return <div className="shell" style={accentTokens(distribution.branding.primaryColor) as CSSProperties}>
    <AgentSidebar branding={distribution.branding} edition={distribution.name} agents={agents} selected={selected} onSelect={id=>{if(!busy)setSelected(id)}} onCreated={a=>{setAgents(old=>[...old,a]);if(!busy)setSelected(a.id)}}/>
    <div className="content">
      <header className="statusbar"><div className="breadcrumbs"><span>Workspace</span><span aria-hidden="true">/</span><strong>{agent?.name??"Agents"}</strong></div><div className="header-actions"><Status tone={error?"danger":loading?"neutral":provider==="mock"?"neutral":"info"}>{loading?"Connecting…":error?"API unavailable":provider==="mock"?"Mock mode":"Provider: "+provider}</Status><button className="icon-button" aria-label="Toggle agent details" aria-pressed={inspector} disabled={!agent||busy} onClick={()=>setInspector(v=>!v)}><Icon name="panel"/></button></div></header>
      <nav className="view-tabs" aria-label="Workspace views">{tabs.map(tab=><button key={tab.id} disabled={busy} aria-pressed={view===tab.id} onClick={()=>setView(tab.id)}><Icon name={tab.id} size={17}/>{tab.label}</button>)}</nav>
      <div className={"workspace-body"+(inspector&&agent&&!error&&!loading?" with-inspector":"")}><div className="main-pane">
      {error?<div className="empty" role="alert"><h2>Cannot connect to workspace</h2><p>{error}</p><button onClick={()=>setRetry(v=>v+1)}>Retry</button></div>:loading?<div className="empty">Loading workspace…</div>:agent?(view==="team"?<TeamPanel key={agent.id} agent={agent} agents={agents}/>:view==="context"?<ContextPanel key={agent.id} agentId={agent.id}/>:view==="runtime"?<RuntimePanel key={agent.id} agentId={agent.id}/>:<TaskWorkspace key={agent.id} agent={agent} provider={provider} busy={busy} onBusy={setBusy}/>):<div className="empty"><span className="empty-icon"><Icon name="bot" size={30}/></span><h1>Your AI workspace</h1><p>Create an agent using the sidebar to run your first task.</p></div>}
      </div>{inspector&&agent&&!error&&!loading&&<AgentInspector agent={agent} provider={provider} onClose={()=>setInspector(false)} onContext={()=>{if(!busy)setView("context")}}/>}</div>
    </div>
  </div>
}
