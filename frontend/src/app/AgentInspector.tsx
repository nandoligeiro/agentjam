import type {Agent} from "../modules/agents/api";
import {Icon} from "../shared/ui/Icon";
import {Status} from "../shared/ui/Status";
export function AgentInspector({agent,provider,onClose,onContext}:{agent:Agent;provider:string;onClose:()=>void;onContext:()=>void}){
 return <aside className="inspector" aria-label="Agent details">
  <div className="inspector-heading"><h2>Agent details</h2><button className="icon-button" aria-label="Close agent details" onClick={onClose}>×</button></div>
  <div className="inspector-profile"><span className="agent-avatar large"><Icon name="bot" size={24}/></span><h3>{agent.name}</h3><Status>{provider} provider</Status></div>
  <section><h3>Instructions</h3><p className="instruction-copy">{agent.instructions||"No custom instructions."}</p></section>
  <section><h3>Context</h3><p>Manage selected skills and persistent memory.</p><button className="quiet-button" onClick={onContext}>Open context <Icon name="arrow" size={15}/></button></section>
  <section><h3>Execution model</h3><p>Independent tasks. Background jobs require a running worker.</p></section>
 </aside>;
}
