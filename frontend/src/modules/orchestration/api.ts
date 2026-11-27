import {request} from "../../shared/api";
export interface Delegation {job_id:string;parent_job_id:string;source_agent_id:string;target_agent_id:string;depth:number}
const path=(id:string)=>"/agents/"+encodeURIComponent(id)+"/delegations";
export const listDelegations=(id:string)=>request<Delegation[]>(path(id));
export const delegate=(id:string,parent_job_id:string,target_agent_id:string,prompt:string)=>request<Delegation>(path(id),{method:"POST",body:JSON.stringify({parent_job_id,target_agent_id,prompt})});
