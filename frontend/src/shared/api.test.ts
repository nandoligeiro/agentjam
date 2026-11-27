import {afterEach,describe,expect,it,vi} from "vitest";
import {request} from "./api";
import {runTask} from "../modules/tasks/api";
afterEach(()=>vi.unstubAllGlobals());
describe("API boundary",()=>{
  it("routes tasks through local proxy and encodes IDs",async()=>{
    const fetch=vi.fn().mockResolvedValue(new Response(JSON.stringify({id:"1"}),{status:201}));
    vi.stubGlobal("fetch",fetch);
    await runTask("a/b","hello");
    expect(fetch).toHaveBeenCalledWith("/api/agents/a%2Fb/tasks",expect.objectContaining({method:"POST",body:JSON.stringify({prompt:"hello"})}));
  });
  it("surfaces server errors",async()=>{
    vi.stubGlobal("fetch",vi.fn().mockResolvedValue(new Response(JSON.stringify({detail:"Agent not found"}),{status:404})));
    await expect(request("/agents")).rejects.toThrow("Agent not found");
  });
});
