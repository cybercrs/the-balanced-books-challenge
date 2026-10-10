# Browser validation — 2026-10-10

Repository: `cybercrs/the-balanced-books-challenge`. Source branch: `rollout/stlite-browser-navigation`. Static branch: `stlite-browser`. Baseline main: `ea92880a95243fb297168c9a9ce559c7dbbd1694`.

| Check | Final result |
| --- | --- |
| Repository unit/AppTest suite including three navigation regressions | Passed: 22 |
| Browser entrypoint AppTest regressions | Passed: 3 |
| Actual Chromium/stlite/Wasm walkthrough | Passed: 14 checks |
| Pinned build and local asset integrity | Passed |
| Ruff 0.14.0 on new browser source/tests | Passed |
| Python compilation, loader JavaScript syntax and Git whitespace | Passed |
| Hosted HTTPS UI, physical device/browser matrix, classroom capacity | Not run |

Actual browser runtime: {"pyodide": "0.29.3", "python": "3.13.2", "streamlit": "1.57.0"}.

The complete browser walkthrough ran with external traffic blocked by a closed test proxy and local static files served under `/lesson/`. Final errors: zero console errors, zero page errors, zero external requests, zero HTTP asset errors. Review, future-view rejection, drafts, complete lessons, deliberate wrong selections/revisions, keyboard focus/Enter, 390-pixel rendering, reset, independent sessions, and intended refresh/bookmark behavior were exercised. Detailed checks and screenshots are committed under `review/`. The test harness adds diagnostic console state only to its HTTP test response; diagnostics are absent from the published app.

Navigation treats each inbox event and equation transaction as a page, followed by the statement workspace and debrief. The existing three-statement workspace retains its validation and finalized tabs. Both original local HTML components are packaged with their original paths and retain componentReady, frame-height, scroll and value messages. The browser build narrowly patches the pinned stlite frontend to skip the legacy HTTP reachability probe for its synthetic stlite.invalid kernel origin; frames are still served through the local kernel. The original npm archive is integrity-verified before this patch, and manifest.json records the patched file hash. A browser-only statement adapter separates the viewed statement tab from earned workspace progress. Earlier tabs disable edits, checks, reset and new thinking reveals, while future tabs remain blocked; partial placement, tile order and statement_view bookmarks survive refresh. Outer review displays all three finalized statements with no new reveal or mutation controls. The live wrapper and HTML files are unchanged.

Source protection: `streamlit_app.py`, original case/engine/progress modules, `requirements.txt`, `.streamlit/`, and the original workflows remain byte-identical to baseline main. The only workflow added is isolated browser validation. Browser files and navigation tests are additive.

No final functional failure remains. Development test harness locator/timing corrections and any runtime compatibility adaptations are captured in the code; incomplete early runs are not represented as successful. Pages activation and hosted classroom-device checks remain outstanding. No classroom capacity claim is made.
