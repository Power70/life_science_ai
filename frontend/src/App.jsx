import { useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { sendChatMessage, submitInteraction } from "./store/interactionThunks";
import { applyFormUpdates } from "./store/interactionSlice";

const initialMessage =
  'Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure").';

const formatList = (items, keyName) =>
  (items || [])
    .map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object") return item[keyName] || item.name || item.action || JSON.stringify(item);
      return "";
    })
    .filter(Boolean)
    .join(", ");

function App() {
  const dispatch = useDispatch();
  const interaction = useSelector((state) => state.interaction);
  const chat = useSelector((state) => state.chat);
  const [prompt, setPrompt] = useState("");
  const sessionId = useMemo(() => crypto.randomUUID(), []);

  const onSend = async () => {
    if (!prompt.trim()) return;
    const result = await dispatch(sendChatMessage({ message: prompt, context: interaction, sessionId }));
    if (result.payload?.form_updates) {
      dispatch(applyFormUpdates(result.payload.form_updates));
    }
    setPrompt("");
  };

  return (
    <div className="min-h-screen bg-[#f5f6f8] p-3 md:p-5">
      <div className="mx-auto max-w-[1280px]">
        <h1 className="mb-4 text-3xl font-semibold text-slate-800">Log HCP Interaction</h1>
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-[1fr_360px]">
          <form
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
            onSubmit={(event) => {
              event.preventDefault();
              dispatch(submitInteraction(interaction));
            }}
          >
            <div className="mb-4 rounded border border-slate-100 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700">
              Interaction Details (AI-controlled)
            </div>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div>
                <p className="mb-1 text-sm font-medium text-slate-700">HCP Name</p>
                <input className="w-full rounded border border-slate-300 bg-white p-2" placeholder="Search or select HCP..." value={interaction.hcp || ""} readOnly />
              </div>
              <div>
                <p className="mb-1 text-sm font-medium text-slate-700">Interaction Type</p>
                <input className="w-full rounded border border-slate-300 bg-white p-2" value={interaction.interactionType || "Meeting"} readOnly />
              </div>
              <div>
                <p className="mb-1 text-sm font-medium text-slate-700">Date</p>
                <input className="w-full rounded border border-slate-300 bg-white p-2" type="date" value={interaction.date || ""} readOnly />
              </div>
              <div>
                <p className="mb-1 text-sm font-medium text-slate-700">Time</p>
                <input className="w-full rounded border border-slate-300 bg-white p-2" type="time" value={interaction.time || ""} readOnly />
              </div>
            </div>

            <div className="mt-3">
              <p className="mb-1 text-sm font-medium text-slate-700">Attendees</p>
              <input className="w-full rounded border border-slate-300 bg-white p-2" placeholder="Enter names or search..." value={(interaction.attendees || []).join(", ")} readOnly />
            </div>

            <div className="mt-3">
              <p className="mb-1 text-sm font-medium text-slate-700">Topics Discussed</p>
              <textarea
                className="w-full rounded border border-slate-300 bg-white p-2"
                rows={3}
                placeholder="Enter key discussion points..."
                value={interaction.topicsDiscussed || ""}
                readOnly
              />
            </div>

            <button type="button" className="mt-2 rounded bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
              Summarize from Voice Note (Requires Consent)
            </button>

            <div className="mt-4">
              <p className="text-sm font-semibold text-slate-700">Materials Shared / Samples Distributed</p>
              <div className="mt-2">
                <p className="mb-1 text-sm font-medium text-slate-700">Materials Shared</p>
                <textarea
                  className="w-full rounded border border-slate-300 bg-white p-2"
                  rows={2}
                  placeholder="No materials added."
                  value={formatList(interaction.materialsShared, "name")}
                  readOnly
                />
              </div>
              <div className="mt-2">
                <p className="mb-1 text-sm font-medium text-slate-700">Samples Distributed</p>
                <textarea
                  className="w-full rounded border border-slate-300 bg-white p-2"
                  rows={2}
                  placeholder="No samples added."
                  value={formatList(interaction.samplesDistributed, "product")}
                  readOnly
                />
              </div>
            </div>

            <textarea
              className="mt-3 w-full rounded border border-slate-300 bg-white p-2"
              rows={3}
              placeholder="Outcomes"
              value={interaction.outcomes || ""}
              readOnly
            />

            <p className="mt-3 text-sm font-medium text-slate-700">Observed/Inferred HCP Sentiment</p>
            <div className="mt-1 flex gap-4 text-sm">
              {["Positive", "Neutral", "Negative"].map((item) => (
                <label key={item} className="flex items-center gap-1">
                  <input type="radio" checked={interaction.sentiment === item} readOnly />
                  {item}
                </label>
              ))}
            </div>

            <div className="mt-3">
              <p className="mb-1 text-sm font-medium text-slate-700">Follow-up Actions</p>
              <textarea
                className="w-full rounded border border-slate-300 bg-white p-2"
                rows={3}
                placeholder="Enter next steps or tasks..."
                value={formatList(interaction.followUpActions, "action")}
                readOnly
              />
            </div>
            <div className="mt-2 text-sm text-blue-700">
              <p className="font-semibold">AI Suggested Follow-up:</p>
              <ul className="list-disc pl-5">
                {(interaction.aiSuggestedFollowUps || []).map((item, idx) => (
                  <li key={`${item?.action || "follow-up"}-${idx}`}>{item?.action || JSON.stringify(item)}</li>
                ))}
              </ul>
            </div>
            <button className="mt-4 rounded bg-blue-600 px-4 py-2 text-white" type="submit">
              Log Interaction
            </button>
          </form>
          <section className="rounded-xl border border-slate-200 bg-[#f6fafc] shadow-sm">
            <div className="border-b border-slate-200 bg-[#f0f7fb] px-4 py-3">
              <h2 className="text-2xl font-semibold text-slate-800">AI Assistant</h2>
              <p className="text-sm text-slate-500">Log interaction via chat</p>
            </div>
            <div className="h-[640px] overflow-y-auto p-3">
              {chat.messages.length === 0 && <p className="text-sm text-slate-500">{initialMessage}</p>}
              {chat.error && <p className="mb-2 rounded bg-red-50 p-2 text-sm text-red-700">{chat.error}</p>}
              {chat.messages.map((message) => (
                <div
                  key={message.id}
                  className={`mb-2 rounded-xl border p-2 text-sm shadow-sm ${
                    message.role === "assistant" ? "bg-green-50 border-green-100" : "bg-white border-slate-200"
                  }`}
                >
                  <p className="font-semibold lowercase text-slate-700">{message.role}</p>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  {message.tool_used && <p className="mt-1 text-xs text-blue-600">Tool: {message.tool_used}</p>}
                </div>
              ))}
            </div>
            <div className="flex gap-2 border-t border-slate-200 bg-white p-3">
              <input
                className="flex-1 rounded border border-slate-300 p-2"
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                placeholder="Describe interaction..."
              />
              <button className="rounded bg-slate-800 px-4 py-2 text-white disabled:opacity-60" onClick={onSend} type="button" disabled={chat.isLoading}>
                Log
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
