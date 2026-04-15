import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { useDispatch, useSelector } from "react-redux";

import { sendChatMessage, submitInteraction } from "./store/interactionThunks";
import { applyFormUpdates } from "./store/interactionSlice";

const initialMessage =
  'Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure").';

function App() {
  const dispatch = useDispatch();
  const interaction = useSelector((state) => state.interaction);
  const chat = useSelector((state) => state.chat);
  const [prompt, setPrompt] = useState("");
  const sessionId = useMemo(() => crypto.randomUUID(), []);

  const { register, handleSubmit, setValue } = useForm({ values: interaction });

  const onSend = async () => {
    if (!prompt.trim()) return;
    const result = await dispatch(sendChatMessage({ message: prompt, context: interaction, sessionId }));
    if (result.payload?.form_updates) {
      dispatch(applyFormUpdates(result.payload.form_updates));
      Object.entries(result.payload.form_updates).forEach(([key, value]) => setValue(key, value));
    }
    setPrompt("");
  };

  return (
    <div className="min-h-screen bg-[#f8f9fa] p-3 md:p-6">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-4 text-2xl font-semibold text-slate-900">Log HCP Interaction</h1>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
          <form
            className="lg:col-span-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
            onSubmit={handleSubmit((values) => dispatch(submitInteraction(values)))}
          >
            <p className="mb-4 text-sm font-semibold text-slate-700">Interaction Details (AI-controlled)</p>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <input className="rounded border p-2" placeholder="HCP Name" {...register("hcp")} readOnly />
              <input className="rounded border p-2" placeholder="Interaction Type" {...register("interactionType")} readOnly />
              <input className="rounded border p-2" type="date" {...register("date")} readOnly />
              <input className="rounded border p-2" type="time" {...register("time")} readOnly />
            </div>
            <textarea className="mt-3 w-full rounded border p-2" rows={4} placeholder="Topics Discussed" {...register("topicsDiscussed")} readOnly />
            <div className="mt-3 flex gap-3 text-sm">
              {["Positive", "Neutral", "Negative"].map((item) => (
                <label key={item} className="flex items-center gap-1">
                  <input type="radio" checked={interaction.sentiment === item} readOnly />
                  {item}
                </label>
              ))}
            </div>
            <textarea className="mt-3 w-full rounded border p-2" rows={3} placeholder="Outcomes" {...register("outcomes")} readOnly />
            <textarea className="mt-3 w-full rounded border p-2" rows={3} value={JSON.stringify(interaction.followUpActions)} readOnly />
            <button className="mt-4 rounded bg-blue-600 px-4 py-2 text-white" type="submit">
              Log Interaction
            </button>
          </form>
          <section className="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">AI Assistant</h2>
            <p className="mt-1 text-sm text-slate-500">Log interaction via chat</p>
            <div className="mt-3 h-[420px] overflow-y-auto rounded border bg-slate-50 p-3">
              {chat.messages.length === 0 && <p className="text-sm text-slate-500">{initialMessage}</p>}
              {chat.messages.map((message) => (
                <div key={message.id} className="mb-2 rounded bg-white p-2 text-sm shadow-sm">
                  <p className="font-semibold">{message.role}</p>
                  <p>{message.content}</p>
                  {message.tool_used && <p className="mt-1 text-xs text-blue-600">Tool: {message.tool_used}</p>}
                </div>
              ))}
            </div>
            <div className="mt-3 flex gap-2">
              <input className="flex-1 rounded border p-2" value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder="Describe interaction..." />
              <button className="rounded bg-slate-800 px-4 py-2 text-white" onClick={onSend} type="button" disabled={chat.isLoading}>
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
