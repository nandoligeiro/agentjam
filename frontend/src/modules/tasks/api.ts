import { request } from "../../shared/api";
export interface Task { id:string; agent_id:string; prompt:string; result:string }
const path=(id:string)=>"/agents/"+encodeURIComponent(id)+"/tasks";
export const listTasks=(id:string)=>request<Task[]>(path(id));
export const runTask=(id:string,prompt:string)=>request<Task>(path(id),{method:"POST",body:JSON.stringify({prompt})});
