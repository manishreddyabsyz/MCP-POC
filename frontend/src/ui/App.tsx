import React, { useEffect, useMemo, useRef, useState } from "react";

type BackendResponse =
  | {
      type: "clarification";
      session_id: string;
      message: string;
      questions: string[];
    }
  | {
      type: "case_search_results";
      session_id: string;
      message: string;
      candidates: Array<{
        Id?: string;
        CaseNumber?: string;
        Subject?: string;
        Status?: string;
        Description?: string;
      }>;
    }
  | {
      type: "case_status";
      session_id: string;
      case_number?: string;
      status?: string;
      priority?: string;
      subject?: string;
      case_source?: string;
    }
  | {
      type: "in_progress_cases";
      session_id: string;
      count: number;
      message?: string;
      cases: Array<{
        Id?: string;
        CaseNumber?: string;
        Subject?: string;
        Status?: string;
        Priority?: string;
        LastModifiedDate?: string;
      }>;
    }
  | {
      type: "case_response";
      session_id: string;
      case_number?: string;
      case_type?: string;
      case_summary?: string;
      technical_summary?: string;
      troubleshooting_steps?: string[];
      next_actions?: string[];
      assumptions_and_gaps?: string[];
      tree?: { title: string; content: string; children: any[] };
      prompt_knowledge_article_confirmation?: string;
      case_source?: string;
    }
  | {
      type: "case_comments";
      session_id: string;
      case_id?: string;
      case_number?: string;
      comments: Array<{
        CommentBody?: string;
        CreatedDate?: string;
        CreatedBy?: { Name?: string };
      }>;
      message?: string;
    }
  | {
      type: "case_history";
      session_id: string;
      case_id?: string;
      case_number?: string;
      history: Array<{
        Field?: string;
        OldValue?: string;
        NewValue?: string;
        CreatedDate?: string;
        CreatedBy?: { Name?: string };
      }>;
      message?: string;
    }
  | {
      type: "case_feed";
      session_id: string;
      case_id?: string;
      case_number?: string;
      feed: Array<{
        Body?: string;
        Type?: string;
        CreatedDate?: string;
        CreatedBy?: { Name?: string };
      }>;
      message?: string;
    }
  | {
      type: "followup_answer";
      session_id: string;
      needs_clarification?: boolean;
      answer?: string;
      follow_up_questions?: string[];
      citations?: string[];
      stored_as_level2_knowledge?: boolean;
    }
  | {
      type: "knowledge_article";
      session_id: string;
      article: Record<string, unknown>;
    }
  | { type: "ok"; session_id: string; message: string }
  | { type: "error"; session_id: string; error: string; case_number?: string };

type ChatMsg =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; raw: BackendResponse }
  | { id: string; role: "assistant"; text: string; isError?: boolean; isTyping?: boolean };

function uuid() {
  return Math.random().toString(16).slice(2) + Date.now().toString(16);
}

function renderTree(node: any, indent = ""): string {
  if (!node) return "";
  const title = node.title ?? "Node";
  const content = node.content ? `: ${String(node.content)}` : "";
  let out = `${indent}- ${title}${content}\n`;
  const children = Array.isArray(node.children) ? node.children : [];
  for (const child of children) out += renderTree(child, indent + "  ");
  return out;
}

async function postQuery(query: string, session_id: string): Promise<BackendResponse> {
  const res = await fetch("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, session_id })
  });
  return (await res.json()) as BackendResponse;
}

export function App() {
  const [sessionId] = useState(() => `ui-${crypto?.randomUUID?.() ?? uuid()}`);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [msgs, setMsgs] = useState<ChatMsg[]>(() => [
    {
      id: uuid(),
      role: "assistant",
      text:
        "Hi — ask about a Salesforce case.\n\nExamples:\n- What is the status of case 00001163?\n- Summarize case 00001161\n- Show comments for case 00001163\n- Show history for case 00001161\n- Show feed for case 00001163\n- Are there any in progress cases?\n- Search: Return Order Issue RO-0017"
    }
  ]);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [msgs.length]);

  const headerChips = useMemo(
    () => [
      { label: "Session", value: sessionId },
      { label: "Endpoint", value: "POST /query" }
    ],
    [sessionId]
  );

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || busy) return;

    setMsgs((m) => [...m, { id: uuid(), role: "user", text: trimmed }]);
    setDraft("");
    setBusy(true);
    
    // Add typing indicator
    const typingId = uuid();
    setMsgs((m) => [...m, { id: typingId, role: "assistant", text: "", isTyping: true }]);
    
    try {
      const resp = await postQuery(trimmed, sessionId);
      // Remove typing indicator and add actual response
      setMsgs((m) => m.filter(msg => msg.id !== typingId).concat({ id: uuid(), role: "assistant", raw: resp }));
    } catch (e: any) {
      // Remove typing indicator and add error
      setMsgs((m) => m.filter(msg => msg.id !== typingId).concat({ 
        id: uuid(), 
        role: "assistant", 
        text: `Request failed: ${e?.message ?? String(e)}`, 
        isError: true 
      }));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <div className="topbar">
        <div className="brand">
          <div className="brandTitle">Salesforce MCP Agent Chat</div>
          <div className="brandSub">Chat UI → FastAPI `/query` → MCP tool (`ask`) → Salesforce + ChatGPT</div>
        </div>
        <div className="chipRow">
          {headerChips.map((c) => (
            <div key={c.label} className="chip">
              {c.label}: {c.value}
            </div>
          ))}
        </div>
      </div>

      <div className="card chat">
        <div className="messages" ref={scrollRef}>
          {msgs.map((m) => {
            if (m.role === "user") {
              return (
                <div key={m.id} className="row" style={{ justifyContent: "flex-end" }}>
                  <div className="bubble bubbleUser">{m.text}</div>
                  <div className="avatar">U</div>
                </div>
              );
            }

            if ("text" in m) {
              if (m.isTyping) {
                return (
                  <div key={m.id} className="row">
                    <div className="avatar">A</div>
                    <div className="bubble">
                      <div className="typingIndicator">
                        <div className="typingDots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              }
              
              return (
                <div key={m.id} className="row">
                  <div className="avatar">A</div>
                  <div className={"bubble " + (m.isError ? "bubbleErr" : "")}>{m.text}</div>
                </div>
              );
            }

            const r = m.raw;
            return (
              <div key={m.id} className="row">
                <div className="avatar">A</div>
                <div className="bubble">
                  <ResponseView resp={r} onQuickSend={(t) => send(t)} />
                </div>
              </div>
            );
          })}
        </div>

        <div className="composer">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Type a question… (Enter to send, Shift+Enter for newline)"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(draft);
              }
            }}
          />
          <button onClick={() => send(draft)} disabled={busy || !draft.trim()}>
            {busy ? "Sending…" : "Send"}
          </button>
        </div>
      </div>

      <div className="footer">
        <span>Tip: ask “Are there any in progress cases?” then click a CaseNumber to summarize.</span>
        <span>Session memory is kept server-side by `session_id`.</span>
      </div>
    </div>
  );
}

function ResponseView({ resp, onQuickSend }: { resp: BackendResponse; onQuickSend: (t: string) => void }) {
  if (resp.type === "clarification") {
    return (
      <>
        <div>{resp.message}</div>
        <div className="sections">
          <div className="section">
            <div className="sectionTitle">Follow-up questions</div>
            <ul className="list">
              {resp.questions.map((q) => (
                <li key={q}>{q}</li>
              ))}
            </ul>
          </div>
        </div>
      </>
    );
  }

  if (resp.type === "case_search_results") {
    return (
      <>
        <div>{resp.message}</div>
        <div className="sections">
          <div className="section">
            <div className="sectionTitle">Matches</div>
            <ul className="list">
              {resp.candidates.map((c) => {
                const cn = c.CaseNumber ?? "";
                return (
                  <li key={c.Id ?? cn}>
                    <button
                      style={{ height: 28, padding: "0 10px", marginRight: 8 }}
                      onClick={() => onQuickSend(`Summarize case ${cn}`)}
                      disabled={!cn}
                    >
                      {cn || "—"}
                    </button>
                    <span style={{ color: "rgba(232,236,255,0.9)" }}>{c.Subject}</span>{" "}
                    <span style={{ color: "rgba(232,236,255,0.65)" }}>({c.Status})</span>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </>
    );
  }

  if (resp.type === "case_status") {
    return (
      <>
        <div>
          Status of case <b>{resp.case_number}</b>: <b>{resp.status}</b>
        </div>
        <div className="meta">
          {resp.subject ? <span className="pill">Subject: {resp.subject}</span> : null}
          {resp.priority ? <span className="pill">Priority: {resp.priority}</span> : null}
          {resp.case_source ? <span className="pill">Source: {resp.case_source}</span> : null}
        </div>
      </>
    );
  }

  if (resp.type === "in_progress_cases") {
    return (
      <>
        <div>
          In progress cases: <b>{resp.count}</b>
        </div>
        {resp.message ? <div className="meta">{resp.message}</div> : null}
        <div className="sections">
          <div className="section">
            <div className="sectionTitle">Cases</div>
            <ul className="list">
              {resp.cases.map((c) => (
                <li key={c.Id ?? c.CaseNumber}>
                  <button
                    style={{ height: 28, padding: "0 10px", marginRight: 8 }}
                    onClick={() => onQuickSend(`Summarize case ${c.CaseNumber}`)}
                    disabled={!c.CaseNumber}
                  >
                    {c.CaseNumber}
                  </button>
                  <span>{c.Subject}</span>{" "}
                  <span style={{ color: "rgba(232,236,255,0.65)" }}>
                    ({c.Status}
                    {c.Priority ? `, ${c.Priority}` : ""})
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </>
    );
  }

  if (resp.type === "case_response") {
    return (
      <>
        <div>
          <b>Case {resp.case_number}</b> {resp.case_type ? <span className="pill">Type: {resp.case_type}</span> : null}
        </div>
        <div className="meta">
          {resp.case_source ? <span className="pill">Source: {resp.case_source}</span> : null}
        </div>
        <div className="sections">
          <div className="section">
            <div className="sectionTitle">Case summary</div>
            <div>{resp.case_summary}</div>
          </div>
          <div className="section">
            <div className="sectionTitle">Technical summary</div>
            <div>{resp.technical_summary}</div>
          </div>
          <div className="section">
            <div className="sectionTitle">Troubleshooting steps</div>
            <ul className="list">
              {(resp.troubleshooting_steps ?? []).map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
          </div>
          <div className="section">
            <div className="sectionTitle">Next immediate actions</div>
            <ul className="list">
              {(resp.next_actions ?? []).map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
          </div>
          {(resp.assumptions_and_gaps ?? []).length ? (
            <div className="section">
              <div className="sectionTitle">Assumptions & gaps</div>
              <ul className="list">
                {(resp.assumptions_and_gaps ?? []).map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {resp.tree ? (
            <div className="section">
              <div className="sectionTitle">Tree view</div>
              <div className="tree">{renderTree(resp.tree)}</div>
            </div>
          ) : null}
          {resp.prompt_knowledge_article_confirmation ? (
            <div className="section">
              <div className="sectionTitle">Knowledge article</div>
              <div>{resp.prompt_knowledge_article_confirmation}</div>
              <div className="meta">
                <button style={{ height: 32 }} onClick={() => onQuickSend("confirm")}>
                  Confirm
                </button>
                <button style={{ height: 32 }} onClick={() => onQuickSend("cancel")}>
                  Cancel
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </>
    );
  }

  if (resp.type === "case_comments") {
    return (
      <>
        <div>
          <b>Comments for Case {resp.case_number}</b>
        </div>
        {resp.message ? <div className="meta">{resp.message}</div> : null}
        {resp.comments.length > 0 ? (
          <div className="sections">
            <div className="section">
              <div className="sectionTitle">Case Comments ({resp.comments.length})</div>
              <div className="commentsList">
                {resp.comments.map((comment, index) => (
                  <div key={index} className="commentItem">
                    <div className="commentHeader">
                      <span className="commentAuthor">
                        {comment.CreatedBy?.Name || 'Unknown User'}
                      </span>
                      <span className="commentDate">
                        {comment.CreatedDate ? new Date(comment.CreatedDate).toLocaleString() : ''}
                      </span>
                    </div>
                    <div className="commentBody">
                      {comment.CommentBody || 'No comment body'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </>
    );
  }

  if (resp.type === "case_history") {
    return (
      <>
        <div>
          <b>History for Case {resp.case_number}</b>
        </div>
        {resp.message ? <div className="meta">{resp.message}</div> : null}
        {resp.history.length > 0 ? (
          <div className="sections">
            <div className="section">
              <div className="sectionTitle">Case History ({resp.history.length})</div>
              <div className="historyList">
                {resp.history.map((change, index) => (
                  <div key={index} className="historyItem">
                    <div className="historyHeader">
                      <span className="historyField">{change.Field}</span>
                      <span className="historyAuthor">
                        by {change.CreatedBy?.Name || 'Unknown User'}
                      </span>
                      <span className="historyDate">
                        {change.CreatedDate ? new Date(change.CreatedDate).toLocaleString() : ''}
                      </span>
                    </div>
                    <div className="historyChange">
                      <span className="oldValue">
                        From: <em>{change.OldValue || '(empty)'}</em>
                      </span>
                      <span className="newValue">
                        To: <em>{change.NewValue || '(empty)'}</em>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </>
    );
  }

  if (resp.type === "case_feed") {
    return (
      <>
        <div>
          <b>Feed for Case {resp.case_number}</b>
        </div>
        {resp.message ? <div className="meta">{resp.message}</div> : null}
        {resp.feed.length > 0 ? (
          <div className="sections">
            <div className="section">
              <div className="sectionTitle">Case Feed ({resp.feed.length})</div>
              <div className="feedList">
                {resp.feed.map((item, index) => (
                  <div key={index} className="feedItem">
                    <div className="feedHeader">
                      <span className="feedType pill">{item.Type || 'Activity'}</span>
                      <span className="feedAuthor">
                        {item.CreatedBy?.Name || 'System'}
                      </span>
                      <span className="feedDate">
                        {item.CreatedDate ? new Date(item.CreatedDate).toLocaleString() : ''}
                      </span>
                    </div>
                    {item.Body ? (
                      <div className="feedBody">
                        {item.Body}
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </>
    );
  }

  if (resp.type === "followup_answer") {
    return (
      <>
        <div>{resp.answer}</div>
        {(resp.follow_up_questions ?? []).length ? (
          <div className="sections">
            <div className="section">
              <div className="sectionTitle">Follow-up questions</div>
              <ul className="list">
                {(resp.follow_up_questions ?? []).map((q) => (
                  <li key={q}>{q}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : null}
      </>
    );
  }

  if (resp.type === "knowledge_article") {
    return (
      <>
        <div className="sectionTitle">Knowledge article draft</div>
        <div className="tree">{JSON.stringify(resp.article, null, 2)}</div>
      </>
    );
  }

  if (resp.type === "ok") return <div>{resp.message}</div>;
  if (resp.type === "error") return <div className="bubbleErr">{resp.error}</div>;

  return <div className="tree">{JSON.stringify(resp, null, 2)}</div>;
}

