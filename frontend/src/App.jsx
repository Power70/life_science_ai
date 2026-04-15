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

const formatActionItem = (item) => {
  if (!item) return "";
  if (typeof item === "string") return item;
  if (typeof item !== "object") return "";

  const action = item.action || item.name || "";
  const due = item.dueDate ? ` (due: ${item.dueDate})` : "";
  return `${action}${due}`.trim();
};

const cleanSummaryText = (text) => {
  if (!text || typeof text !== "string") return "";

  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/^\s*[-*]\s+/gm, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
};

function App() {
  const dispatch = useDispatch();
  const interaction = useSelector((state) => state.interaction);
  const chat = useSelector((state) => state.chat);
  const [prompt, setPrompt] = useState("");
  const sessionId = useMemo(() => crypto.randomUUID(), []);
  const interactionTypeOptions = ["Meeting", "Call", "Email", "Conference", "Other"];

  const onSend = async () => {
    if (!prompt.trim()) return;
    const result = await dispatch(sendChatMessage({ message: prompt, context: interaction, sessionId }));
    if (result.payload?.form_updates) {
      dispatch(applyFormUpdates(result.payload.form_updates));
    }
    setPrompt("");
  };

  return (
    <div className="min-h-screen bg-[#efeff3] p-4 lg:h-screen lg:overflow-hidden">
      <div className="mx-auto flex h-full max-w-[1280px] flex-col">
        <h1 className="mb-3 shrink-0 text-[40px] font-semibold leading-none text-[#1f3556]">Log HCP Interaction</h1>
        <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 lg:grid-cols-[1fr_400px]">
          <form
            className="min-h-0 rounded-lg border border-[#d7dde4] bg-white p-4 lg:overflow-y-auto"
            onSubmit={(event) => {
              event.preventDefault();
              dispatch(submitInteraction(interaction));
            }}
          >
            <div className="mb-3 rounded-t-md border border-[#dbe2e9] bg-[#edf2f6] px-3 py-2 text-[22px] font-semibold text-[#2c3f58]">
              Interaction Details
            </div>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div>
                <p className="mb-1 text-[20px] font-semibold text-[#3a4a60]">HCP Name</p>
                <input
                  className="h-11 w-full rounded-md border border-[#cfd6de] bg-white px-3 text-[17px] text-[#3c495b] placeholder:text-[#9aa4b2]"
                  placeholder="Search or select HCP..."
                  value={interaction.hcp || ""}
                  readOnly
                />
              </div>
              <div>
                <p className="mb-1 text-[20px] font-semibold text-[#3a4a60]">Interaction Type</p>
                <select
                  className="h-11 w-full rounded-md border border-[#cfd6de] bg-white px-3 text-[17px] text-[#3c495b]"
                  value={interaction.interactionType || "Meeting"}
                  disabled
                >
                  {interactionTypeOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <p className="mb-1 text-[20px] font-semibold text-[#3a4a60]">Date</p>
                <input className="h-11 w-full rounded-md border border-[#cfd6de] bg-white px-3 text-[17px] text-[#3c495b]" type="date" value={interaction.date || ""} readOnly />
              </div>
              <div>
                <p className="mb-1 text-[20px] font-semibold text-[#3a4a60]">Time</p>
                <input className="h-11 w-full rounded-md border border-[#cfd6de] bg-white px-3 text-[17px] text-[#3c495b]" type="time" value={interaction.time || ""} readOnly />
              </div>
            </div>

            <div className="mt-3">
              <p className="mb-1 text-[20px] font-semibold text-[#3a4a60]">Attendees</p>
              <input
                className="h-11 w-full rounded-md border border-[#cfd6de] bg-white px-3 text-[17px] text-[#3c495b] placeholder:text-[#9aa4b2]"
                placeholder="Enter names or search..."
                value={(interaction.attendees || []).join(", ")}
                readOnly
              />
            </div>

            <div className="mt-3">
              <p className="mb-1 text-[20px] font-semibold text-[#3a4a60]">Topics Discussed</p>
              <textarea
                className="w-full rounded-md border border-[#cfd6de] bg-white px-3 py-2 text-[17px] text-[#3c495b] placeholder:text-[#9aa4b2]"
                rows={3}
                placeholder="Enter key discussion points..."
                value={interaction.topicsDiscussed || ""}
                readOnly
              />
            </div>

            <button type="button" className="mt-2 rounded-md bg-[#e9edf3] px-3 py-1 text-[15px] font-semibold text-[#5f6f83]">
              Summarize from Voice Note (Requires Consent)
            </button>

            <div className="mt-4">
              <p className="text-[24px] font-semibold text-[#37465b]">Materials Shared / Samples Distributed</p>
              <div className="mt-2 rounded-md border border-[#d6dce4] bg-white px-3 py-2">
                <div className="flex items-center justify-between">
                  <p className="text-[22px] font-semibold text-[#37465b]">Materials Shared</p>
                  <button type="button" className="rounded-md border border-[#cdd5de] bg-[#f9fbfc] px-3 py-1 text-[17px] font-semibold text-[#4a5a70]">
                    Search/Add
                  </button>
                </div>
                <p className="mt-2 text-[16px] italic text-[#9aa6b3]">{formatList(interaction.materialsShared, "name") || "No materials added."}</p>
              </div>
              <div className="mt-2 rounded-md border border-[#d6dce4] bg-white px-3 py-2">
                <div className="flex items-center justify-between">
                  <p className="text-[22px] font-semibold text-[#37465b]">Samples Distributed</p>
                  <button type="button" className="rounded-md border border-[#cdd5de] bg-[#f9fbfc] px-3 py-1 text-[17px] font-semibold text-[#4a5a70]">
                    Add Sample
                  </button>
                </div>
                <p className="mt-2 text-[16px] italic text-[#9aa6b3]">{formatList(interaction.samplesDistributed, "product") || "No samples added."}</p>
              </div>
            </div>

            <p className="mt-3 text-[22px] font-semibold text-[#3a4a60]">Observed/Inferred HCP Sentiment</p>
            <div className="mt-2 flex flex-wrap items-center gap-5 text-[26px] text-[#4a5a70]">
              {[
                { label: "Positive", value: "Positive" },
                { label: "Neutral", value: "Neutral" },
                { label: "Negative", value: "Negative" },
              ].map((item) => (
                <label key={item.value} className="flex items-center gap-2">
                  <input type="radio" checked={interaction.sentiment === item.value} readOnly />
                  <span>{item.label}</span>
                </label>
              ))}
            </div>

            <div className="mt-3">
              <p className="mb-1 text-[22px] font-semibold text-[#3a4a60]">Outcomes</p>
              <textarea
                className="w-full rounded-md border border-[#cfd6de] bg-white px-3 py-2 text-[17px] text-[#3c495b] placeholder:text-[#9aa4b2]"
                rows={3}
                placeholder="Key outcomes or agreements..."
                value={interaction.outcomes || ""}
                readOnly
              />
            </div>

            <div className="mt-3">
              <p className="mb-1 text-[22px] font-semibold text-[#3a4a60]">Follow-up Actions</p>
              <textarea
                className="w-full rounded-md border border-[#cfd6de] bg-white px-3 py-2 text-[17px] text-[#3c495b] placeholder:text-[#9aa4b2]"
                rows={3}
                placeholder="Enter next steps or tasks..."
                value={(interaction.followUpActions || []).map((item) => formatActionItem(item)).filter(Boolean).join(", ")}
                readOnly
              />
            </div>
            <div className="mt-2 text-[18px] text-[#486fd2]">
              <p className="font-semibold text-[#4a5a70]">AI Suggested Follow-ups:</p>
              <ul className="pl-0">
                {(interaction.aiSuggestedFollowUps || []).map((item, idx) => (
                  <li key={`${item?.action || "follow-up"}-${idx}`} className="leading-7">
                    + {formatActionItem(item) || JSON.stringify(item)}
                    {item?.rationale ? ` - ${item.rationale}` : ""}
                  </li>
                ))}
              </ul>
            </div>

            <div className="mt-3">
              <p className="mb-1 text-[22px] font-semibold text-[#3a4a60]">AI Summary</p>
              <textarea
                className="w-full rounded-md border border-[#cfd6de] bg-[#fbfcfe] px-3 py-2 text-[17px] text-[#3c495b] placeholder:text-[#9aa4b2]"
                rows={4}
                placeholder="Generated call summary will appear here when you ask the AI to summarize the interaction..."
                value={cleanSummaryText(interaction.aiSummary)}
                readOnly
              />
            </div>
            <button className="mt-4 rounded-md bg-[#61738a] px-5 py-2 text-[17px] font-semibold text-white" type="submit">
              Log Interaction
            </button>
          </form>
          <section className="min-h-0 rounded-lg border border-[#d7dde4] bg-[#eef3f6] lg:flex lg:h-full lg:flex-col">
            <div className="border-b border-[#d7dde4] bg-[#f3f7fa] px-4 py-3">
              <h2 className="text-[34px] font-semibold text-[#2f72c4]">AI Assistant</h2>
              <p className="text-[17px] text-[#7d8898]">Log interaction details here via chat</p>
            </div>
            <div className="min-h-[280px] space-y-3 p-3 lg:flex-1 lg:overflow-y-auto">
              {chat.messages.length === 0 && (
                <div className="rounded-md border border-[#e0e6ee] bg-white p-3 text-[16px] font-semibold leading-6 text-[#39495e]">{initialMessage}</div>
              )}
              {chat.error && <p className="mb-2 rounded-md bg-red-50 p-2 text-[15px] text-red-700">{chat.error}</p>}
              {chat.messages.map((message) => (
                <div
                  key={message.id}
                  className={`rounded-md border p-3 text-[17px] leading-6 ${
                    message.role === "assistant" ? "border-[#b8e4c0] bg-[#dbf3df] text-[#395246]" : "border-[#d7dde4] bg-white text-[#38485c]"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  {message.tool_used && <p className="mt-1 text-[13px] text-[#486fd2]">Tool: {message.tool_used}</p>}
                </div>
              ))}
            </div>
            <div className="flex items-end gap-2 border-t border-[#d7dde4] bg-[#f8fbfd] p-3">
              <textarea
                className="h-11 max-h-24 min-h-[42px] flex-1 resize-y rounded-md border border-[#cfd6de] bg-white px-3 py-2 text-[16px] text-[#39495e] placeholder:text-[#9ba6b3]"
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                placeholder="Describe interaction..."
                rows={1}
              />
              <button
                className="h-11 rounded-full bg-[#707786] px-6 text-[17px] font-semibold text-white disabled:opacity-60"
                onClick={onSend}
                type="button"
                disabled={chat.isLoading}
              >
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
