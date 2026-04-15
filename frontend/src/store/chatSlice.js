import { createSlice } from "@reduxjs/toolkit";

const chatSlice = createSlice({
  name: "chat",
  initialState: { messages: [], isLoading: false, error: null },
  reducers: {
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const { setLoading, addMessage, setError } = chatSlice.actions;
export default chatSlice.reducer;
