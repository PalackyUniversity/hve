from enum import IntEnum, auto


class Vaccine(IntEnum):
    """
    Dose index number.
    """

    DOSE1 = 0  # required
    DOSE2 = auto()
    DOSE3 = auto()


class StateMeta(type):
    def __len__(self):
        return len(Vaccine) * 2 + 1

    def __iter__(self):
        self.value = State.UNVACCINATED
        yield self

        for vaccine in Vaccine:
            for higher in [True, False]:
                self.value = State.to_code(vaccine, higher)
                yield self

    @staticmethod
    def to_code(vaccine: Vaccine, higher: bool):
        """
        Convert dose and higher to state.
        """
        return (vaccine.value + 1) * 10 + higher

    @property
    def label(self):
        if self.value == State.UNVACCINATED:
            return "Unvaccinated"
        else:
            return f"{'<' if self.value % 10 == 0 else '>'} {{0}} weeks from dose {self.value // 10}"


class State(metaclass=StateMeta):
    """
    State of a person.
    - The first digit is the dose number
    - The second digit is the time since the dose (lower/higher than threshold).
    """

    UNVACCINATED = 0
