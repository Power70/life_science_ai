import { addMessage, setLoading } from "./chatSlice";

const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const sendChatMessage = ({ message, context, sessionId }) => async (dispatch) => {
  dispatch(addMessage({ id: crypto.randomUUID(), role: "user", content: message }));
  dispatch(setLoading(true));
  try {
    const response = await fetch(`${API_URL}/agent/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message, context }),
    });
    const data = await response.json();
    dispatch(
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response,
        tool_used: data.tool_used,
      }),
    );
    return { payload: data };
  } finally {
    dispatch(setLoading(false));
  }
};

export const submitInteraction = (interaction) => async () => {
  await fetch(`${API_URL}/interactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      interaction_type: interaction.interactionType,
      interaction_date: interaction.date,
      interaction_time: interaction.time || null,
      attendees: interaction.attendees || [],
      topics_discussed: interaction.topicsDiscussed || "",
      materials_shared: interaction.materialsShared || [],
      samples_distributed: interaction.samplesDistributed || [],
      sentiment: interaction.sentiment || "Neutral",
      outcomes: interaction.outcomes || "",
      follow_up_actions: interaction.followUpActions || [],
      ai_suggested_followups: interaction.aiSuggestedFollowUps || [],
      ai_summary: interaction.aiSummary || "",
      logged_via: "chat",
      raw_chat_input: "",
    }),
  });
};
