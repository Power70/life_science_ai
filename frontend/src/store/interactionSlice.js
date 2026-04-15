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

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    applyFormUpdates: (state, action) => ({ ...state, ...action.payload }),
  },
});

export const { applyFormUpdates } = interactionSlice.actions;
export default interactionSlice.reducer;
