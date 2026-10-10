from playwright.sync_api import expect
from balanced_books.case_data import (
    TRANSACTIONS,
    RECORDABLE_TRANSACTIONS,
    EVENT_TYPE_OPTIONS,
)
from balanced_books.progress import STATEMENT_EXPECTED


def lesson(page, click, choose, select, idle, check, results, readonly):
    begin = (
        page.locator("[data-testid=stMain]").get_by_role("button").all_text_contents()
    )
    click(next(x for x in begin if x not in ["Back", "Forward", "Start over"]))
    choose(EVENT_TYPE_OPTIONS[0])
    baseline = idle()
    click("Back")
    readonly()
    assert idle() == baseline
    click("Forward")
    page.reload()
    idle()
    expect(
        page.get_by_role("radio", name=EVENT_TYPE_OPTIONS[0], exact=True)
    ).to_be_checked()
    for i, item in enumerate(TRANSACTIONS):
        choose(
            next(x for x in EVENT_TYPE_OPTIONS if x != item.event_type)
            if i == 0
            else item.event_type
        )
        click("Check this event")
        expect(page.get_by_role("button", name="Forward", exact=True)).to_be_disabled()
        click(
            "Continue to the Equation Lab"
            if i == len(TRANSACTIONS) - 1
            else "Next event"
        )
    for i, item in enumerate(RECORDABLE_TRANSACTIONS):
        choose(
            next(x for x in item.choices if x != item.correct_choice)
            if i == 0
            else item.correct_choice
        )
        click("Check the dual effect")
        expect(page.get_by_role("button", name="Forward", exact=True)).to_be_disabled()
        click(
            "Build the financial statements"
            if i == len(RECORDABLE_TRANSACTIONS) - 1
            else "Next transaction"
        )
    check(
        "Complete inbox and equation rounds with preserved draft, wrong-answer feedback and original scoring"
    )

    def workspace_frame():
        deadline = __import__("time").monotonic() + 30
        while __import__("time").monotonic() < deadline:
            for candidate in page.frames:
                try:
                    if (
                        candidate.locator("#root .workspace").count()
                        or candidate.locator("#finalize-statement").count()
                    ):
                        return candidate
                except Exception:
                    continue
            page.wait_for_timeout(100)
        raise AssertionError("Statement workspace frame did not initialize")

    frame = workspace_frame()
    expect(frame.locator("#finalize-statement")).to_be_visible()
    frame.locator("#finalize-statement").click()
    page.wait_for_timeout(150)
    idle()
    assert idle()["bbc_statement_progress"]["attempts"][0] == 1
    expect(frame.locator('[data-statement-index="1"]')).to_be_disabled()
    for stage, placements in enumerate(STATEMENT_EXPECTED):
        for tile_index, (tile, zone) in enumerate(placements.items()):
            tile_button = frame.locator('[data-tile-id="' + tile + '"]')
            place_button = frame.locator('[data-place-zone="' + zone + '"]')
            if stage == 0 and tile_index == 0:
                tile_button.focus()
                tile_button.press("Enter")
                place_button.focus()
                place_button.press("Enter")
            else:
                tile_button.click()
                place_button.click()
            page.wait_for_timeout(100)
            if stage == 0 and tile_index == 0:
                baseline = idle()
                order = baseline["bbc_statement_progress"]["shuffledAccountIds"]
                click("Back")
                readonly()
                assert idle() == baseline
                click("Forward")
                page.reload()
                idle()
                frame = workspace_frame()
                assert (
                    idle()["bbc_statement_progress"]["placements"]
                    == baseline["bbc_statement_progress"]["placements"]
                )
                assert idle()["bbc_statement_progress"]["shuffledAccountIds"] == order
                check(
                    "Statement draft, tile order and keyboard placement survive outer review and refresh"
                )
        frame.locator("#finalize-statement").click()
        page.wait_for_timeout(150)
        idle()
        if stage < 2:
            frame.locator("#continue-forward").click()
            page.wait_for_timeout(150)
            idle()
            if stage == 0:
                token = page.url.split("progress=")[1].split("&")[0]
                canonical = idle()["bbc_statement_progress"]
                frame.locator('[data-statement-index="0"]').click()
                page.wait_for_timeout(150)
                idle()
                assert idle()["bbc_statement_progress"] == canonical
                assert page.url.split("progress=")[1].split("&")[0] == token
                assert (
                    frame.locator(
                        "#finalize-statement, #reset-statement, #continue-forward, [data-thinking-toggle]"
                    ).count()
                    == 0
                )
                expect(frame.locator('[data-statement-index="2"]')).to_be_disabled()
                page.reload()
                idle()
                frame = workspace_frame()
                assert idle()["bbc_statement_progress"] == canonical
                assert (
                    frame.locator(
                        "#finalize-statement, #reset-statement, #continue-forward, [data-thinking-toggle]"
                    ).count()
                    == 0
                )
                frame.locator('[data-statement-index="1"]').click()
                page.wait_for_timeout(150)
                idle()
                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(600)
                frame = workspace_frame()
                frame.locator("#finalize-statement").scroll_into_view_if_needed()
                assert frame.evaluate(
                    "document.documentElement.scrollWidth <= innerWidth"
                )
                page.screenshot(path=str(results / "statement-component-narrow.png"))
                page.set_viewport_size({"width": 1280, "height": 900})
                page.wait_for_timeout(600)
                frame = workspace_frame()
                check(
                    "Finalized statement tabs are read-only, reject future views and preserve bookmark/refresh state"
                )
        else:
            page.screenshot(path=str(results / "statement-component.png"))
            frame.locator("#finish-workspace").click()
            page.wait_for_timeout(200)
            idle()
    assert idle()["bbc_stage"] == 4
    assert idle()["bbc_statement_completion"]["statementsFinalized"] == 3
    check(
        "Custom component initialization, resize/value messages, wrong checks, touch placement and three-statement completion"
    )
