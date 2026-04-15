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
  ai_summary: "aiSummary",
};

const normalizeUpdates = (updates = {}) =>
  Object.entries(updates).reduce((acc, [rawKey, value]) => {
    if (value === null || value === undefined) {
      return acc;
    }
    const key = KEY_ALIASES[rawKey] || rawKey;
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
