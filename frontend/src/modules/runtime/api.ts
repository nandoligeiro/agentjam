import {request} from "../../shared/api";
export interface Job {id:string;agent_id:string;prompt:string;status:"queued"|"running"|"succeeded"|"failed"|"interrupted";due_at:number;result:string|null;error:string|null}
export interface Schedule {id:string;agent_id:string;prompt:string;interval_seconds:number;next_at:number;enabled:boolean}
const base=(id:string)=>"/agents/"+encodeURIComponent(id);
export const listJobs=(id:string)=>request<Job[]>(base(id)+"/jobs");
export const listSchedules=(id:string)=>request<Schedule[]>(base(id)+"/schedules");
export const enqueue=(id:string,prompt:string,delay_seconds:number)=>request<Job>(base(id)+"/jobs",{method:"POST",body:JSON.stringify({prompt,delay_seconds})});
export const addSchedule=(id:string,prompt:string,interval_seconds:number)=>request<Schedule>(base(id)+"/schedules",{method:"POST",body:JSON.stringify({prompt,interval_seconds})});
export const disableSchedule=(id:string,sid:string)=>request<{enabled:boolean}>(base(id)+"/schedules/"+encodeURIComponent(sid),{method:"DELETE"});
