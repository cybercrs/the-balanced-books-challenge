/** Native DOM workspace. No iframe, kernel, or message bridge. */
export function mount(target,args,onChange,onThinking){
 const document=target.attachShadow({mode:'open'});document.innerHTML='<style>'+"\n    :host {\n      --red: #ce0037;\n      --red-dark: #a9002e;\n      --blue: #003087;\n      --blue-soft: #eef4ff;\n      --ink: #14213d;\n      --muted: #526176;\n      --line: #d9e0ea;\n      --surface: #ffffff;\n      --background: #f6f8fb;\n      --success: #137a4b;\n      --success-soft: #e7f4ed;\n      --warning: #8a5100;\n      --warning-soft: #fff6e8;\n    }\n\n    * { box-sizing: border-box; }\n    :host { margin: 0; padding: 0; background: transparent; color: var(--ink); font-family: Arial, Helvetica, sans-serif; }\n    button { font: inherit; }\n    .workspace { background: var(--background); border: 1px solid var(--line); border-radius: 16px; padding: 18px; }\n    .workspace-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; margin-bottom: 14px; }\n    .workspace-header h2 { color: var(--blue); font-size: 1.2rem; margin: 0 0 4px; }\n    .workspace-header p { color: var(--muted); font-size: .91rem; line-height: 1.45; margin: 0; max-width: 720px; }\n    .drag-label { background: var(--blue-soft); border: 1px solid #c8d9f5; border-radius: 999px; color: var(--blue); font-size: .78rem; font-weight: 800; padding: 7px 10px; white-space: nowrap; }\n\n    .statement-nav { display: grid; grid-template-columns: repeat(3, 1fr); gap: 7px; margin-bottom: 14px; }\n    .statement-nav button { background: #e9edf4; border: 1px solid #d4dbe6; border-radius: 999px; color: #58667a; cursor: pointer; font-size: .8rem; font-weight: 800; min-height: 38px; padding: 7px 10px; }\n    .statement-nav button.active { background: var(--red); border-color: var(--red); color: white; }\n    .statement-nav button.complete:not(.active) { background: var(--success-soft); border-color: #a8d5be; color: #0a653d; }\n    .statement-nav button:disabled { cursor: not-allowed; opacity: .58; }\n\n    .workspace-body { align-items: stretch; display: grid; gap: 12px; grid-template-columns: minmax(230px, .72fr) minmax(0, 2fr); }\n    .account-sidebar { height: 680px; overflow-y: auto; scrollbar-gutter: stable; }\n    .statement-content { height: 680px; overflow-y: auto; padding-right: 4px; scrollbar-gutter: stable; }\n    .workspace-body.bank-hidden { grid-template-columns: 1fr; }\n    .workspace-body.bank-hidden .statement-content { height: auto; overflow: visible; padding-right: 0; }\n\n    .account-bank { background: var(--surface); border: 1px solid var(--line); border-radius: 13px; margin: 0; padding: 13px; }\n    .bank-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; margin-bottom: 9px; }\n    .bank-heading strong { color: var(--blue); }\n    .bank-heading span { color: var(--muted); font-size: .78rem; }\n    .tiles { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }\n    .account-sidebar .bank-heading { align-items: flex-start; display: grid; }\n    .account-sidebar .tiles { grid-template-columns: 1fr; }\n    .account-sidebar .tile { min-height: 44px; padding: 7px 8px; }\n    .tile { align-items: center; background: #fff; border: 1px solid #b9c4d3; border-radius: 9px; color: var(--ink); cursor: grab; display: flex; gap: 8px; justify-content: space-between; min-height: 49px; padding: 8px 10px; text-align: left; width: 100%; }\n    .tile:hover { border-color: var(--blue); box-shadow: 0 3px 10px rgba(0,48,135,.09); }\n    .tile.selected { border: 2px solid var(--red); background: #fff5f7; }\n    .tile-name { font-size: .84rem; font-weight: 750; line-height: 1.2; }\n    .tile-value { color: var(--blue); font-size: .84rem; font-variant-numeric: tabular-nums; font-weight: 850; white-space: nowrap; }\n    .empty-bank { color: var(--muted); font-size: .86rem; grid-column: 1 / -1; padding: 8px 2px; }\n\n    .statement-shell { background: var(--surface); border: 1px solid var(--line); border-radius: 13px; padding: 15px; }\n    .statement-title { color: var(--blue); font-size: 1.02rem; font-weight: 850; text-align: center; }\n    .statement-period { color: var(--muted); font-size: .8rem; margin: 3px 0 12px; text-align: center; }\n    .section-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }\n    .dropzone { background: #fafbfd; border: 2px dashed #bac5d4; border-radius: 11px; min-height: 118px; padding: 10px; }\n    .dropzone.over { background: var(--blue-soft); border-color: var(--blue); }\n    .dropzone h3 { color: var(--ink); font-size: .88rem; margin: 0 0 3px; }\n    .dropzone p { color: var(--muted); font-size: .76rem; line-height: 1.35; margin: 0 0 7px; }\n    .placed-list { display: grid; gap: 5px; min-height: 28px; }\n    .placed-item { align-items: center; background: #fff; border: 1px solid #d2dae5; border-radius: 8px; display: flex; gap: 7px; justify-content: space-between; padding: 6px 7px; }\n    .placed-copy { min-width: 0; }\n    .placed-name { display: block; font-size: .79rem; font-weight: 750; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }\n    .placed-value { color: var(--blue); font-size: .77rem; font-variant-numeric: tabular-nums; font-weight: 800; }\n    .remove { background: transparent; border: 0; color: var(--red); cursor: pointer; font-size: 1rem; font-weight: 900; line-height: 1; padding: 3px 5px; }\n    .place-selected { background: transparent; border: 1px solid #aeb9c8; border-radius: 7px; color: var(--blue); cursor: pointer; font-size: .73rem; font-weight: 800; margin-top: 7px; padding: 5px 7px; width: 100%; }\n    .place-selected:disabled { color: #8d98a8; cursor: not-allowed; opacity: .65; }\n\n    .totals { background: var(--blue-soft); border: 1px solid #c7d8f4; border-radius: 11px; margin-top: 10px; padding: 8px 11px; }\n    .total-line { display: flex; gap: 12px; justify-content: space-between; padding: 4px 0; }\n    .total-line span:first-child { color: var(--muted); font-size: .82rem; }\n    .total-line strong { color: var(--ink); font-size: .86rem; font-variant-numeric: tabular-nums; }\n    .total-line.grand { border-bottom: 3px double var(--ink); border-top: 1px solid #77849a; margin-top: 3px; padding: 7px 0 5px; }\n    .balance-status { border-radius: 8px; font-size: .8rem; font-weight: 800; margin-top: 7px; padding: 7px 9px; text-align: center; }\n    .balance-status.balanced { background: var(--success-soft); color: var(--success); }\n    .balance-status.unbalanced { background: var(--warning-soft); color: var(--warning); }\n\n    .feedback { border-radius: 10px; font-size: .84rem; line-height: 1.45; margin-top: 11px; padding: 9px 11px; }\n    .feedback.success { background: var(--success-soft); border-left: 5px solid var(--success); color: #0a5d39; }\n    .feedback.review { background: var(--warning-soft); border-left: 5px solid var(--warning); color: #674000; }\n    .feedback ul { margin: 5px 0 0 18px; padding: 0; }\n\n    .thinking { background: #fff5f7; border-left: 5px solid var(--red); border-radius: 10px; margin-top: 12px; padding: 11px 12px; }\n    .thinking .label { color: var(--red); font-size: .72rem; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }\n    .thinking strong { display: block; font-size: .91rem; line-height: 1.4; margin: 3px 0 7px; }\n    .thinking-toggle { align-items: center; background: #fff; border: 1px solid #c4cee0; border-radius: 8px; color: var(--blue); cursor: pointer; display: flex; font-size: .82rem; font-weight: 800; justify-content: space-between; padding: 7px 9px; width: 100%; }\n    .thinking-toggle .chevron { font-size: 1rem; line-height: 1; transition: transform .15s ease; }\n    .thinking-toggle[aria-expanded=\"true\"] .chevron { transform: rotate(180deg); }\n    .thinking-answer { color: var(--muted); font-size: .84rem; line-height: 1.45; margin: 9px 2px 1px; }\n\n    .actions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; margin-top: 12px; }\n    .actions button { border-radius: 8px; cursor: pointer; font-size: .82rem; font-weight: 800; min-height: 39px; padding: 8px 12px; }\n    .primary { background: var(--red); border: 1px solid var(--red); color: white; }\n    .primary:hover { background: var(--red-dark); border-color: var(--red-dark); }\n    .secondary { background: #fff; border: 1px solid #aeb9c8; color: var(--ink); }\n\n    @media (max-width: 740px) {\n      .workspace { padding: 12px; }\n      .workspace-header { display: block; }\n      .drag-label { display: inline-block; margin-top: 9px; }\n      .statement-nav { grid-template-columns: 1fr; }\n      .workspace-body { grid-template-columns: 1fr; }\n      .account-sidebar, .statement-content { height: auto; overflow: visible; padding-right: 0; }\n      .account-sidebar .tiles { grid-template-columns: 1fr 1fr; }\n      .tiles { grid-template-columns: 1fr 1fr; }\n      .section-grid { grid-template-columns: 1fr; }\n    }\n    @media (max-width: 480px) {\n      .account-sidebar .tiles { grid-template-columns: 1fr; }\n      .tiles { grid-template-columns: 1fr; }\n      .actions { display: grid; grid-template-columns: 1fr; }\n      .actions button { width: 100%; }\n    }\n  \nbutton{min-height:44px;}button:focus-visible{outline:2px solid var(--blue);outline-offset:3px;} .remove{min-width:44px;min-height:44px;}\n"+ '</style><main id="root" aria-live="polite"></main>';

    const state = {
      args: null,
      stage: 0,
      initialized: false,
      finalized: [false, false, false],
      placements: [{}, {}, {}],
      selected: null,
      attempts: [0, 0, 0],
      feedback: [null, null, null],
      thinkingOpen: [false, false, false],
      shuffledAccounts: [],
      scrollPositions: [
        {sidebar: 0, statement: 0},
        {sidebar: 0, statement: 0},
        {sidebar: 0, statement: 0},
      ],
    };

    const statements = [
      {
        short: "Income Statement",
        title: "Multi-Step Income Statement",
        period: "For the Month Ended September 30",
        zones: [
          ["operating_revenue", "Operating revenue", "Revenue earned from the company's primary operations"],
          ["operating_expenses", "Operating expenses", "Costs used to generate operating revenue"],
          ["other_items", "Other revenues and expenses", "Nonoperating items, if any"],
        ],
        expected: {service_revenue: "operating_revenue", rent_expense: "operating_expenses", supplies_expense: "operating_expenses"},
        question: "Why does the $600 owner distribution not appear among the company's expenses?",
        answer: "The distribution is an accounting transaction because Cash and Dividends change, but it is a distribution of equity—not a cost of earning revenue. It does not affect net income.",
      },
      {
        short: "Retained Earnings",
        title: "Retained Earnings Calculation",
        period: "For the Month Ended September 30",
        zones: [
          ["additions", "Additions", "Place items that increase retained earnings here"],
          ["subtractions", "Subtractions", "Place items that decrease retained earnings here"],
        ],
        expected: {net_income: "additions", dividends: "subtractions"},
        question: "Why does net income increase retained earnings while an owner distribution decreases it?",
        answer: "Net income adds earnings kept by the company. A distribution transfers part of those accumulated earnings to an owner, so it reduces retained earnings without reducing net income.",
      },
      {
        short: "Balance Sheet",
        title: "Classified Balance Sheet",
        period: "September 30",
        zones: [
          ["current_assets", "Current assets", "Assets expected to be used or converted to cash within one year"],
          ["long_term_investments", "Long-term investments", "Investments the company expects to hold beyond one year"],
          ["ppe", "Property, plant, and equipment", "Long-lived operating assets"],
          ["intangible_assets", "Intangible assets", "Long-lived assets without physical substance"],
          ["current_liabilities", "Current liabilities", "Obligations expected to be paid within one year"],
          ["long_term_liabilities", "Long-term liabilities", "Obligations not expected to be paid within one year"],
          ["equity", "Stockholders' equity", "Owner investment plus retained earnings"],
        ],
        expected: {cash: "current_assets", accounts_receivable: "current_assets", supplies: "current_assets", equipment: "ppe", accounts_payable: "current_liabilities", common_stock: "equity", ending_retained_earnings: "equity"},
        question: "Which prior statement supplies ending retained earnings, and why does that amount matter here?",
        answer: "The retained earnings calculation supplies the ending balance. Including it in stockholders' equity helps the balance sheet show that total assets equal total liabilities plus stockholders' equity.",
      },
    ];

    function setHeight() {}
    function setComponentValue(value) { onChange({...value,thinkingOpen:[...state.thinkingOpen]}); }
    function money(value) {
      return new Intl.NumberFormat("en-US", {style: "currency", currency: "USD", maximumFractionDigits: 0}).format(value || 0);
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
    }

    function shuffledCopy(items) {
      const result = [...items];
      for (let index = result.length - 1; index > 0; index -= 1) {
        const swapIndex = Math.floor(Math.random() * (index + 1));
        [result[index], result[swapIndex]] = [result[swapIndex], result[index]];
      }
      return result;
    }

    function progressPayload() {
      return {
        stage: state.earnedStage ?? state.stage,
        finalized: [...state.finalized],
        placements: state.placements.map(placement => ({...placement})),
        selected: state.selected,
        attempts: [...state.attempts],
        feedbackKinds: state.feedback.map(feedback => feedback ? feedback.kind : null),
        shuffledAccountIds: state.shuffledAccounts.map(account => account.id),
      };
    }

    function emitProgress() {
      setComponentValue({completed: false, progress: progressPayload(), browserView: state.stage});
    }

    function restoreProgress(progress) {
      if (!progress) return;
      state.stage = progress.stage;
      state.finalized = [...progress.finalized];
      state.placements = progress.placements.map(placement => ({...placement}));
      state.selected = progress.selected;
      state.attempts = [...progress.attempts];
      state.feedback = progress.feedbackKinds.map((kind, index) => {
        if (kind === "success") {
          return {kind, messages: [`${statements[index].short} finalized correctly.`]};
        }
        if (kind === "review") {
          return {kind, messages: validationMessages(index)};
        }
        return null;
      });
    }

    function allTiles() {
      const base = state.shuffledAccounts;
      const derived = state.args.derived || [];
      if (state.stage === 1) return [...base, ...derived.filter(tile => tile.id === "net_income")];
      if (state.stage === 2) return [...base, ...derived.filter(tile => tile.id === "ending_retained_earnings")];
      return base;
    }

    function tileById(id) {
      return allTiles().find(tile => tile.id === id);
    }

    function zoneName(zoneId, statementIndex = state.stage) {
      const zone = statements[statementIndex].zones.find(item => item[0] === zoneId);
      return zone ? zone[1] : "that section";
    }

    function placedIds(zoneId) {
      return Object.entries(state.placements[state.stage]).filter(([, zone]) => zone === zoneId).map(([id]) => id);
    }

    function sumZone(zoneId) {
      return placedIds(zoneId).reduce((sum, id) => sum + (tileById(id)?.value || 0), 0);
    }

    function signedSumZone(zoneId) {
      return placedIds(zoneId).reduce((sum, id) => {
        const tile = tileById(id);
        return sum + ((tile?.incomeSign || 0) * (tile?.value || 0));
      }, 0);
    }

    function placeTile(id, zoneId) {
      if (state.stage < state.earnedStage) return;
      if (state.finalized[state.stage] || !tileById(id)) return;
      state.placements[state.stage][id] = zoneId;
      state.selected = null;
      state.feedback[state.stage] = null;
      render();
      emitProgress();
    }

    function toggleTile(id) {
      if (state.stage < state.earnedStage) return;
      if (state.finalized[state.stage]) return;
      state.selected = state.selected === id ? null : id;
      render();
      emitProgress();
    }

    function removeTile(id) {
      if (state.stage < state.earnedStage) return;
      if (state.finalized[state.stage]) return;
      delete state.placements[state.stage][id];
      state.feedback[state.stage] = null;
      render();
      emitProgress();
    }

    function validationMessages(statementIndex = state.stage) {
      const expected = statements[statementIndex].expected;
      const placements = state.placements[statementIndex];
      const incorrectZones = [...new Set(
        Object.entries(placements)
          .filter(([id, zone]) => expected[id] !== zone)
          .map(([, zone]) => zone)
      )];
      const messages = incorrectZones.map(zone => `One of the balances in ${zoneName(zone, statementIndex)} doesn't belong there.`);
      const correctCount = Object.entries(expected).filter(([id, zone]) => placements[id] === zone).length;
      const remaining = Object.keys(expected).length - correctCount;
      if (remaining > 0) {
        messages.push(`You still have ${remaining} account balance${remaining === 1 ? "" : "s"} to place correctly on this statement.`);
      }
      return messages;
    }

    function finalizeCurrent() {
      if (state.stage < state.earnedStage) return;
      if (state.finalized[state.stage]) return;
      const messages = validationMessages();
      state.attempts[state.stage] += 1;
      if (messages.length) {
        state.feedback[state.stage] = {kind: "review", messages};
      } else {
        state.finalized[state.stage] = true;
        state.feedback[state.stage] = {kind: "success", messages: [`${statements[state.stage].short} finalized correctly.`]};
      }
      render();
      emitProgress();
    }

    function resetCurrent() {
      if (state.stage < state.earnedStage) return;
      if (state.finalized[state.stage]) return;
      state.placements[state.stage] = {};
      state.selected = null;
      state.feedback[state.stage] = null;
      render();
      emitProgress();
    }

    function selectStatement(index) {
      if (state.stage < state.earnedStage && index > state.earnedStage) return;
      const firstUnfinished = state.finalized.findIndex(value => !value);
      if (state.finalized[index] || index === firstUnfinished) {
        rememberScrollPosition();
        if (index > state.earnedStage) {
          state.earnedStage = index;
          state.selected = null;
        }
        state.stage = index;
        render(false);
        emitProgress();
      }
    }

    function continueForward() {
      if (state.stage < state.earnedStage) return;
      if (!state.finalized[state.stage]) return;
      const next = state.finalized.findIndex(value => !value);
      rememberScrollPosition();
      if (next >= 0) { state.stage = next; state.earnedStage = next; }
      state.selected = null;
      render(false);
      emitProgress();
    }

    function finishWorkspace() {
      if (state.stage < state.earnedStage) return;
      if (!state.finalized.every(Boolean)) return;
      setComponentValue({
        completed: true,
        statementsFinalized: state.finalized.filter(Boolean).length,
        attempts: state.attempts.reduce((sum, value) => sum + value, 0),
        progress: progressPayload(), browserView: state.stage,
      });
    }

    function renderBank() {
      if (state.finalized[state.stage]) return "";
      const placements = state.placements[state.stage];
      const available = allTiles().filter(tile => !placements[tile.id]);
      const tiles = available.length ? available.map(tile => `
        <button type="button" class="tile ${state.selected === tile.id ? "selected" : ""}" draggable="true" data-tile-id="${escapeHtml(tile.id)}" aria-pressed="${state.selected === tile.id}">
          <span class="tile-name">${escapeHtml(tile.label)}</span><span class="tile-value">${money(tile.value)}</span>
        </button>`).join("") : '<div class="empty-bank">Every available balance has been placed. Remove a balance from a section to move it elsewhere.</div>';
      return `<section class="account-bank"><div class="bank-heading"><strong>Correct account balances</strong><span>Drag a balance, or select it and use “Place selected here.”</span></div><div class="tiles">${tiles}</div></section>`;
    }

    function renderZone(zone) {
      const [id, title, description] = zone;
      const placed = placedIds(id);
      const items = placed.length ? placed.map(tileId => {
        const tile = tileById(tileId);
        return `<div class="placed-item"><div class="placed-copy"><span class="placed-name">${escapeHtml(tile.label)}</span><span class="placed-value">${money(tile.value)}</span></div>${state.finalized[state.stage] ? "" : `<button type="button" class="remove" data-remove-id="${escapeHtml(tileId)}" aria-label="Remove ${escapeHtml(tile.label)}">×</button>`}</div>`;
      }).join("") : '<div class="empty-bank">No balances placed</div>';
      return `<section class="dropzone" data-zone-id="${escapeHtml(id)}" aria-label="${escapeHtml(title)} drop area"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(description)}</p><div class="placed-list">${items}</div>${state.finalized[state.stage] ? "" : `<button type="button" class="place-selected" data-place-zone="${escapeHtml(id)}" ${state.selected ? "" : "disabled"}>Place selected here</button>`}</section>`;
    }

    function renderTotals() {
      if (state.stage === 0) {
        const revenue = sumZone("operating_revenue");
        const expenses = sumZone("operating_expenses");
        const incomeFromOperations = revenue - expenses;
        const other = signedSumZone("other_items");
        return `<div class="totals"><div class="total-line"><span>Total operating revenue</span><strong>${money(revenue)}</strong></div><div class="total-line"><span>Total operating expenses</span><strong>${money(expenses)}</strong></div><div class="total-line"><span>Income from operations</span><strong>${money(incomeFromOperations)}</strong></div><div class="total-line"><span>Net other revenues and expenses</span><strong>${money(other)}</strong></div><div class="total-line grand"><span>Net income</span><strong>${money(incomeFromOperations + other)}</strong></div></div>`;
      }
      if (state.stage === 1) {
        const beginning = (state.args.derived || []).find(tile => tile.id === "beginning_retained_earnings")?.value || 0;
        const additions = sumZone("additions");
        const subtractions = sumZone("subtractions");
        return `<div class="totals"><div class="total-line"><span>Beginning retained earnings</span><strong>${money(beginning)}</strong></div><div class="total-line"><span>Additions</span><strong>${money(additions)}</strong></div><div class="total-line"><span>Subtractions</span><strong>${money(subtractions)}</strong></div><div class="total-line grand"><span>Ending retained earnings</span><strong>${money(beginning + additions - subtractions)}</strong></div></div>`;
      }
      const currentAssets = sumZone("current_assets");
      const longTermInvestments = sumZone("long_term_investments");
      const ppe = sumZone("ppe");
      const intangibleAssets = sumZone("intangible_assets");
      const currentLiabilities = sumZone("current_liabilities");
      const longTermLiabilities = sumZone("long_term_liabilities");
      const equity = sumZone("equity");
      const assets = currentAssets + longTermInvestments + ppe + intangibleAssets;
      const liabilities = currentLiabilities + longTermLiabilities;
      const liabilitiesEquity = liabilities + equity;
      const balanced = assets === liabilitiesEquity && assets !== 0;
      return `<div class="totals"><div class="total-line"><span>Total current assets</span><strong>${money(currentAssets)}</strong></div><div class="total-line"><span>Total long-term investments</span><strong>${money(longTermInvestments)}</strong></div><div class="total-line"><span>Total property, plant, and equipment</span><strong>${money(ppe)}</strong></div><div class="total-line"><span>Total intangible assets</span><strong>${money(intangibleAssets)}</strong></div><div class="total-line grand"><span>Total assets</span><strong>${money(assets)}</strong></div><div class="total-line"><span>Total current liabilities</span><strong>${money(currentLiabilities)}</strong></div><div class="total-line"><span>Total long-term liabilities</span><strong>${money(longTermLiabilities)}</strong></div><div class="total-line"><span>Total liabilities</span><strong>${money(liabilities)}</strong></div><div class="total-line"><span>Total stockholders' equity</span><strong>${money(equity)}</strong></div><div class="total-line grand"><span>Total liabilities and stockholders' equity</span><strong>${money(liabilitiesEquity)}</strong></div><div class="balance-status ${balanced ? "balanced" : "unbalanced"}">${balanced ? "Balanced — both sides equal " + money(assets) : "Not balanced yet — difference " + money(Math.abs(assets - liabilitiesEquity))}</div></div>`;
    }

    function renderFeedback() {
      const feedback = state.feedback[state.stage];
      if (!feedback) return "";
      const body = feedback.messages.length === 1 ? escapeHtml(feedback.messages[0]) : `<ul>${feedback.messages.slice(0, 8).map(message => `<li>${escapeHtml(message)}</li>`).join("")}</ul>`;
      return `<div class="feedback ${feedback.kind}" role="status">${body}</div>`;
    }

    function renderThinking() {
      if (!state.finalized[state.stage]) return "";
      const statement = statements[state.stage];
      const open = state.thinkingOpen[state.stage];
      if (state.stage < state.earnedStage) return open ? `<section class="thinking"><div class="label">Test Your Thinking</div><strong>${escapeHtml(statement.question)}</strong><p class="thinking-answer">${escapeHtml(statement.answer)}</p></section>` : "";
      return `<section class="thinking"><div class="label">Test Your Thinking</div><strong>${escapeHtml(statement.question)}</strong><button type="button" class="thinking-toggle" data-thinking-toggle aria-expanded="${open}" aria-label="Review the explanation"><span>Review the explanation</span><span class="chevron" aria-hidden="true">⌄</span></button>${open ? `<p class="thinking-answer">${escapeHtml(statement.answer)}</p>` : ""}</section>`;
    }

    function renderActions() {
      if (state.stage < state.earnedStage) return "";
      if (!state.finalized[state.stage]) {
        return `<div class="actions"><button type="button" class="secondary" id="reset-statement">Reset this statement</button><button type="button" class="primary" id="finalize-statement">Check and finalize</button></div>`;
      }
      const allFinalized = state.finalized.every(Boolean);
      if (allFinalized) return `<div class="actions"><button type="button" class="primary" id="finish-workspace">Continue to debrief</button></div>`;
      const firstUnfinished = state.finalized.findIndex(value => !value);
      return `<div class="actions"><button type="button" class="primary" id="continue-forward">Continue to ${escapeHtml(statements[firstUnfinished].short)}</button></div>`;
    }

    function rememberScrollPosition() {
      const sidebar = document.querySelector(".account-sidebar");
      const statement = document.querySelector(".statement-content");
      if (sidebar) state.scrollPositions[state.stage].sidebar = sidebar.scrollTop;
      if (statement) state.scrollPositions[state.stage].statement = statement.scrollTop;
    }

    function render(captureScroll = true) {
      if (!state.args) return;
      if (captureScroll) rememberScrollPosition();
      const firstUnfinished = state.finalized.findIndex(value => !value);
      const nav = statements.map((statement, index) => {
        const enabled = index <= state.earnedStage || state.stage === state.earnedStage && index === firstUnfinished;
        const classes = `${index === state.stage ? "active" : ""} ${state.finalized[index] ? "complete" : ""}`;
        const prefix = state.finalized[index] ? "Finalized: " : index === state.stage ? "Current: " : "Upcoming: ";
        return `<button type="button" class="${classes}" data-statement-index="${index}" ${enabled ? "" : "disabled"} aria-label="${prefix}${escapeHtml(statement.short)}">${escapeHtml(statement.short)}</button>`;
      }).join("");
      const statement = statements[state.stage];
      const bank = renderBank();
      document.getElementById("root").innerHTML = `
        <div class="workspace">
          <div class="workspace-header"><div><h2>Financial Statement Workspace</h2><p>Use the account balances to build each statement. Totals update as soon as a balance is placed.</p></div><span class="drag-label">Drag or click to place</span></div>
          <nav class="statement-nav" aria-label="Financial statements">${nav}</nav>
          <div class="workspace-body ${bank ? "" : "bank-hidden"}">
            ${bank ? `<aside class="account-sidebar" aria-label="Correct account balances sidebar">${bank}</aside>` : ""}
            <div class="statement-content">
              <section class="statement-shell"><div class="statement-title">${escapeHtml(state.args.company)} · ${escapeHtml(statement.title)}</div><div class="statement-period">${escapeHtml(statement.period)}</div><div class="section-grid">${statement.zones.map(renderZone).join("")}</div>${renderTotals()}</section>
              ${renderFeedback()}${renderThinking()}${renderActions()}
            </div>
          </div>
        </div>`;
      const savedScroll = state.scrollPositions[state.stage];
      requestAnimationFrame(() => {
        const sidebar = document.querySelector(".account-sidebar");
        const statementContent = document.querySelector(".statement-content");
        if (sidebar) sidebar.scrollTop = savedScroll.sidebar;
        if (statementContent) statementContent.scrollTop = savedScroll.statement;
      });
      setHeight();
    }

    document.addEventListener("click", event => {
      const thinkingButton = event.target.closest("[data-thinking-toggle]");
      if (thinkingButton) {
        if (state.stage < state.earnedStage) return;
        state.thinkingOpen[state.stage] = !state.thinkingOpen[state.stage];
        onThinking([...state.thinkingOpen]);
        render();
        return;
      }
      const tile = event.target.closest(".tile");
      if (tile) {
        toggleTile(tile.dataset.tileId);
        return;
      }
      const placeButton = event.target.closest("[data-place-zone]");
      if (placeButton && state.selected) {
        placeTile(state.selected, placeButton.dataset.placeZone);
        return;
      }
      const removeButton = event.target.closest("[data-remove-id]");
      if (removeButton) {
        removeTile(removeButton.dataset.removeId);
        return;
      }
      const statementButton = event.target.closest("[data-statement-index]");
      if (statementButton) {
        selectStatement(Number(statementButton.dataset.statementIndex));
        return;
      }
      if (event.target.closest("#reset-statement")) resetCurrent();
      else if (event.target.closest("#finalize-statement")) finalizeCurrent();
      else if (event.target.closest("#continue-forward")) continueForward();
      else if (event.target.closest("#finish-workspace")) finishWorkspace();
    });

    document.addEventListener("dragstart", event => {
      const tile = event.target.closest(".tile");
      if (tile) event.dataTransfer.setData("text/plain", tile.dataset.tileId);
    });

    document.addEventListener("dragover", event => {
      const zone = event.target.closest(".dropzone");
      if (!zone) return;
      event.preventDefault();
      zone.classList.add("over");
    });

    document.addEventListener("dragleave", event => {
      const zone = event.target.closest(".dropzone");
      if (zone) zone.classList.remove("over");
    });

    document.addEventListener("drop", event => {
      const zone = event.target.closest(".dropzone");
      if (!zone) return;
      event.preventDefault();
      zone.classList.remove("over");
      placeTile(event.dataTransfer.getData("text/plain"), zone.dataset.zoneId);
    });


    state.args = args;
    const initialProgress = args.initialProgress;
    const accountsById = new Map((args.accounts || []).map(account => [account.id, account]));
    const savedOrder = initialProgress?.shuffledAccountIds || [];
    state.shuffledAccounts = savedOrder.length === accountsById.size ? savedOrder.map(id => accountsById.get(id)).filter(Boolean) : shuffledCopy(args.accounts || []);
    restoreProgress(initialProgress);state.earnedStage = state.stage;
    const savedView=Number(args.browserView);
    if(args.browserView!==null&&args.browserView!==undefined&&Number.isInteger(savedView)&&savedView>=0&&savedView<=state.earnedStage)state.stage=savedView;
    state.thinkingOpen=args.thinkingOpen||[false,false,false];state.initialized=true;
    render(false);emitProgress();

}
