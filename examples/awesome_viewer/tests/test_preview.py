from __future__ import annotations

from typing import Iterator

import pytest

from examples.awesome_viewer.viewer import Category, Entry, print_category_preview


def _sample_categories() -> list[Category]:
    return [
        Category(
            title="Category One",
            items=(
                Entry(name="Alpha", url="https://example.com/alpha", description="Alpha lib"),
                Entry(name="Beta", url="https://example.com/beta", description="Beta lib"),
                Entry(name="Gamma", url="https://example.com/gamma", description="Gamma lib"),
                Entry(name="Delta", url="https://example.com/delta", description="Delta lib"),
            ),
        ),
        Category(
            title="Category Two",
            items=(
                Entry(name="Echo", url="https://example.com/echo", description="Echo lib"),
            ),
        ),
        Category(
            title="Category Three",
            items=(
                Entry(name="Foxtrot", url="https://example.com/foxtrot", description="Foxtrot lib"),
            ),
        ),
    ]


def test_print_category_preview_step_mode_respects_quit(capsys: pytest.CaptureFixture[str]) -> None:
    categories = _sample_categories()
    responses: Iterator[str] = iter(["q"])

    def fake_input(prompt: str) -> str:
        # Mirror ``input`` by writing the prompt so it is captured.
        print(prompt, end="")
        return next(responses)

    print_category_preview(
        categories,
        limit=3,
        mode="step",
        interactive=True,
        input_func=fake_input,
    )

    output = capsys.readouterr().out
    assert "[1/3] Category One" in output
    assert "[2/3] Category Two" not in output


def test_print_category_preview_step_mode_handles_eof(capsys: pytest.CaptureFixture[str]) -> None:
    categories = _sample_categories()

    def raising_input(prompt: str) -> str:
        print(prompt, end="")
        raise EOFError

    print_category_preview(
        categories,
        limit=3,
        mode="step",
        interactive=True,
        input_func=raising_input,
    )

    output = capsys.readouterr().out
    assert "[1/3] Category One" in output
    assert "[2/3] Category Two" not in output


def test_print_category_preview_non_interactive_falls_back(capsys: pytest.CaptureFixture[str]) -> None:
    categories = _sample_categories()

    print_category_preview(
        categories,
        limit=2,
        mode="step",
        interactive=False,
    )

    output = capsys.readouterr().out
    assert "Press Enter for next category" not in output
    assert "[1/3] Category One" in output
    assert "[2/3] Category Two" in output
