import { configureStore } from "@reduxjs/toolkit";

import chatReducer from "./chatSlice";
import interactionReducer from "./interactionSlice";

export const store = configureStore({
  reducer: {
    interaction: interactionReducer,
    chat: chatReducer,
  },
});
