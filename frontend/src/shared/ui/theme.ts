const DEFAULT_ACCENT="#5eead4";
function luminance(hex:string){
 const channels=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(c=>c<=0.04045?c/12.92:((c+0.055)/1.055)**2.4);
 return channels[0]*0.2126+channels[1]*0.7152+channels[2]*0.0722;
}
export function contrast(a:string,b:string){
 const [x,y]=[luminance(a),luminance(b)].sort((a,b)=>b-a);
 return (x+0.05)/(y+0.05);
}
export function accentTokens(input:string){
 const accent=/^#[0-9a-f]{6}$/i.test(input)?input:DEFAULT_ACCENT;
 const ink=contrast(accent,"#101114")>=contrast(accent,"#ffffff")?"#101114":"#ffffff";
 const readable=contrast(accent,"#191b20")>=4.5?accent:DEFAULT_ACCENT;
 return {"--brand":accent,"--brand-ink":ink,"--accent":readable};
}
