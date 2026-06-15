import React, { useState } from "react";
import { useTheme } from "../context/ThemeContext";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/common/Navbar";
import Footer from "../components/common/Footer";
import { ArrowLeft, Send, CheckCircle, BarChart3 } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const Analytics = ({ onNavigate }) => {
  const { user } = useAuth();
  const { colors, mode } = useTheme();

  const [formData, setFormData] = useState({
    logoQuality: "",
    videoQuality: "",
    generationTime: "",
    scheduling: "",
    comments: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackResponse, setFeedbackResponse] = useState(null);

  const [sentimentStats, setSentimentStats] = useState({
    positive: 0,
    negative: 0,
    neutral: 0,
    total: 0,
  });

  const fetchSentimentStats = async () => {
    try {
      const resp = await fetch(`${API_BASE_URL}/api/sentiment-stats`);
      if (resp.ok) {
        const data = await resp.json();
        setSentimentStats(data);
      }
    } catch (e) {
      console.error("Failed to fetch sentiment statistics:", e);
    }
  };

  const handleTextChange = (field, value) => {
    // Enforce letters and spaces only, stripping out numbers and symbols
    const cleanValue = value.replace(/[^a-zA-Z\s]/g, "");
    setFormData((prev) => ({ ...prev, [field]: cleanValue }));
  };

  const handleCommentsChange = (e) => {
    handleTextChange("comments", e.target.value);
  };

  const getPercentage = (value, total) => {
    if (!total) return 0;
    return Math.round((value / total) * 100);
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!formData.logoQuality || !formData.videoQuality || !formData.generationTime || !formData.scheduling || !formData.comments.trim()) {
      alert("Please answer all questions before submitting.");
      return;
    }

    setIsSubmitting(true);
    setFeedbackResponse(null);
    try {
      const resp = await fetch(`${API_BASE_URL}/api/submit-feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await resp.json();
      if (resp.ok) {
        setFeedbackResponse({ type: "success", message: data.message, sentiment: data.sentiment });
        setFormData({ logoQuality: "", videoQuality: "", generationTime: "", scheduling: "", comments: "" });
        fetchSentimentStats();
      } else {
        setFeedbackResponse({ type: "error", message: data.error || "Failed to submit feedback" });
      }
    } catch (err) {
      setFeedbackResponse({ type: "error", message: "Server error occurred while submitting feedback." });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Donut/Pie chart calculations
  const donutRadius = 65;
  const donutCircumference = 2 * Math.PI * donutRadius;
  const totalSentiment = sentimentStats.total || 0;

  const posPct = totalSentiment ? (sentimentStats.positive / totalSentiment) : 0;
  const neuPct = totalSentiment ? (sentimentStats.neutral / totalSentiment) : 0;
  const negPct = totalSentiment ? (sentimentStats.negative / totalSentiment) : 0;

  const donutSegments = [
    { label: "Positive", pct: posPct, color: "#10B981", offset: 0 },
    { label: "Neutral", pct: neuPct, color: "#F59E0B", offset: -(posPct * donutCircumference) },
    { label: "Negative", pct: negPct, color: "#EF4444", offset: -((posPct + neuPct) * donutCircumference) },
  ];

  // Bar chart calculations
  const maxPct = Math.max(posPct, neuPct, negPct, 0.1);
  const barChartHeight = 140;
  const baseLineY = 160;

  const getBarHeight = (pct) => {
    return (pct / maxPct) * barChartHeight;
  };

  const drawBarPath = (x, y, w, bottom) => {
    const r = 6;
    const h = bottom - y;
    if (h <= r) {
      return `M ${x} ${bottom} L ${x} ${y} L ${x + w} ${y} L ${x + w} ${bottom} Z`;
    }
    return `M ${x} ${bottom} 
            L ${x} ${y + r} 
            Q ${x} ${y} ${x + r} ${y} 
            L ${x + w - r} ${y} 
            Q ${x + w} ${y} ${x + w} ${y + r} 
            L ${x + w} ${bottom} 
            Z`;
  };

  return (
    <div style={{ minHeight: "100vh", background: colors.bg1, color: colors.text1, fontFamily: "'Inter', sans-serif", transition: "background 0.3s ease" }}>
      <Navbar onNavigate={onNavigate} />

      <div style={{ maxWidth: 1240, margin: "40px auto", padding: "0 24px", paddingTop: 80 }}>
        {/* Navigation / Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
          <div>
            <button
              onClick={() => onNavigate("dashboard")}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                background: "none",
                border: "none",
                color: colors.primary,
                cursor: "pointer",
                fontSize: "1rem",
                fontWeight: 600,
                padding: 0,
                marginBottom: 12,
                transition: "transform 0.2s ease"
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = "translateX(-4px)"}
              onMouseLeave={(e) => e.currentTarget.style.transform = "translateX(0)"}
            >
              <ArrowLeft size={16} /> Back to Dashboard
            </button>
            <h1 style={{ fontSize: "2.2rem", fontWeight: 800, margin: 0, fontFamily: "'Outfit', sans-serif" }}>Feedback Analytics</h1>
          </div>
        </div>

        {/* Main Feedback Form & Charts Container (Centered) */}
        <div style={{ maxWidth: 680, margin: "0 auto 48px auto", display: "flex", flexDirection: "column", gap: 32 }}>
          
          {/* Feedback Form Card */}
          <div style={{
            background: colors.bg2,
            border: `1px solid ${colors.border}`,
            borderRadius: 24,
            padding: 32,
            boxShadow: mode === "dark" ? "none" : "0 10px 30px rgba(0,0,0,0.03)"
          }}>
            <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginTop: 0, marginBottom: 8, color: colors.text1, fontFamily: "'Outfit', sans-serif" }}>
              Submit Platform Feedback
            </h2>
            <p style={{ color: colors.text2, fontSize: "0.95rem", marginTop: 0, marginBottom: 28 }}>
              Let us know how we can improve. All fields are required.
            </p>

            {feedbackResponse && (
              <div style={{
                padding: 16,
                borderRadius: 16,
                marginBottom: 24,
                background: feedbackResponse.type === "success" ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.08)",
                border: feedbackResponse.type === "success" ? "1px solid #10B981" : "1px solid #EF4444",
                display: "flex",
                flexDirection: "column",
                gap: 4
              }}>
                <div style={{ fontWeight: 700, color: feedbackResponse.type === "success" ? "#10B981" : "#EF4444", display: "flex", alignItems: "center", gap: 8 }}>
                  <CheckCircle size={18} /> {feedbackResponse.message}
                </div>
                {feedbackResponse.sentiment && (
                  <div style={{ fontSize: "0.9rem", color: colors.text2 }}>
                    Sentiment analysis identified this feedback as: <strong style={{ color: colors.text1, textTransform: "capitalize" }}>{feedbackResponse.sentiment}</strong>
                  </div>
                )}
              </div>
            )}

            <form onSubmit={handleFeedbackSubmit} style={{ display: "flex", flexDirection: "column", gap: 24 }}>
              
              {/* Question 1: Logo Quality */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, borderBottom: `1px solid ${colors.border}22`, paddingBottom: 16 }}>
                <label style={{ fontSize: "0.95rem", fontWeight: "600", color: colors.text1 }}>
                  1. How satisfied are you with the quality of generated Logos & Posters? (Letters and spaces only)
                </label>
                <input
                  type="text"
                  value={formData.logoQuality}
                  onChange={(e) => handleTextChange("logoQuality", e.target.value)}
                  placeholder="e.g. Excellent logo quality, clean designs"
                  required
                  style={{
                    width: "100%",
                    padding: 14,
                    borderRadius: 14,
                    border: `1px solid ${colors.border}`,
                    background: mode === "dark" ? "rgba(0,0,0,0.2)" : "white",
                    color: colors.text1,
                    outline: "none",
                    fontSize: "0.95rem",
                    boxSizing: "border-box",
                    transition: "border-color 0.2s ease"
                  }}
                  onFocus={(e) => e.target.style.borderColor = colors.primary}
                  onBlur={(e) => e.target.style.borderColor = colors.border}
                />
              </div>

              {/* Question 2: Video Quality */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, borderBottom: `1px solid ${colors.border}22`, paddingBottom: 16 }}>
                <label style={{ fontSize: "0.95rem", fontWeight: "600", color: colors.text1 }}>
                  2. How satisfied are you with the quality of generated Video Ads? (Letters and spaces only)
                </label>
                <input
                  type="text"
                  value={formData.videoQuality}
                  onChange={(e) => handleTextChange("videoQuality", e.target.value)}
                  placeholder="e.g. Video transition and quality was amazing"
                  required
                  style={{
                    width: "100%",
                    padding: 14,
                    borderRadius: 14,
                    border: `1px solid ${colors.border}`,
                    background: mode === "dark" ? "rgba(0,0,0,0.2)" : "white",
                    color: colors.text1,
                    outline: "none",
                    fontSize: "0.95rem",
                    boxSizing: "border-box",
                    transition: "border-color 0.2s ease"
                  }}
                  onFocus={(e) => e.target.style.borderColor = colors.primary}
                  onBlur={(e) => e.target.style.borderColor = colors.border}
                />
              </div>

              {/* Question 3: Generation Speed */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, borderBottom: `1px solid ${colors.border}22`, paddingBottom: 16 }}>
                <label style={{ fontSize: "0.95rem", fontWeight: "600", color: colors.text1 }}>
                  3. How would you rate the speed of asset generation? (Letters and spaces only)
                </label>
                <input
                  type="text"
                  value={formData.generationTime}
                  onChange={(e) => handleTextChange("generationTime", e.target.value)}
                  placeholder="e.g. Generation speed was very fast"
                  required
                  style={{
                    width: "100%",
                    padding: 14,
                    borderRadius: 14,
                    border: `1px solid ${colors.border}`,
                    background: mode === "dark" ? "rgba(0,0,0,0.2)" : "white",
                    color: colors.text1,
                    outline: "none",
                    fontSize: "0.95rem",
                    boxSizing: "border-box",
                    transition: "border-color 0.2s ease"
                  }}
                  onFocus={(e) => e.target.style.borderColor = colors.primary}
                  onBlur={(e) => e.target.style.borderColor = colors.border}
                />
              </div>

              {/* Question 4: Scheduling Satisfaction */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, borderBottom: `1px solid ${colors.border}22`, paddingBottom: 16 }}>
                <label style={{ fontSize: "0.95rem", fontWeight: "600", color: colors.text1 }}>
                  4. How satisfied are you with the Social Media Content Scheduling feature? (Letters and spaces only)
                </label>
                <input
                  type="text"
                  value={formData.scheduling}
                  onChange={(e) => handleTextChange("scheduling", e.target.value)}
                  placeholder="e.g. The scheduler makes social media managing very easy"
                  required
                  style={{
                    width: "100%",
                    padding: 14,
                    borderRadius: 14,
                    border: `1px solid ${colors.border}`,
                    background: mode === "dark" ? "rgba(0,0,0,0.2)" : "white",
                    color: colors.text1,
                    outline: "none",
                    fontSize: "0.95rem",
                    boxSizing: "border-box",
                    transition: "border-color 0.2s ease"
                  }}
                  onFocus={(e) => e.target.style.borderColor = colors.primary}
                  onBlur={(e) => e.target.style.borderColor = colors.border}
                />
              </div>

              {/* Question 5: Comments */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <label style={{ fontSize: "0.95rem", fontWeight: "600", color: colors.text1 }}>
                  5. Comments & suggestions (Letters and spaces only)
                </label>
                <textarea
                  value={formData.comments}
                  onChange={handleCommentsChange}
                  placeholder="Type your feedback here..."
                  rows={4}
                  required
                  style={{
                    width: "100%",
                    padding: 16,
                    borderRadius: 14,
                    border: `1px solid ${colors.border}`,
                    background: mode === "dark" ? "rgba(0,0,0,0.2)" : "white",
                    color: colors.text1,
                    outline: "none",
                    fontSize: "0.95rem",
                    resize: "vertical",
                    boxSizing: "border-box",
                    transition: "border-color 0.2s ease"
                  }}
                  onFocus={(e) => e.target.style.borderColor = colors.primary}
                  onBlur={(e) => e.target.style.borderColor = colors.border}
                />
                <span style={{ fontSize: "0.8rem", color: colors.text2 }}>
                  * Numbers and special characters are blocked from being entered in all fields.
                </span>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                style={{
                  padding: "14px 28px",
                  background: colors.primary,
                  color: mode === "dark" ? "#0A0E27" : "#fff",
                  borderRadius: 14,
                  border: "none",
                  fontWeight: 700,
                  fontSize: "1rem",
                  cursor: isSubmitting ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 10,
                  transition: "all 0.3s ease",
                  boxShadow: `0 8px 20px ${colors.primary}22`
                }}
                onMouseEnter={(e) => {
                  if (!isSubmitting) {
                    e.currentTarget.style.transform = "translateY(-2px)";
                    e.currentTarget.style.boxShadow = `0 12px 24px ${colors.primary}44`;
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSubmitting) {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow = `0 8px 20px ${colors.primary}22`;
                  }
                }}
              >
                {isSubmitting ? "Submitting..." : <>Submit Feedback <Send size={16} /></>}
              </button>

            </form>
          </div>

          {/* Sentiment Charts Card (Rendered only after successful submission) */}
          {feedbackResponse && feedbackResponse.type === "success" && (
            <div style={{
              background: colors.bg2,
              border: `1px solid ${colors.border}`,
              borderRadius: 24,
              padding: 32,
              boxShadow: mode === "dark" ? "none" : "0 10px 30px rgba(0,0,0,0.03)",
              display: "flex",
              flexDirection: "column"
            }}>
              <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginTop: 0, marginBottom: 8, color: colors.text1, fontFamily: "'Outfit', sans-serif" }}>
                Sentiment Analysis Distribution
              </h2>
              <p style={{ color: colors.text2, fontSize: "0.95rem", marginTop: 0, marginBottom: 28 }}>
                Sentiment analysis predictions derived from user comment entries.
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: 40, alignItems: "center", justifyContent: "center", flex: 1 }}>
                
                {/* Charts Flexbox */}
                <div style={{ display: "flex", flexWrap: "wrap", width: "100%", justifyContent: "space-around", alignItems: "center", gap: 24 }}>
                  
                  {/* Donut / Pie Chart */}
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
                    <div style={{ position: "relative", width: 180, height: 180 }}>
                      <svg width="100%" height="100%" viewBox="0 0 160 160">
                        {donutSegments.map((seg, i) => {
                          const strokeDash = seg.pct * donutCircumference;
                          return (
                            <circle
                              key={i}
                              cx="80"
                              cy="80"
                              r={donutRadius}
                              fill="transparent"
                              stroke={seg.color}
                              strokeWidth="14"
                              strokeDasharray={`${strokeDash} ${donutCircumference}`}
                              strokeDashoffset={seg.offset}
                              strokeLinecap={seg.pct > 0.02 ? "round" : "butt"}
                              style={{
                                transform: "rotate(-90deg)",
                                transformOrigin: "80px 80px",
                                transition: "all 0.6s cubic-bezier(0.16, 1, 0.3, 1)"
                              }}
                            />
                          );
                        })}
                        <circle cx="80" cy="80" r={donutRadius - 10} fill={mode === "dark" ? "#0F1330" : "#fff"} />
                        <text x="80" y="76" textAnchor="middle" fill={colors.text2} fontSize="10" fontWeight="600" letterSpacing="0.05em">TOTAL</text>
                        <text x="80" y="96" textAnchor="middle" fill={colors.text1} fontSize="20" fontWeight="800">{totalSentiment}</text>
                      </svg>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8, width: "100%" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.85rem" }}>
                        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#10B981" }} />
                        <span style={{ fontWeight: 600, color: colors.text1 }}>Positive:</span>
                        <span style={{ color: colors.text2 }}>{sentimentStats.positive} ({getPercentage(sentimentStats.positive, totalSentiment)}%)</span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.85rem" }}>
                        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#F59E0B" }} />
                        <span style={{ fontWeight: 600, color: colors.text1 }}>Neutral:</span>
                        <span style={{ color: colors.text2 }}>{sentimentStats.neutral} ({getPercentage(sentimentStats.neutral, totalSentiment)}%)</span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.85rem" }}>
                        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#EF4444" }} />
                        <span style={{ fontWeight: 600, color: colors.text1 }}>Negative:</span>
                        <span style={{ color: colors.text2 }}>{sentimentStats.negative} ({getPercentage(sentimentStats.negative, totalSentiment)}%)</span>
                      </div>
                    </div>
                  </div>

                  {/* Vertical Bar Chart */}
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
                    <div style={{ width: 260, height: 200 }}>
                      <svg width="100%" height="100%" viewBox="0 0 260 200">
                        <line x1="40" y1="20" x2="240" y2="20" stroke={colors.border} strokeWidth="1" strokeDasharray="3 3" opacity="0.3" />
                        <line x1="40" y1="90" x2="240" y2="90" stroke={colors.border} strokeWidth="1" strokeDasharray="3 3" opacity="0.3" />
                        <line x1="40" y1="160" x2="240" y2="160" stroke={colors.border} strokeWidth="1.5" opacity="0.5" />

                        <text x="32" y="24" textAnchor="end" fill={colors.text2} fontSize="9" fontWeight="600">100%</text>
                        <text x="32" y="94" textAnchor="end" fill={colors.text2} fontSize="9" fontWeight="600">50%</text>
                        <text x="32" y="164" textAnchor="end" fill={colors.text2} fontSize="9" fontWeight="600">0%</text>

                        {[
                          { val: posPct, x: 60, color: "#10B981", count: sentimentStats.positive, label: "Pos" },
                          { val: neuPct, x: 120, color: "#F59E0B", count: sentimentStats.neutral, label: "Neu" },
                          { val: negPct, x: 180, color: "#EF4444", count: sentimentStats.negative, label: "Neg" }
                        ].map((bar, idx) => {
                          const h = getBarHeight(bar.val);
                          const y = baseLineY - h;
                          return (
                            <g key={idx}>
                              <rect x={bar.x} y="20" width="28" height={barChartHeight} fill={`${bar.color}05`} rx="4" />
                              <path
                                d={drawBarPath(bar.x, y, 28, baseLineY)}
                                fill={bar.color}
                                style={{
                                  transition: "all 0.6s cubic-bezier(0.16, 1, 0.3, 1)"
                                }}
                              />
                              <text x={bar.x + 14} y={y - 8} textAnchor="middle" fill={colors.text1} fontSize="10" fontWeight="700">
                                {Math.round(bar.val * 100)}%
                              </text>
                              <text x={bar.x + 14} y="180" textAnchor="middle" fill={colors.text2} fontSize="10" fontWeight="600">
                                {bar.label}
                              </text>
                            </g>
                          );
                        })}
                      </svg>
                    </div>
                  </div>

                </div>

              </div>
            </div>
          )}
        </div>

      </div>

      <Footer />
    </div>
  );
};

export default Analytics;
