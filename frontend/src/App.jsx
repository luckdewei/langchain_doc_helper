import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";

const API_URL = "http://localhost:8000/chat";

function MessageBubble({ msg }) {
  const isUser = msg.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 16,
      }}
    >
      {!isUser && (
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            background: "#1677ff",
            color: "white",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 14,
            fontWeight: "bold",
            marginRight: 8,
            flexShrink: 0,
          }}
        >
          AI
        </div>
      )}

      <div
        style={{
          maxWidth: "75%",
          padding: "10px 16px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          background: isUser ? "#1677ff" : "#f0f2f5",
          color: isUser ? "white" : "#1a1a1a",
          fontSize: 15,
          lineHeight: 1.6,
        }}
      >
        {isUser ? (
          msg.content
        ) : msg.content ? (
          <ReactMarkdown
            components={{
              code({ inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={oneLight}
                    language={match[1]}
                    PreTag="div"
                    customStyle={{
                      borderRadius: 8,
                      fontSize: 13,
                      margin: "8px 0",
                    }}
                    {...props}
                  >
                    {String(children).replace(/\n$/, "")}
                  </SyntaxHighlighter>
                ) : (
                  <code
                    style={{
                      background: "#e8e8e8",
                      color: "#d63384",
                      padding: "2px 6px",
                      borderRadius: 4,
                      fontSize: 13,
                    }}
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
              p({ children }) {
                return <p style={{ margin: "4px 0" }}>{children}</p>;
              },
              ul({ children }) {
                return (
                  <ul style={{ paddingLeft: 20, margin: "4px 0" }}>
                    {children}
                  </ul>
                );
              },
              ol({ children }) {
                return (
                  <ol style={{ paddingLeft: 20, margin: "4px 0" }}>
                    {children}
                  </ol>
                );
              },
            }}
            remarkPlugins={[remarkGfm]}
          >
            {msg.content}
          </ReactMarkdown>
        ) : (
          <span style={{ opacity: 0.4 }}>▌</span>
        )}
      </div>

      {isUser && (
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            background: "#e0e0e0",
            color: "#555",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 14,
            fontWeight: "bold",
            marginLeft: 8,
            flexShrink: 0,
          }}
        >
          我
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "ai",
      content:
        "你好！我是 LangChain 文档助手，有什么关于 LangChain 的问题都可以问我 😊",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setLoading(true);

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setMessages((prev) => [...prev, { role: "ai", content: "" }]);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) throw new Error(`请求失败: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: updated[updated.length - 1].content + chunk,
          };
          return updated;
        });
      }
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content: `请求出错：${err.message}`,
        };
        return updated;
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function clearChat() {
    setMessages([{ role: "ai", content: "对话已清空，有什么问题尽管问我 😊" }]);
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        maxWidth: 860,
        margin: "0 auto",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      }}
    >
      {/* 顶部栏 */}
      <div
        style={{
          padding: "16px 24px",
          borderBottom: "1px solid #e8e8e8",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "white",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 8,
              background: "#1677ff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span style={{ color: "white", fontSize: 18 }}>🦜</span>
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 16 }}>
              LangChain 文档助手
            </div>
            <div style={{ fontSize: 12, color: "#888" }}>
              基于官方文档 · RAG 驱动
            </div>
          </div>
        </div>
        <button
          onClick={clearChat}
          style={{
            padding: "6px 14px",
            borderRadius: 6,
            border: "1px solid #e0e0e0",
            background: "white",
            color: "#666",
            cursor: "pointer",
            fontSize: 13,
          }}
        >
          清空对话
        </button>
      </div>

      {/* 消息区域 */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "24px 24px 8px",
          background: "#fafafa",
        }}
      >
        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}
        {loading && (
          <div
            style={{
              textAlign: "center",
              color: "#aaa",
              fontSize: 13,
              marginBottom: 8,
            }}
          >
            正在思考中...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div
        style={{
          padding: "16px 24px",
          borderTop: "1px solid #e8e8e8",
          background: "white",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 10,
            alignItems: "flex-end",
            background: "#f5f5f5",
            borderRadius: 12,
            padding: "8px 8px 8px 16px",
            border: "1px solid #e0e0e0",
          }}
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="问一个关于 LangChain 的问题...（Enter 发送，Shift+Enter 换行）"
            disabled={loading}
            rows={1}
            style={{
              flex: 1,
              border: "none",
              outline: "none",
              background: "transparent",
              fontSize: 15,
              resize: "none",
              lineHeight: 1.6,
              maxHeight: 120,
              overflowY: "auto",
              fontFamily: "inherit",
            }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={{
              width: 36,
              height: 36,
              borderRadius: 8,
              border: "none",
              background: loading || !input.trim() ? "#ccc" : "#1677ff",
              color: "white",
              cursor: loading || !input.trim() ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 16,
              flexShrink: 0,
              transition: "background 0.2s",
            }}
          >
            ↑
          </button>
        </div>
        <div
          style={{
            textAlign: "center",
            fontSize: 12,
            color: "#bbb",
            marginTop: 8,
          }}
        >
          内容基于 LangChain 官方文档生成，仅供参考
        </div>
      </div>
    </div>
  );
}
