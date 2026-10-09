/**
 * Screen-reader checks that axe can't do, because they depend on how content
 * is *read* rather than on how it's marked up.
 *
 * checkNoDoubleAnnouncements(selector)
 *   Walks Chrome's real accessibility tree in reading order (what VoiceOver's
 *   "next item" or NVDA's down-arrow steps through) and fails when two
 *   neighboring items say the same thing. Catches the classic "pill read twice"
 *   bug: a visually hidden <input> inside a <label> followed by its visible
 *   <span> text, or sr-only text sitting next to the same visible text.
 *   Two controls with the same name (a "Search" box and its "Search" button)
 *   and repeated values in neighboring table cells are allowed.
 *
 * checkNoClickableText(selector)
 *   Fails when a click/mouse listener is attached to a non-interactive element
 *   (div, span, li...) that has text of its own. Chrome then exposes that text
 *   as "clickable", so VoiceOver reads plain labels as "Deadlines, clickable".
 *   Empty elements (e.g. a menu's click-to-close backdrop) are allowed.
 *   Requires the page to be visited with trackClickListeners:
 *     cy.visit(url, { onBeforeLoad: trackClickListeners })
 *
 * Both use Chrome-only APIs and skip themselves in other browsers.
 */

type AXValue = { value?: unknown };
type AXNode = {
    nodeId: string;
    ignored: boolean;
    role?: AXValue;
    name?: AXValue;
    childIds?: string[];
    backendDOMNodeId?: number;
};
type DOMNode = {
    nodeId: number;
    nodeName: string;
    frameId?: string;
    children?: DOMNode[];
    contentDocument?: DOMNode;
};
// A null item marks a table-cell boundary; repeats across cells are just data.
type ReadingItem = { text: string; role: string } | null;

// Roles a screen reader reads as a single item, including all their content.
const CONTROL_ROLES = [
    "button", "checkbox", "combobox", "link", "menuitem", "menuitemcheckbox",
    "menuitemradio", "option", "radio", "searchbox", "slider", "spinbutton",
    "switch", "tab", "textbox", "treeitem",
];

const INTERACTIVE_SELECTOR = [
    "a[href]", "button", "input", "select", "textarea", "summary", "label",
    "[tabindex]", "[contenteditable]",
    ...CONTROL_ROLES.map((role) => `[role="${role}"]`),
].join(", ");

const CELL_ROLES = ["cell", "gridcell", "columnheader", "rowheader"];

const CLICK_EVENTS = ["click", "mousedown", "mouseup", "pointerdown", "pointerup"];

function cdp<T>(command: string, params: Record<string, unknown> = {}): Cypress.Chainable<T> {
    return cy.then(() =>
        Cypress.automation("remote:debugger:protocol", { command, params }),
    ) as unknown as Cypress.Chainable<T>;
}

function isChrome(): boolean {
    if (Cypress.browser.family === "chromium") return true;
    cy.log(`Skipping screen-reader check: needs Chrome, running ${Cypress.browser.name}`);
    return false;
}

function normalize(text: string): string {
    return text.replace(/\s+/g, " ").trim().toLowerCase();
}

/** The iframe element Cypress runs the app under test in, inside the runner's DOM. */
function findAppFrame(node: DOMNode, url: string): DOMNode | undefined {
    if (node.nodeName === "IFRAME" && node.contentDocument) {
        const frameUrl = (node.contentDocument as DOMNode & { documentURL?: string }).documentURL;
        if (frameUrl === url) return node;
    }
    for (const child of node.children || []) {
        const found = findAppFrame(child, url);
        if (found) return found;
    }
    return undefined;
}

/** Flatten the accessibility subtree into what a screen reader steps through. */
function readingItems(byId: { [id: string]: AXNode }, root: AXNode): ReadingItem[] {
    const items: ReadingItem[] = [];
    const walk = (node: AXNode) => {
        const role = String(node.role?.value || "");
        const name = String(node.name?.value || "");
        if (!node.ignored && CONTROL_ROLES.indexOf(role) !== -1) {
            items.push({ text: name, role });
            return; // A control is one item; its own text isn't read again.
        }
        if (!node.ignored && role === "StaticText") {
            if (normalize(name)) items.push({ text: name, role });
            return;
        }
        const isCell = CELL_ROLES.indexOf(role) !== -1;
        if (isCell) items.push(null);
        (node.childIds || []).forEach((id) => byId[id] && walk(byId[id]));
        if (isCell) items.push(null);
    };
    walk(root);
    return items;
}

/** Neighboring items that say the same thing, unless both are controls. */
function findRepeats(items: ReadingItem[]): string[] {
    const repeats: string[] = [];
    for (let i = 1; i < items.length; i++) {
        const [prev, item] = [items[i - 1], items[i]];
        if (!prev || !item) continue;
        const bothControls = prev.role !== "StaticText" && item.role !== "StaticText";
        if (!bothControls && normalize(prev.text) === normalize(item.text)) {
            repeats.push(`"${item.text}" read twice (${prev.role}, then ${item.role})`);
        }
    }
    return repeats;
}

export function checkNoDoubleAnnouncements(selector = "main") {
    if (!isChrome()) return;
    cy.get(selector).should("exist");
    let frame: DOMNode;
    let nodes: AXNode[];
    const byId: { [id: string]: AXNode } = {};
    cy.url()
        .then((url) =>
            cdp<{ root: DOMNode }>("DOM.getDocument", { depth: -1, pierce: true }).then(({ root }) => {
                frame = findAppFrame(root, url)!;
                expect(frame, `app iframe for ${url}`).to.exist;
            }),
        )
        .then(() =>
            cdp<{ nodes: AXNode[] }>("Accessibility.getFullAXTree", { frameId: frame.frameId }),
        )
        .then((tree) => {
            nodes = tree.nodes;
            nodes.forEach((n) => (byId[n.nodeId] = n));
            return cdp<{ nodeIds: number[] }>("DOM.querySelectorAll", {
                nodeId: frame.contentDocument!.nodeId,
                selector,
            });
        })
        .then(({ nodeIds }) => {
            nodeIds.forEach((nodeId) => {
                cdp<{ node: { backendNodeId: number } }>("DOM.describeNode", { nodeId }).then(
                    ({ node }) => {
                        const root = nodes.filter((n) => n.backendDOMNodeId === node.backendNodeId)[0];
                        expect(root, `accessibility node for ${selector}`).to.exist;
                        const repeats = findRepeats(readingItems(byId, root));
                        expect(repeats, `double announcements in ${selector}`).to.deep.equal([]);
                    },
                );
            });
        });
}

/** Pass as cy.visit's onBeforeLoad so checkNoClickableText can see listeners. */
export function trackClickListeners(win: Cypress.AUTWindow) {
    const targets: EventTarget[] = [];
    (win as unknown as { __clickListenerTargets: EventTarget[] }).__clickListenerTargets = targets;
    const proto = (win as unknown as typeof globalThis).EventTarget.prototype;
    const original = proto.addEventListener;
    proto.addEventListener = function (this: EventTarget, type: string, ...rest: unknown[]) {
        if (CLICK_EVENTS.indexOf(type) !== -1 && targets.indexOf(this) === -1) {
            targets.push(this);
        }
        return (original as (...args: unknown[]) => void).call(this, type, ...rest);
    } as typeof proto.addEventListener;
}

/** Text a screen reader would attribute to el itself, not to controls inside it. */
function ownText(el: Element): string {
    let text = "";
    const walk = (node: Node) => {
        if (node.nodeType === 3) text += node.textContent;
        node.childNodes.forEach((child) => {
            if (
                child.nodeType === 1 &&
                (child as Element).matches(`${INTERACTIVE_SELECTOR}, [aria-hidden="true"]`)
            ) {
                return;
            }
            walk(child);
        });
    };
    walk(el);
    return normalize(text);
}

function describeElement(el: Element): string {
    const classes = el.classList.length ? "." + Array.prototype.join.call(el.classList, ".") : "";
    const text = normalize(el.textContent || "").slice(0, 40);
    return `<${el.tagName.toLowerCase()}${classes}> "${text}"`;
}

export function checkNoClickableText(selector = "main") {
    if (!isChrome()) return;
    cy.window().then((win) => {
        const targets = (win as unknown as { __clickListenerTargets?: EventTarget[] })
            .__clickListenerTargets;
        expect(targets, "click listener tracking (visit with onBeforeLoad: trackClickListeners)")
            .to.exist;
        cy.get(selector).then(($contexts) => {
            const contexts = $contexts.toArray();
            const withListeners = targets!.filter(
                (t): t is Element => t instanceof win.Element,
            );
            const inline = Array.prototype.slice.call(win.document.querySelectorAll("[onclick]"));
            // A listener on a wrapper around the context counts too; Chrome makes
            // everything inside it clickable. <html>/<body> listeners don't.
            const offenders = withListeners
                .concat(inline)
                .filter((el) => el !== win.document.documentElement && el !== win.document.body)
                .filter((el) => contexts.some((c) => c.contains(el) || el.contains(c)))
                .filter((el) => !el.matches(INTERACTIVE_SELECTOR) && ownText(el) !== "")
                .map(describeElement);
            expect(offenders, `non-interactive elements with click handlers in ${selector}`)
                .to.deep.equal([]);
        });
    });
}
