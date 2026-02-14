from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class GoalEvent(BaseModel):
    """A single goal-like event in the timeline (including own goals, penalties, disallowed goals)."""

    model_config = ConfigDict(extra="forbid")

    minute: Optional[str] = Field(
        None,
        description='Minute string as shown on the page, e.g. "12", "45+2", "90+5".',
    )
    team: Optional[Literal["home", "away"]] = Field(
        None, description="Which team the event belongs to."
    )
    scorer: Optional[str] = Field(None, description="Scorer name if available.")
    assist: Optional[str] = Field(None, description="Assist name if available.")
    kind: Optional[
        Literal[
            "goal",
            "penalty_goal",
            "own_goal",
            "disallowed_goal",
        ]
    ] = Field(None, description="Type of goal event.")
    counted: Optional[bool] = Field(
        None, description="Whether this goal counted in the official score."
    )
    note: Optional[str] = Field(
        None,
        description='Extra detail, e.g. "VAR offside", "handball", "after extra time".',
    )


class CardEvent(BaseModel):
    """A single card event (yellow/red/second yellow) with time and team."""

    model_config = ConfigDict(extra="forbid")

    minute: Optional[str] = Field(
        None,
        description='Minute string as shown on the page, e.g. "33", "90+1".',
    )
    team: Optional[Literal["home", "away"]] = Field(
        None, description="Which team the card belongs to."
    )
    player: Optional[str] = Field(None, description="Player name if available.")
    card: Optional[Literal["yellow", "red", "second_yellow"]] = Field(
        None, description="Card type."
    )
    note: Optional[str] = Field(None, description='Reason if available, e.g. "foul".')


class PenaltyShootoutKick(BaseModel):
    """One kick in a penalty shootout series."""

    model_config = ConfigDict(extra="forbid")

    order: Optional[int] = Field(None, description="Kick order in the shootout (1..N).")
    team: Optional[Literal["home", "away"]] = Field(
        None, description="Which team took the kick."
    )
    taker: Optional[str] = Field(
        None,
        alias="player",
        description="Penalty taker name if available.",
    )
    outcome: Optional[Literal["scored", "missed", "saved", "post", "unknown"]] = Field(
        None,
        alias="result",
        description="Outcome of the kick.",
    )
    note: Optional[str] = Field(None, description="Extra detail if available.")


class MatchReport(BaseModel):
    """
    Structured result returned by the AI tool call.
    Extended to include timeline details: goals, cards, substitutions, penalties, etc.
    """

    model_config = ConfigDict(extra="forbid")

    # --- Validity ---
    is_valid: bool = Field(
        ...,
        description="Whether the provided text is a football match statistics page.",
    )

    # --- Basic match info ---
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    final_score: Optional[str] = Field(
        None, description='Final score in format like "2-1".'
    )

    # If match went to extra time
    went_to_extra_time: Optional[bool] = Field(
        None, description="True if match included extra time."
    )
    score_after_90: Optional[str] = Field(
        None,
        description='Score after regular time (90 minutes), e.g. "1-1".',
    )
    score_after_extra_time: Optional[str] = Field(
        None,
        description='Score after extra time (120 minutes), e.g. "2-2".',
    )

    # --- Possession / shots (existing) ---
    possession_home: Optional[str] = Field(
        None, description='Possession for home team, e.g. "54%".'
    )
    possession_away: Optional[str] = Field(
        None, description='Possession for away team, e.g. "46%".'
    )
    shots_home: Optional[int] = None
    shots_away: Optional[int] = None

    # --- Cards totals (existing) ---
    yellow_cards_home: Optional[int] = None
    yellow_cards_away: Optional[int] = None
    red_cards_home: Optional[int] = Field(None, description="Total red cards (home).")
    red_cards_away: Optional[int] = Field(None, description="Total red cards (away).")

    # --- Detailed timelines ---
    goals: List[GoalEvent] = Field(
        default_factory=list,
        description="Timeline of goal-related events, including disallowed goals.",
    )
    cards: List[CardEvent] = Field(
        default_factory=list,
        description="Timeline of yellow/red card events with minute and team.",
    )

    # --- Substitutions / changes ---
    substitutions_home: Optional[int] = Field(
        None, description="Number of substitutions (home team)."
    )
    substitutions_away: Optional[int] = Field(
        None, description="Number of substitutions (away team)."
    )

    # --- Penalties (in match play) ---
    penalties_awarded_home: Optional[int] = Field(
        None, description="Penalties awarded to home team in match play."
    )
    penalties_awarded_away: Optional[int] = Field(
        None, description="Penalties awarded to away team in match play."
    )
    penalties_scored_home: Optional[int] = Field(
        None, description="Penalties scored by home team in match play."
    )
    penalties_scored_away: Optional[int] = Field(
        None, description="Penalties scored by away team in match play."
    )
    penalties_missed_home: Optional[int] = Field(
        None, description="Penalties missed by home team in match play."
    )
    penalties_missed_away: Optional[int] = Field(
        None, description="Penalties missed by away team in match play."
    )

    # --- Penalty shootout series (if applicable) ---
    has_penalty_shootout: Optional[bool] = Field(
        None, description="True if the match decided by a penalty shootout."
    )
    penalty_shootout_score: Optional[str] = Field(
        None,
        description='Shootout score in format like "4-3" (home-away).',
    )
    penalty_shootout_kicks: List[PenaltyShootoutKick] = Field(
        default_factory=list,
        description="Ordered list of shootout kicks (if available).",
    )

    # --- Extra details / anomalies ---
    disallowed_goals_count: Optional[int] = Field(
        None, description="Total number of disallowed goals (both teams)."
    )
    disallowed_goals: List[GoalEvent] = Field(
        default_factory=list,
        description="Optional separate list of disallowed goals (can overlap with goals list if you prefer).",
    )
    notes: Optional[str] = Field(
        None,
        description="Any additional important details not captured elsewhere (e.g. VAR incidents, abandoned match).",
    )

    # --- Final generated narrative ---
    report: str = Field(..., description="Professional ~300-word match report.")
