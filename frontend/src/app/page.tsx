"use client";

import { useEffect, useMemo, useState } from "react";

type ChatMessage = { sender: string; message: string };
type EmployeeState = {
  name: string;
  level: string;
  task: string;
  question: string;
  ai_attempts: number;
  stuck: boolean;
  mentor_requested: boolean;
  mentor_alert: null | {
    employee: string;
    employee_level: string;
    task: string;
    blocker: string;
    ai_attempts: number;
  };
  understood: boolean;
  chat: ChatMessage[];
};

type ApiState = {
  task: {
    title: string;
    assigned_employee: string;
    deadline: string;
    status: string;
    steps: { label: string; status: string }[];
  };
  employees: {
    employeeA: EmployeeState;
    employeeB: EmployeeState;
  };
  recent_blockers: {
    employee: string;
    task: string;
    blocker: string;
    ai_attempts: number;
    status: string;
  }[];
  mentor_interventions: number;
  completed_tasks: number;
  active_tasks: number;
  blocked_employees: number;
};

type MemoryCard = {
  id: number;
  problem: string;
  ai_explanation: string;
  mentor_explanation: string;
  outcome: string;
  successful_approach: string;
  technologies: string;
  used_to_help_employee: string;
};

type DemoResponse = {
  state: ApiState;
  memory_cards: MemoryCard[];
  team_learning_insights: {
    label: string;
    recurring_knowledge_gap: string;
    employees_affected: number;
    successful_resolution: number;
    recommended_action: string;
  };
  hindsight: { enabled: boolean; base_url_configured: boolean };
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const statusBadge = (status: string) => {
  if (status === "done") return "bg-emerald-100 text-emerald-700";
  if (status === "active") return "bg-blue-100 text-blue-700";
  return "bg-slate-100 text-slate-600";
};

export default function Home() {
  const [data, setData] = useState<DemoResponse | null>(null);
  const [tab, setTab] = useState<"manager" | "employee" | "memory">("manager");
  const [selectedEmployee, setSelectedEmployee] = useState<"employeeA" | "employeeB">(
    "employeeA"
  );
  const [question, setQuestion] = useState(
    "I don't understand how the API connects to the database."
  );
  const [mentorText, setMentorText] = useState(
    "Think of the API as a receptionist. It receives the employee information and passes it to the database layer, which stores the information."
  );
  const [lastAi, setLastAi] = useState<{ answer: string; used_memory: boolean } | null>(null);
  const [loading, setLoading] = useState(false);

  const employee = useMemo(
    () => data?.state.employees[selectedEmployee],
    [data, selectedEmployee]
  );

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`${API_BASE}/api/demo/state`);
      const json = (await res.json()) as DemoResponse;
      setData(json);
    };
    void load();
  }, []);

  const runDemo = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/demo/run`, { method: "POST" });
      const json = (await res.json()) as DemoResponse;
      setData(json);
      setSelectedEmployee("employeeA");
      setTab("manager");
      setLastAi(null);
    } finally {
      setLoading(false);
    }
  };

  const askAi = async () => {
    if (!employee) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/demo/ask-ai`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ employee_id: selectedEmployee, question }),
      });
      const json = await res.json();
      setData((prev) => (prev ? { ...prev, state: json.state } : prev));
      setLastAi({ answer: json.answer, used_memory: json.used_memory });
    } finally {
      setLoading(false);
    }
  };

  const postSimple = async (path: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ employee_id: selectedEmployee }),
      });
      const json = await res.json();
      setData((prev) =>
        prev
          ? {
              ...prev,
              state: json.state,
              memory_cards: json.memory_cards || prev.memory_cards,
            }
          : prev
      );
    } finally {
      setLoading(false);
    }
  };

  const mentorResolve = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/demo/mentor-resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          employee_id: selectedEmployee,
          mentor_explanation: mentorText,
        }),
      });
      const json = await res.json();
      setData((prev) =>
        prev
          ? {
              ...prev,
              state: json.state,
              memory_cards: json.memory_cards || prev.memory_cards,
            }
          : prev
      );
    } finally {
      setLoading(false);
    }
  };

  if (!data) {
    return <main className="p-6">Loading TeamMento AI...</main>;
  }

  return (
    <main className="mx-auto max-w-7xl p-6">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-white p-5 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold">TeamMento AI</h1>
          <p className="text-sm text-slate-500">
            Every problem solved by your team becomes knowledge for the next employee.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={runDemo}
            disabled={loading}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Run Demo
          </button>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            Hindsight {data.hindsight.enabled ? "Connected" : "Config Needed"}
          </span>
        </div>
      </header>

      <div className="mb-6 flex gap-2">
        {[
          ["manager", "Manager Dashboard"],
          ["employee", "Employee / AI Mentor"],
          ["memory", "Team Memory"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key as "manager" | "employee" | "memory")}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === key ? "bg-blue-600 text-white" : "bg-white text-slate-600"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "manager" && (
        <section className="grid gap-4 lg:grid-cols-3">
          {[ 
            ["Active tasks", data.state.active_tasks],
            ["Completed tasks", data.state.completed_tasks],
            ["Blocked employees", data.state.blocked_employees],
            ["Mentor interventions", data.state.mentor_interventions],
          ].map(([k, v]) => (
            <div key={k} className="rounded-xl bg-white p-4 shadow-sm">
              <p className="text-sm text-slate-500">{k}</p>
              <p className="mt-2 text-2xl font-bold">{v}</p>
            </div>
          ))}
          <div className="rounded-xl bg-white p-4 shadow-sm lg:col-span-2">
            <h3 className="font-semibold">Assign Task</h3>
            <p className="mt-2 text-sm text-slate-600">Task: {data.state.task.title}</p>
            <p className="text-sm text-slate-600">Employee: Manu</p>
            <p className="text-sm text-slate-600">Deadline: Today</p>
            <button
              onClick={runDemo}
              className="mt-3 rounded-lg bg-slate-900 px-4 py-2 text-sm text-white"
            >
              Assign with AI Mentor
            </button>
          </div>
          <div className="rounded-xl bg-white p-4 shadow-sm">
            <h3 className="font-semibold">Recent Blockers</h3>
            <div className="mt-2 space-y-2 text-sm">
              {data.state.recent_blockers.length === 0 && (
                <p className="text-slate-500">No blockers yet.</p>
              )}
              {data.state.recent_blockers.map((b, i) => (
                <div key={`${b.employee}-${i}`} className="rounded-lg bg-slate-50 p-2">
                  <p className="font-medium">{b.employee}</p>
                  <p className="text-slate-600">{b.blocker}</p>
                  <p className="text-xs text-slate-400">AI attempts: {b.ai_attempts}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {tab === "employee" && employee && (
        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl bg-white p-4 shadow-sm lg:col-span-2">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-semibold">Task: {employee.task}</h3>
              <select
                value={selectedEmployee}
                onChange={(e) => setSelectedEmployee(e.target.value as "employeeA" | "employeeB")}
                className="rounded-lg border border-slate-200 px-3 py-1 text-sm"
              >
                <option value="employeeA">Employee A (Manu - Fresher)</option>
                <option value="employeeB">Employee B (Riya - Junior)</option>
              </select>
            </div>
            <ol className="mb-4 grid gap-2 text-sm">
              {data.state.task.steps.map((step, idx) => (
                <li
                  key={step.label}
                  className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2"
                >
                  <span>
                    {idx + 1}. {step.label}
                  </span>
                  <span className={`rounded-full px-2 py-1 text-xs ${statusBadge(step.status)}`}>
                    {step.status}
                  </span>
                </li>
              ))}
            </ol>

            <div className="mb-3 rounded-lg border border-slate-200 p-3">
              <p className="mb-2 text-sm font-medium">AI Mentor Chat</p>
              <div className="max-h-64 space-y-2 overflow-auto">
                {employee.chat.length === 0 && (
                  <p className="text-sm text-slate-500">Start the conversation with Ask AI.</p>
                )}
                {employee.chat.map((msg, idx) => (
                  <div
                    key={`${msg.sender}-${idx}`}
                    className={`rounded-lg px-3 py-2 text-sm ${
                      msg.sender === "employee"
                        ? "bg-blue-50"
                        : msg.sender === "mentor"
                          ? "bg-emerald-50"
                          : "bg-slate-50"
                    }`}
                  >
                    <p className="mb-1 text-xs font-semibold uppercase text-slate-500">{msg.sender}</p>
                    <p>{msg.message}</p>
                  </div>
                ))}
              </div>
            </div>

            {lastAi?.used_memory && (
              <div className="mb-3 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-700">
                🧠 Learned from previous team experience
              </div>
            )}

            <div className="grid gap-2 sm:grid-cols-2">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="rounded-lg border border-slate-200 px-3 py-2 text-sm sm:col-span-2"
              />
              <button
                onClick={askAi}
                disabled={loading}
                className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white"
              >
                Ask AI
              </button>
              <button
                onClick={() => postSimple("/api/demo/im-stuck")}
                disabled={loading}
                className="rounded-lg bg-amber-500 px-3 py-2 text-sm font-medium text-white"
              >
                I&apos;m Stuck
              </button>
              <button
                onClick={() => postSimple("/api/demo/request-mentor")}
                disabled={loading || employee.ai_attempts < 1}
                className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white"
              >
                Request Mentor
              </button>
              <button
                onClick={() => postSimple("/api/demo/understood")}
                disabled={loading}
                className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white"
              >
                Understood
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-xl bg-white p-4 shadow-sm">
              <h3 className="font-semibold">Mentor Alert</h3>
              {!employee.mentor_alert ? (
                <p className="mt-2 text-sm text-slate-500">No active mentor alert.</p>
              ) : (
                <div className="mt-2 text-sm text-slate-700">
                  <p>Employee: {employee.mentor_alert.employee}</p>
                  <p>Task: {employee.mentor_alert.task}</p>
                  <p>Blocker: {employee.mentor_alert.blocker}</p>
                  <p>AI attempts: {employee.mentor_alert.ai_attempts}</p>
                </div>
              )}
            </div>

            <div className="rounded-xl bg-white p-4 shadow-sm">
              <h3 className="font-semibold">Mentor Resolution</h3>
              <textarea
                value={mentorText}
                onChange={(e) => setMentorText(e.target.value)}
                className="mt-2 h-28 w-full rounded-lg border border-slate-200 p-2 text-sm"
              />
              <button
                onClick={mentorResolve}
                disabled={loading}
                className="mt-2 w-full rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white"
              >
                Save to Hindsight
              </button>
            </div>
          </div>
        </section>
      )}

      {tab === "memory" && (
        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl bg-white p-4 shadow-sm lg:col-span-2">
            <h3 className="mb-3 font-semibold">Team Memory (Hindsight-backed experiences)</h3>
            <div className="space-y-3">
              {data.memory_cards.map((card) => (
                <article key={card.id} className="rounded-lg border border-slate-200 p-3">
                  <p className="mb-1 font-semibold">🧠 Learned Experience</p>
                  <p className="text-sm"><b>Problem:</b> {card.problem}</p>
                  <p className="text-sm"><b>AI explanation:</b> {card.ai_explanation}</p>
                  <p className="text-sm"><b>Mentor explanation:</b> {card.mentor_explanation}</p>
                  <p className="text-sm"><b>Outcome:</b> {card.outcome}</p>
                  <p className="text-sm"><b>Learning:</b> {card.successful_approach}</p>
                  <p className="text-sm"><b>Technologies:</b> {card.technologies}</p>
                  <p className="text-sm text-blue-700">Used to help: {card.used_to_help_employee}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="rounded-xl bg-white p-4 shadow-sm">
            <h3 className="font-semibold">TEAM LEARNING INSIGHTS</h3>
            <p className="mt-2 text-xs text-slate-500">{data.team_learning_insights.label}</p>
            <div className="mt-3 space-y-2 text-sm">
              <p>
                <b>Recurring knowledge gap:</b> {data.team_learning_insights.recurring_knowledge_gap}
              </p>
              <p>
                <b>Employees affected:</b> {data.team_learning_insights.employees_affected}
              </p>
              <p>
                <b>Successful resolution:</b> {data.team_learning_insights.successful_resolution}
              </p>
              <p>
                <b>Recommended action:</b> {data.team_learning_insights.recommended_action}
              </p>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
