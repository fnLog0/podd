import { describe, it, expect, beforeEach } from "vitest";
import {
  setCurrentSession,
  getCurrentSessionContextId,
  getCurrentTurnContextId,
} from "../../../locusgraph/sessions/tracker.js";

describe("session tracker", () => {
  beforeEach(() => {
    // Reset state between tests
    setCurrentSession("", 0);
  });

  describe("getCurrentSessionContextId", () => {
    it("returns empty string when no session is set", () => {
      expect(getCurrentSessionContextId()).toBe("");
    });

    it("returns correct session context after setCurrentSession", () => {
      setCurrentSession("breakfast_eggs_01032026", 1);
      expect(getCurrentSessionContextId()).toBe(
        "session:breakfast_eggs_01032026",
      );
    });

    it("updates when session changes", () => {
      setCurrentSession("session_a", 1);
      expect(getCurrentSessionContextId()).toBe("session:session_a");

      setCurrentSession("session_b", 1);
      expect(getCurrentSessionContextId()).toBe("session:session_b");
    });
  });

  describe("getCurrentTurnContextId", () => {
    it("returns empty string when no session is set", () => {
      expect(getCurrentTurnContextId()).toBe("");
    });

    it("returns empty string when turn is 0", () => {
      setCurrentSession("my_session", 0);
      expect(getCurrentTurnContextId()).toBe("");
    });

    it("returns correct turn context after setCurrentSession", () => {
      setCurrentSession("breakfast_eggs_01032026", 1);
      expect(getCurrentTurnContextId()).toBe(
        "turn:breakfast_eggs_01032026_t1",
      );
    });

    it("reflects updated turn number", () => {
      setCurrentSession("my_session", 1);
      expect(getCurrentTurnContextId()).toBe("turn:my_session_t1");

      setCurrentSession("my_session", 3);
      expect(getCurrentTurnContextId()).toBe("turn:my_session_t3");
    });
  });
});
