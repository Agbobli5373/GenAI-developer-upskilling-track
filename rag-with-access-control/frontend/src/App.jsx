import { useState } from "react";
import {
  User,
  Search,
  Lock,
  AlertCircle,
  CheckCircle,
  Send,
} from "lucide-react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = "http://localhost:8000";

function App() {
  const [selectedRole, setSelectedRole] = useState("");
  const [token, setToken] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const roles = [
    {
      id: "hr",
      name: "HR Manager",
      description: "Access HR documents and policies",
      icon: "👥",
    },
    {
      id: "engineering",
      name: "Software Engineer",
      description: "Access technical documentation",
      icon: "👨‍💻",
    },
    {
      id: "public",
      name: "Public User",
      description: "Access public information only",
      icon: "🌐",
    },
  ];

  const sampleQuestions = {
    hr: [
      "What are the performance review guidelines?",
      "What are the salary bands for engineers?",
      "What is our vacation policy?",
    ],
    engineering: [
      "How does our CI/CD pipeline work?",
      "What are our architecture patterns?",
      "What testing frameworks do we use?",
    ],
    public: [
      "What is the company mission?",
      "What products does the company offer?",
      "How can I contact support?",
    ],
  };

  const handleLogin = async () => {
    if (!selectedRole) {
      setError("Please select a role first");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        role: selectedRole,
      });

      setToken(response.data.access_token);
      setIsAuthenticated(true);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!question.trim()) {
      setError("Please enter a question");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/rag`,
        { question: question.trim() },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setAnswer(response.data.answer);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Query failed");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken("");
    setIsAuthenticated(false);
    setSelectedRole("");
    setQuestion("");
    setAnswer("");
    setError("");
  };

  const handleSampleQuestion = (sampleQ) => {
    setQuestion(sampleQ);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>
            <Lock className="header-icon" />
            RAG with Access Control
          </h1>
          <p>Secure document retrieval with role-based access</p>
        </div>
      </header>

      <main className="app-main">
        {!isAuthenticated ? (
          <div className="auth-section">
            <div className="auth-card">
              <h2>
                <User className="section-icon" />
                Select Your Role
              </h2>

              <div className="roles-grid">
                {roles.map((role) => (
                  <div
                    key={role.id}
                    className={`role-card ${
                      selectedRole === role.id ? "selected" : ""
                    }`}
                    onClick={() => setSelectedRole(role.id)}
                  >
                    <div className="role-icon">{role.icon}</div>
                    <h3>{role.name}</h3>
                    <p>{role.description}</p>
                  </div>
                ))}
              </div>

              {selectedRole && (
                <div className="auth-actions">
                  <button
                    onClick={handleLogin}
                    disabled={loading}
                    className="login-btn"
                  >
                    {loading ? "Authenticating..." : "Login"}
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="query-section">
            <div className="user-info">
              <div className="user-badge">
                <CheckCircle className="check-icon" />
                Logged in as:{" "}
                <strong>
                  {roles.find((r) => r.id === selectedRole)?.name}
                </strong>
                <button onClick={handleLogout} className="logout-btn">
                  Logout
                </button>
              </div>
            </div>

            <div className="query-card">
              <h2>
                <Search className="section-icon" />
                Ask a Question
              </h2>

              <div className="sample-questions">
                <h3>
                  Sample Questions for{" "}
                  {roles.find((r) => r.id === selectedRole)?.name}:
                </h3>
                <div className="questions-list">
                  {sampleQuestions[selectedRole]?.map((sampleQ, index) => (
                    <button
                      key={index}
                      onClick={() => handleSampleQuestion(sampleQ)}
                      className="sample-question-btn"
                    >
                      {sampleQ}
                    </button>
                  ))}
                </div>
              </div>

              <div className="query-input">
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Type your question here..."
                  rows={3}
                  className="question-textarea"
                />
                <button
                  onClick={handleQuery}
                  disabled={loading || !question.trim()}
                  className="query-btn"
                >
                  <Send className="btn-icon" />
                  {loading ? "Processing..." : "Ask Question"}
                </button>
              </div>

              {answer && (
                <div className="answer-section">
                  <h3>Answer:</h3>
                  <div className="answer-content">{answer}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <AlertCircle className="error-icon" />
            {error}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
