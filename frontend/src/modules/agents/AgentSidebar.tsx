import { useState, type FormEvent } from "react";
import { createAgent, type Agent } from "./api";
import { errorMessage } from "../../shared/api";
interface Props { branding:{name:string;tagline:string;initials:string}; edition:string; agents: Agent[]; selected: string | null; onSelect: (id:string)=>void; onCreated: (agent:Agent)=>void }
export function AgentSidebar({branding,edition,agents,selected,onSelect,onCreated}:Props) {
  const [creating,setCreating] = useState(false);
  const [name,setName] = useState("");
  const [instructions,setInstructions] = useState("");
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState("");
  async function submit(e:FormEvent) {
    e.preventDefault(); if(busy || !name.trim()) return;
    setBusy(true); setError("");
    try { const agent=await createAgent({name:name.trim(),instructions}); onCreated(agent); setCreating(false);setName("");setInstructions(""); }
    catch(e){setError(errorMessage(e));} finally {setBusy(false);}
  }
  return <aside className="sidebar">
    <div className="brand"><span className="logo" aria-hidden="true">{branding.initials}</span><div><strong>{branding.name}</strong><small>{branding.tagline}</small></div></div>
    <div className="sidebar-heading"><h2>Agents</h2><button onClick={()=>setCreating(!creating)} disabled={busy} aria-expanded={creating}>{creating?"Close":"+ New"}</button></div>
    {creating && <form className="create-form" onSubmit={submit}>
      <label>Name<input required maxLength={120} value={name} onChange={e=>setName(e.target.value)}/></label>
      <label>Instructions<textarea maxLength={20000} rows={4} value={instructions} onChange={e=>setInstructions(e.target.value)}/></label>
      {error && <p role="alert" className="error">{error}</p>}
      <button type="submit" disabled={busy || !name.trim()}>{busy?"Creating…":"Create agent"}</button>
    </form>}
    <nav aria-label="Agents">{agents.length===0 && <p className="muted">No agents yet. Create your first teammate.</p>}
    {agents.map(agent=><button className={"agent-item"+(agent.id===selected?" active":"")} key={agent.id} onClick={()=>onSelect(agent.id)} aria-current={agent.id===selected?"true":undefined}><span className="avatar">{agent.name.slice(0,2).toUpperCase()}</span><span>{agent.name}</span></button>)}</nav>
    <footer>Local-first · {edition} edition</footer>
  </aside>;
}
