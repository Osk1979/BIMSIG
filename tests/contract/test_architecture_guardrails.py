from scripts.validate_architecture import validate


def test_permanent_architecture_guardrails_are_satisfied() -> None:
    assert validate() == []
