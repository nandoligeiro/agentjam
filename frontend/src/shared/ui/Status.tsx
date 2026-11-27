import type {ReactNode} from "react";
export type Tone="neutral"|"success"|"warning"|"danger"|"info";
export function Status({tone="neutral",children}:{tone?:Tone;children:ReactNode}){
 return <span className={"status-pill "+tone}><span className="status-dot" aria-hidden="true"/>{children}</span>;
}
export function jobTone(status:string):Tone {
 switch(status){case "succeeded":return "success";case "running":return "info";case "interrupted":return "warning";case "failed":return "danger";default:return "neutral";}
}
