# the-balanced-books-challenge: browser version

This separate browser entrypoint runs entirely on the learner's device. The live Streamlit app, server requirements, case modules, deployment settings, and existing workflows are unchanged. Do not merge this branch into main.

The build reuses the accepted Dock to Dollar source implementation (`8a0f25a2bff6f9f1eacbc8ab132ababc94974c87`) and static runtime (`80067eb6a77b6eba7f5f6c8974389301f8c7747c`). It extracts renderer declarations and fails if the expected server driver changes. App-specific progress and teaching rules remain in the original modules.

## Build and local tests

```bash
/workspace/.cloud-setup/venvs/main/bin/python -m browser.build
/workspace/.cloud-setup/venvs/main/bin/python -m browser.test_app
python -m browser.test_browser
```

The last command needs Playwright and Chromium at `/usr/bin/chromium`, available in the saved cloud environment. Run the repository's existing unit tests with its prepared interpreter, and `python -m compileall -q browser`. Optional build arguments `--runtime-archive` and `--asset-cache` reuse cached inputs but still verify every committed hash.

The pinned runtime is stlite 1.8.1, patched Streamlit 1.57.0, Pyodide 0.29.3. Do not install `requirements.txt` into stlite. All JavaScript, fonts, WebAssembly, Python packages and app assets are local and hash-verified. Static hosting works at a repository subdirectory; opening with file:// is unsupported.

## Review navigation

Compact boxed Back/Forward arrows at the upper right retain accessible names, focus rings, tooltips and 44-pixel touch targets. Back is view-only: no edits, submissions, hints/reveals, scoring, reset or progress changes. Forward traverses reached pages and stops at the actual current page. Existing validation controls unlock new steps. A range-checked `view` URL parameter is separate from earned progress. Browser toolbar history is not the supported activity navigation interface.

Navigation treats each inbox event and equation transaction as a page, followed by the statement workspace and debrief. The existing three-statement workspace retains its validation and finalized tabs. Both original local HTML components are packaged with their original paths and retain componentReady, frame-height, scroll and value messages. The browser build narrowly patches the pinned stlite frontend to skip the legacy HTTP reachability probe for its synthetic stlite.invalid kernel origin; frames are still served through the local kernel. The original npm archive is integrity-verified before this patch, and manifest.json records the patched file hash. A browser-only statement adapter separates the viewed statement tab from earned workspace progress. Earlier tabs disable edits, checks, reset and new thinking reveals, while future tabs remain blocked; partial placement, tile order and statement_view bookmarks survive refresh. Outer review displays all three finalized statements with no new reveal or mutation controls. The live wrapper and HTML files are unchanged.

## Review and publication

See [VALIDATION.md](VALIDATION.md), [browser results](review/browser-results.json), and the screenshots in `review/`.

The approved source branch is `rollout/stlite-browser-navigation`. Its separate static branch is `stlite-browser`, in this same repository, with generated files at the branch root and `.nojekyll`. Main remains at `ea92880a95243fb297168c9a9ce559c7dbbd1694`. No PR, merge, new repository, credential, contract or paid service is needed.

GitHub metadata was checked before preparing publication: `has_pages=false`. Current tools do not enable Pages. To activate: repository **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: stlite-browser → Folder: / (root) → Save**. Recheck that there is still no existing Pages site before saving. If another site appeared, stop and report it instead of replacing it. Confirm the resulting Pages deployment and its exact commit before distributing its URL.

Hosted UI testing remains blocked by the saved environment's Pages-hostname proxy restriction. No bypass is used. A classroom device/browser and school-network trial remains necessary; local functional checks make no capacity claim for 40–45 or 80–135 learners. No central saving is added.
