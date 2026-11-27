import {describe,it,expect} from "vitest";
import {accentTokens,contrast} from "./theme";
describe("distribution colors",()=>{
 it("uses readable accent text for dark surfaces",()=>{
  for(const color of ["#ec0000","#000000","#ffffff","#5eead4"]){
   const t=accentTokens(color);
   expect(contrast(t["--accent"],"#191b20")).toBeGreaterThanOrEqual(4.5);
   expect(contrast(t["--brand"],t["--brand-ink"])).toBeGreaterThanOrEqual(4.5);
  }
 });
 it("falls back for invalid values",()=>expect(accentTokens("bad")["--brand"]).toBe("#5eead4"));
});
