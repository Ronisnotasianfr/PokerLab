"""
opponent_model.py — Per-opponent stat tracking for Program 6.

Tracks:
  - VPIP: Voluntarily Put Money In Pot % (loose/tight indicator)
  - Fold-to-raise %: how often they fold when raised (bluffability)
  - Raise frequency: aggression level

Stats are accumulated across hands. Until a minimum sample size is reached,
the model returns neutral adjustments (0 steps) so we fall back to baseline.
"""


class OpponentModel:
    """Tracks behavioral stats for a single opponent."""

    MIN_SAMPLE = 10  # minimum hands before trusting stats

    def __init__(self, player_id):
        self.player_id = player_id

        # VPIP tracking
        self._vpip_opportunities = 0
        self._vpip_actions = 0  # times they voluntarily put $ in

        # Fold-to-raise tracking
        self._faced_raise = 0
        self._folded_to_raise = 0

        # Raise frequency tracking
        self._action_opportunities = 0
        self._raise_actions = 0

    # ------------------------------------------------------------------ #
    # Recording methods (call these as actions are observed)
    # ------------------------------------------------------------------ #

    def record_preflop_action(self, action):
        """Record a preflop action to update VPIP.

        Args:
            action: 'fold', 'call', 'raise', or 'check'
        """
        self._vpip_opportunities += 1
        if action in ("call", "raise"):
            self._vpip_actions += 1

    def record_response_to_raise(self, folded):
        """Record whether the opponent folded when we raised.

        Args:
            folded: True if they folded, False otherwise
        """
        self._faced_raise += 1
        if folded:
            self._folded_to_raise += 1

    def record_action(self, action):
        """Record any in-hand action for raise-frequency tracking.

        Args:
            action: 'fold', 'call', 'raise', or 'check'
        """
        self._action_opportunities += 1
        if action == "raise":
            self._raise_actions += 1

    # ------------------------------------------------------------------ #
    # Stat accessors
    # ------------------------------------------------------------------ #

    @property
    def vpip(self):
        """Voluntarily Put In Pot %. None if insufficient data."""
        if self._vpip_opportunities < self.MIN_SAMPLE:
            return None
        return self._vpip_actions / self._vpip_opportunities

    @property
    def fold_to_raise(self):
        """Fold-to-raise %. None if insufficient data."""
        if self._faced_raise < self.MIN_SAMPLE:
            return None
        return self._folded_to_raise / self._faced_raise

    @property
    def raise_freq(self):
        """Raise frequency %. None if insufficient data."""
        if self._action_opportunities < self.MIN_SAMPLE:
            return None
        return self._raise_actions / self._action_opportunities

    # ------------------------------------------------------------------ #
    # Adjustment logic
    # ------------------------------------------------------------------ #

    def action_adjustment(self):
        """Return an integer step adjustment to apply to the baseline action.

        Positive = more aggressive, negative = more conservative.
        Returns 0 if insufficient data for any stat.
        """
        adjustment = 0

        ftr = self.fold_to_raise
        if ftr is not None:
            if ftr > 0.60:
                # Very bluffable: raise more aggressively
                adjustment += 1
            elif ftr < 0.25:
                # Calling station: only bet for value, dial back bluffs
                adjustment -= 1

        vp = self.vpip
        if vp is not None:
            if vp > 0.70:
                # Loose player: they call wide, so bet thinner for value
                adjustment += 0
            elif vp < 0.20:
                # Very tight: be more cautious — their calls mean strength
                adjustment -= 1

        return adjustment

    def __repr__(self):
        return (
            f"OpponentModel({self.player_id}: "
            f"VPIP={self.vpip}, FTR={self.fold_to_raise}, "
            f"RaiseFreq={self.raise_freq})"
        )


class OpponentModelRegistry:
    """Manages OpponentModel instances for all opponents in a session."""

    def __init__(self):
        self._models = {}

    def get(self, player_id):
        """Get or create an OpponentModel for a given player."""
        if player_id not in self._models:
            self._models[player_id] = OpponentModel(player_id)
        return self._models[player_id]

    def all_players(self):
        return list(self._models.keys())

    def reset(self):
        """Clear all opponent models (e.g. new match)."""
        self._models = {}
