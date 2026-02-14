"""
ScoreFlash — Streamlit app for generating a football match report from a Livesport URL.
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from agent import MatchReportAgent
from cleaner import build_stats_url, clean_html_to_text, normalize_match_url
from config.parameters import API_ENV_VAR
from schemas import MatchReport
from scraper import fetch_html
from storage import save_match_report

load_dotenv()


def apply_scoreflash_theme() -> None:
    """Apply ScoreFlash light theme."""
    st.markdown(
        """
        <style>
          /* Hide Streamlit default header + chrome */
          header[data-testid="stHeader"] { display: none; }
          #MainMenu { visibility: hidden; }
          footer { visibility: hidden; }

          /* App background */
          .stApp {
            background-color: #ededed;
            color: #001e29;
          }

          /* Page container */
          .block-container {
            padding-top: 0.8rem;
            max-width: 860px;
          }

          /* Typography */
          h1, h2, h3, h4 { color: #001e29; font-weight: 900; }
          .scoreflash-muted { color: rgba(0,30,41,0.65); font-size: 0.95rem; }

          /* Custom header bar */
          .scoreflash-header-bar {
            background-color: #001e29;
            color: #ffffff;
            padding: 14px 22px;
            margin: -0.8rem -0.8rem 1rem -0.8rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
            border-radius: 0 0 14px 14px;
          }

          .scoreflash-header-left {
            display: flex;
            flex-direction: column;
            gap: 2px;
          }

          .scoreflash-header-title {
            font-size: 1.35rem;
            font-weight: 900;
            letter-spacing: 0.4px;
            line-height: 1.05;
          }

          .scoreflash-header-accent { color: #fe0146; }

          .scoreflash-header-subtitle {
            color: rgba(255,255,255,0.78);
            font-size: 0.9rem;
            font-weight: 600;
          }

          /* Inputs */
          .stTextInput input,
          .stSelectbox div[data-baseweb="select"] {
            background: #ffffff !important;
            color: #001e29 !important;
            border: 1px solid rgba(0, 30, 41, 0.18) !important;
            border-radius: 12px !important;
          }

          /* Buttons */
          .stButton button {
            background-color: #fe0146 !important;
            color: #ffffff !important;
            border: 0 !important;
            border-radius: 12px !important;
            padding: 0.58rem 1.1rem !important;
            font-weight: 800 !important;
          }
          .stButton button:hover { background-color: #e6003f !important; }

          /* Card */
          .scoreflash-card {
            background: #ffffff;
            border: 1px solid rgba(0, 30, 41, 0.10);
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
          }

          /* Card header */
          .scoreflash-card-header {
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap: 12px;
            margin-bottom: 8px;
          }
          .scoreflash-card-title {
            font-size: 1.05rem;
            font-weight: 900;
            color: #001e29;
          }
          .scoreflash-badge {
            background: rgba(254, 1, 70, 0.10);
            border: 1px solid rgba(254, 1, 70, 0.40);
            color: #fe0146;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 800;
            white-space: nowrap;
          }

          /* Scoreboard */
          .scoreboard {
            display:grid;
            grid-template-columns: 1fr auto 1fr;
            align-items:center;
            gap: 12px;
            margin-top: 6px;
            margin-bottom: 12px;
          }
          .team {
            font-weight: 900;
            font-size: 1.05rem;
            color: #001e29;
          }
          .team.home { text-align:left; }
          .team.away { text-align:right; }

          .score {
            font-size: 2.1rem;
            font-weight: 900;
            color: #001e29;
            padding: 2px 12px;
            border-radius: 12px;
            background: rgba(0,30,41,0.05);
            border: 1px solid rgba(0,30,41,0.10);
          }

          /* Stats grid */
          .stats-grid {
            display:grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
          }
          .stat {
            background: rgba(0,30,41,0.03);
            border: 1px solid rgba(0,30,41,0.08);
            border-radius: 12px;
            padding: 10px;
          }
          .stat-label {
            font-size: 0.82rem;
            color: rgba(0,30,41,0.62);
            font-weight: 700;
          }
          .stat-value {
            font-size: 1.05rem;
            font-weight: 900;
            color: #001e29;
            margin-top: 2px;
          }

          /* Divider */
          hr { border-color: rgba(0,30,41,0.14); }

          /* Small spacing helper */
          .spacer-10 { height: 10px; }
          .spacer-14 { height: 14px; }

          /* Mobile: stack stats grid */
          @media (max-width: 680px) {
            .stats-grid { grid-template-columns: 1fr; }
            .scoreflash-header-bar { border-radius: 0 0 12px 12px; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render a custom header bar."""
    st.markdown(
        """
        <div class="scoreflash-header-bar">
          <div class="scoreflash-header-left">
            <div class="scoreflash-header-title">
              Score<span class="scoreflash-header-accent">Flash</span>
            </div>
            <div class="scoreflash-header-subtitle">
              Livesport / FlashScore match report generator
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_agent() -> MatchReportAgent:
    """Create and cache the OpenAI agent (resource-level cache)."""
    api_key = os.environ.get(API_ENV_VAR)
    if not api_key:
        raise RuntimeError(f"Missing {API_ENV_VAR} environment variable.")
    return MatchReportAgent(api_key=api_key)


def render_report(result: MatchReport) -> None:
    """Render match stats + report in ScoreFlash style."""
    if not result.is_valid:
        st.error(
            "This page does not look like a football match statistics page (or stats could not be extracted)."
        )
        return

    def s(v: object) -> str:
        return "-" if v is None or v == "" else str(v)

    home = result.home_team or "Home"
    away = result.away_team or "Away"
    score = s(result.final_score)

    badge_text = "Stats extracted"
    if getattr(result, "has_penalty_shootout", False):
        badge_text = f"PEN {s(getattr(result, 'penalty_shootout_score', None))}"
    elif getattr(result, "went_to_extra_time", False):
        badge_text = "AET"

    st.markdown(
        f"""
        <div class="scoreflash-card">
          <div class="scoreflash-card-header">
            <div class="scoreflash-card-title">Match overview</div>
            <div class="scoreflash-badge">{badge_text}</div>
          </div>

          <div class="scoreboard">
            <div class="team home">{home}</div>
            <div class="score">{score}</div>
            <div class="team away">{away}</div>
          </div>

          <div class="stats-grid">
            <div class="stat">
              <div class="stat-label">Possession</div>
              <div class="stat-value">{s(result.possession_home)} — {s(result.possession_away)}</div>
            </div>
            <div class="stat">
              <div class="stat-label">Shots</div>
              <div class="stat-value">{s(result.shots_home)} — {s(result.shots_away)}</div>
            </div>
            <div class="stat">
              <div class="stat-label">Yellow cards</div>
              <div class="stat-value">{s(result.yellow_cards_home)} — {s(result.yellow_cards_away)}</div>
            </div>
            <div class="stat">
              <div class="stat-label">Red cards</div>
              <div class="stat-value">{s(getattr(result, "red_cards_home", None))} — {s(getattr(result, "red_cards_away", None))}</div>
            </div>
            <div class="stat">
              <div class="stat-label">Substitutions</div>
              <div class="stat-value">{s(getattr(result, "substitutions_home", None))} — {s(getattr(result, "substitutions_away", None))}</div>
            </div>
            <div class="stat">
              <div class="stat-label">Extra time</div>
              <div class="stat-value">{"Yes" if getattr(result, "went_to_extra_time", False) else "No"}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='spacer-14'></div>", unsafe_allow_html=True)

    st.markdown("### Match report")
    st.write(result.report)


def main() -> None:
    st.set_page_config(page_title="ScoreFlash", layout="centered")
    apply_scoreflash_theme()
    render_header()

    # ---- Controls card ----
    st.markdown("<div class='scoreflash-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='scoreflash-card-header'><div class='scoreflash-card-title'>Generate report</div></div>",
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([1, 2], vertical_alignment="bottom")
    with col_a:
        language = st.selectbox(
            "Report language", options=["English", "Czech"], index=0
        )
        language_code = "en" if language == "English" else "cs"

    with col_b:
        url = st.text_input(
            "Match URL",
            placeholder="https://www.livesport.cz/zapas/fotbal/...",
        )

    generate = st.button("Generate report")
    st.markdown("</div>", unsafe_allow_html=True)  # close card

    if not generate:
        return

    if not url.strip():
        st.error("Please enter a URL.")
        return

    try:
        agent = get_agent()
    except Exception as exc:
        st.error(f"Agent initialization error: {exc}")
        return

    try:
        with st.spinner("Fetching pages..."):
            match_url = normalize_match_url(url)
            stats_url = build_stats_url(url)

            match_html = fetch_html(match_url)
            stats_html = fetch_html(stats_url)

        with st.spinner("Cleaning HTML..."):
            match_text = clean_html_to_text(match_html)
            stats_text = clean_html_to_text(stats_html)
            combined_text = (
                f"SOURCE: MATCH PAGE\n{match_text}\n\nSOURCE: STATS PAGE\n{stats_text}"
            )

        with st.spinner("Generating report with AI..."):
            result = agent.analyze(combined_text, language=language_code)

        saved_path = save_match_report(result, source_url=url)
        st.caption(f"Saved: {saved_path}")

        render_report(result)

    except Exception as exc:
        st.error(f"Something went wrong: {exc}")


if __name__ == "__main__":
    main()
