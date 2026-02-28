import { DynamicTool } from "@langchain/core/tools";

export const getCurrentTime = new DynamicTool({
  name: "get_current_time",
  description: "Returns the current date and time",
  func: async () => new Date().toLocaleString(),
});
