from typing import List, Optional, Tuple

from models import NarrativeEvent, NarrativeOption, HabitatState


class NarrativeManager:
    def __init__(
        self,
        event_repository=None,
        option_repository=None
    ):
        self.event_repository = event_repository
        self.option_repository = option_repository

    def get_event_with_options(
        self,
        event_id: int
    ) -> Tuple[Optional[NarrativeEvent], List[NarrativeOption]]:
        if self.event_repository is None or self.option_repository is None:
            return None, []

        event = self.event_repository.get(event_id)

        if event is None:
            return None, []

        options = self.option_repository.get_by_event(event_id)
        return event, options

    def format_event(
        self,
        event: NarrativeEvent,
        options: List[NarrativeOption]
    ) -> str:
        text = f"{event.description}\n"

        if options:
            text += "\nOptions:\n"

            for index, option in enumerate(options, start=1):
                text += f"{index}. {option.description}\n"

        return text.rstrip()

    def validate_option_choice(
        self,
        choice: str,
        options: List[NarrativeOption]
    ) -> Optional[NarrativeOption]:
        if not choice.isdigit():
            return None

        selected_index = int(choice) - 1

        if selected_index < 0 or selected_index >= len(options):
            return None

        return options[selected_index]

    def apply_option(
        self,
        option: NarrativeOption,
        habitat_state: HabitatState
    ) -> HabitatState:
        habitat_state.energy = self._apply_change(
            habitat_state.energy,
            option.energy_impact
        )

        habitat_state.oxygen = self._apply_change(
            habitat_state.oxygen,
            option.oxygen_impact
        )

        habitat_state.integrity = self._apply_change(
            habitat_state.integrity,
            option.integrity_impact
        )

        habitat_state.crew_health = self._apply_change(
            habitat_state.crew_health,
            option.crew_health_impact
        )

        return habitat_state

    def _apply_change(self, current_value: int, change: int) -> int:
        # habitat values stay between 0 and 100
        new_value = current_value + change
        return max(0, min(100, new_value))