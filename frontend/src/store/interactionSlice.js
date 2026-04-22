import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  hcp: "",
  interactionType: "Meeting",
  date: new Date().toISOString().slice(0, 10),
  time: new Date().toTimeString().slice(0, 5),
  attendees: [],
  topicsDiscussed: "",
  materialsShared: [],
  samplesDistributed: [],
  sentiment: "Neutral",
  outcomes: "",
  followUpActions: [],
  aiSuggestedFollowUps: [],
  aiSummary: "",
};

const KEY_ALIASES = {
  hcp_name: "hcp",
  hcpName: "hcp",
  interaction_type: "interactionType",
  interaction_date: "date",
  interactionDate: "date",
  interaction_time: "time",
  interactionTime: "time",
  topics_discussed: "topicsDiscussed",
  materials_shared: "materialsShared",
  samples_distributed: "samplesDistributed",
  follow_up_actions: "followUpActions",
  ai_suggested_followups: "aiSuggestedFollowUps",
  suggested_follow_ups: "aiSuggestedFollowUps",
  outcome: "outcomes",
  key_outcomes: "outcomes",
  ai_summary: "aiSummary",
};

const pad2 = (value) => String(value).padStart(2, "0");

const INVALID_TIME_TOKENS = new Set([
  "--:--",
  "--:-- --",
  "n/a",
  "na",
  "none",
  "null",
  "undefined",
  "not provided",
  "unknown",
]);

const INVALID_DATE_TOKENS = new Set(["n/a", "na", "none", "null", "undefined", "not provided", "unknown"]);

const normalizeDateValue = (value) => {
  if (!value) return value;

  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return value.toISOString().slice(0, 10);
  }

  if (typeof value !== "string") return value;

  const raw = value.trim();
  if (!raw) return "";
  if (INVALID_DATE_TOKENS.has(raw.toLowerCase())) return null;
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;

  const slashOrDash = raw.match(/^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$/);
  if (slashOrDash) {
    const a = Number(slashOrDash[1]);
    const b = Number(slashOrDash[2]);
    const year = Number(slashOrDash[3]);

    // If first token cannot be a month, treat as DD/MM/YYYY, else default MM/DD/YYYY.
    const month = a > 12 ? b : a;
    const day = a > 12 ? a : b;
    if (month >= 1 && month <= 12 && day >= 1 && day <= 31) {
      return `${year}-${pad2(month)}-${pad2(day)}`;
    }
  }

  const parsed = new Date(raw);
  if (!Number.isNaN(parsed.getTime())) {
    return parsed.toISOString().slice(0, 10);
  }

  return null;
};

const normalizeTimeValue = (value) => {
  if (!value) return value;
  if (typeof value !== "string") return value;

  const raw = value.trim();
  if (!raw) return "";
  if (INVALID_TIME_TOKENS.has(raw.toLowerCase())) return null;

  const hhmm = raw.match(/^(\d{1,2}):(\d{2})(?::\d{2})?$/);
  if (hhmm) {
    const hour = Number(hhmm[1]);
    const minute = Number(hhmm[2]);
    if (hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59) {
      return `${pad2(hour)}:${pad2(minute)}`;
    }
  }

  const meridiem = raw.match(/^(\d{1,2})(?::(\d{2}))?\s*([AaPp][Mm])$/);
  if (meridiem) {
    let hour = Number(meridiem[1]);
    const minute = Number(meridiem[2] || "0");
    const ampm = meridiem[3].toUpperCase();

    if (hour >= 1 && hour <= 12 && minute >= 0 && minute <= 59) {
      if (ampm === "PM" && hour !== 12) hour += 12;
      if (ampm === "AM" && hour === 12) hour = 0;
      return `${pad2(hour)}:${pad2(minute)}`;
    }
  }

  return null;
};

const normalizeUpdates = (updates = {}) =>
  Object.entries(updates).reduce((acc, [rawKey, value]) => {
    if (value === null || value === undefined) {
      return acc;
    }
    const key = KEY_ALIASES[rawKey] || rawKey;
    if (key === "date") {
      const normalizedDate = normalizeDateValue(value);
      if (normalizedDate !== null) {
        acc[key] = normalizedDate;
      }
      return acc;
    }
    if (key === "time") {
      const normalizedTime = normalizeTimeValue(value);
      if (normalizedTime !== null) {
        acc[key] = normalizedTime;
      }
      return acc;
    }
    acc[key] = value;
    return acc;
  }, {});

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    applyFormUpdates: (state, action) => ({ ...state, ...normalizeUpdates(action.payload) }),
  },
});

export const { applyFormUpdates } = interactionSlice.actions;
export default interactionSlice.reducer;
