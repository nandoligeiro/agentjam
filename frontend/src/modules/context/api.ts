import {request} from "../../shared/api";
export interface Skill {id:string;name:string;source:string}
export interface Memory {id:string;agent_id:string;text:string;created_at:number}
const base=(id:string)=>"/agents/"+encodeURIComponent(id);
export const listSkills=()=>request<Skill[]>("/skills");
export const selectedSkills=(id:string)=>request<string[]>(base(id)+"/skills");
export const saveSkills=(id:string,skill_ids:string[])=>request<string[]>(base(id)+"/skills",{method:"PUT",body:JSON.stringify({skill_ids})});
export const listMemory=(id:string)=>request<Memory[]>(base(id)+"/memory");
export const addMemory=(id:string,text:string)=>request<Memory>(base(id)+"/memory",{method:"POST",body:JSON.stringify({text})});
export const deleteMemory=(id:string,mid:string)=>request<{deleted:boolean}>(base(id)+"/memory/"+encodeURIComponent(mid),{method:"DELETE"});
