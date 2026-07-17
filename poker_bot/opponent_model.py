class OpponentModel:
    MIN_SAMPLE = 10

    def __init__(self, player_id):
        self.player_id = player_id
        self._vpip_opportunities = 0
        self._vpip_actions = 0
        self._faced_raise = 0
        self._folded_to_raise = 0
        self._action_opportunities = 0
        self._raise_actions = 0

    def record_preflop_action(self, action):
        self._vpip_opportunities += 1
        if action in ("call", "raise"):
            self._vpip_actions += 1

    def record_response_to_raise(self, folded):
        self._faced_raise += 1
        if folded:
            self._folded_to_raise += 1

    def record_action(self, action):
        self._action_opportunities += 1
        if action == "raise":
            self._raise_actions += 1

    @property
    def vpip(self):
        if self._vpip_opportunities < self.MIN_SAMPLE:
            return None
        return self._vpip_actions / self._vpip_opportunities

    @property
    def fold_to_raise(self):
        if self._faced_raise < self.MIN_SAMPLE:
            return None
        return self._folded_to_raise / self._faced_raise

    @property
    def raise_freq(self):
        if self._action_opportunities < self.MIN_SAMPLE:
            return None
        return self._raise_actions / self._action_opportunities

    def action_adjustment(self):
        adjustment = 0

        ftr = self.fold_to_raise
        if ftr is not None:
            if ftr > 0.60:
                adjustment += 1
            elif ftr < 0.25:
                adjustment -= 1

        vp = self.vpip
        if vp is not None:
            if vp < 0.20:
                adjustment -= 1

        return adjustment

    def __repr__(self):
        return (
            f"OpponentModel({self.player_id}: "
            f"VPIP={self.vpip}, FTR={self.fold_to_raise}, "
            f"RaiseFreq={self.raise_freq})"
        )


class OpponentModelRegistry:
    def __init__(self):
        self._models = {}

    def get(self, player_id):
        if player_id not in self._models:
            self._models[player_id] = OpponentModel(player_id)
        return self._models[player_id]

    def all_players(self):
        return list(self._models.keys())

    def reset(self):
        self._models = {}
