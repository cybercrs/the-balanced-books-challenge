"""Original readonly statement-view correction, used only by native export tooling."""

def adapt_frontend(frontend):
    source = frontend
    source = source.replace(
        "stage: state.stage,", "stage: state.earnedStage ?? state.stage,"
    )
    source = source.replace(
        "setComponentValue({completed: false, progress: progressPayload()});",
        "setComponentValue({completed: false, progress: progressPayload(), browserView: state.stage});",
    )
    source = source.replace(
        "        progress: progressPayload(),",
        "        progress: progressPayload(), browserView: state.stage,",
    )
    source = source.replace(
        "restoreProgress(initialProgress);",
        """restoreProgress(initialProgress);
        state.earnedStage = state.stage;
        const savedView = Number(state.args.browserView);
        if (state.args.browserView !== null && state.args.browserView !== undefined && Number.isInteger(savedView) && savedView >= 0 && savedView <= state.earnedStage) state.stage = savedView;""",
    )
    source = source.replace(
        "const open = state.thinkingOpen[state.stage];",
        """const open = state.thinkingOpen[state.stage];
      if (state.stage < state.earnedStage) return open ? `<section class="thinking"><div class="label">Test Your Thinking</div><strong>${escapeHtml(statement.question)}</strong><p class="thinking-answer">${escapeHtml(statement.answer)}</p></section>` : "";""",
    )
    source = source.replace(
        "state.stage = index;\n        state.selected = null;",
        """if (index > state.earnedStage) {
          state.earnedStage = index;
          state.selected = null;
        }
        state.stage = index;""",
    )
    source = source.replace(
        "if (next >= 0) state.stage = next;",
        "if (next >= 0) { state.stage = next; state.earnedStage = next; }",
    )
    source = source.replace(
        "function selectStatement(index) {",
        "function selectStatement(index) {\n      if (state.stage < state.earnedStage && index > state.earnedStage) return;",
    )
    source = source.replace(
        "function renderActions() {",
        'function renderActions() {\n      if (state.stage < state.earnedStage) return "";',
    )
    source = source.replace(
        "if (thinkingButton) {",
        "if (thinkingButton) {\n        if (state.stage < state.earnedStage) return;",
    )
    source = source.replace(
        "const enabled = state.finalized[index] || index === firstUnfinished;",
        "const enabled = index <= state.earnedStage || state.stage === state.earnedStage && index === firstUnfinished;",
    )
    return source
