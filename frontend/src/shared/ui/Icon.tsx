import type {ReactNode} from "react";
export type IconName="tasks"|"runtime"|"context"|"team"|"plus"|"search"|"arrow"|"panel"|"check"|"bot"|"refresh";
const paths:Record<IconName,ReactNode>={
 tasks:<><path d="M4 5h16v12H9l-5 4z"/><path d="M8 9h8m-8 4h5"/></>,
 runtime:<><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
 context:<><path d="M5 4h7a4 4 0 0 1 4 4v12H9a4 4 0 0 0-4-4zm11 4h3v12h-3M8 8h5m-5 4h5"/></>,
 team:<><circle cx="12" cy="5" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="M12 7v5m-7 4v-4h14v4"/></>,
 plus:<path d="M12 5v14M5 12h14"/>,search:<><circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5 5"/></>,
 arrow:<path d="m5 12 14 0m-6-6 6 6-6 6"/>,
 panel:<><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/></>,
 check:<path d="m5 12 4 4L19 6"/>,
 bot:<><rect x="4" y="7" width="16" height="13" rx="4"/><path d="M12 7V3m-4 9h.01m8 0h.01M9 16h6"/></>,
 refresh:<><path d="M20 10a8 8 0 1 0-2 8m2-13v5h-5"/></>
};
export function Icon({name,size=18}:{name:IconName;size?:number}){
 return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}
