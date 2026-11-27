import { request } from "../../shared/api";
export interface Agent { id: string; name: string; instructions: string }
export interface AgentInput { name: string; instructions: string }
export const listAgents = () => request<Agent[]>("/agents");
export const createAgent = (input: AgentInput) => request<Agent>("/agents", {method:"POST", body:JSON.stringify(input)});
