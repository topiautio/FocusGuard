import { matchingRule } from "./rules";
import { loadSettings } from "./shared/settings";
import type { ObserverRule, SiteRule, SiteSettings } from "./shared/types";

const STYLE_ID = "focusguard-distraction-free-style";
const HIDDEN_ATTRIBUTE = "data-focusguard-hidden";

let observer: MutationObserver | undefined;
let activeUrl = "";
let scheduled = false;

function cssFor(selectors: string[]): string {
  if (selectors.length === 0) {
    return "";
  }
  return `${selectors.join(",\n")} { display: none !important; }`;
}

function injectCss(selectors: string[]): void {
  const css = cssFor(selectors);
  let style = document.getElementById(STYLE_ID) as HTMLStyleElement | null;
  if (!style) {
    style = document.createElement("style");
    style.id = STYLE_ID;
    style.dataset.focusguard = "true";
    (document.head ?? document.documentElement).append(style);
  }
  if (style.textContent !== css) {
    style.textContent = css;
  }
}

function applyObserverRule(rule: ObserverRule, root: ParentNode = document): void {
  for (const element of root.querySelectorAll<HTMLElement>(rule.selector)) {
    if (rule.action === "remove") {
      element.remove();
    } else {
      element.setAttribute(HIDDEN_ATTRIBUTE, "true");
      element.style.setProperty("display", "none", "important");
    }
  }
}

function applyRules(siteRule: SiteRule, url: URL, settings: SiteSettings): void {
  injectCss(siteRule.hideSelectors(url, settings));
  for (const selector of siteRule.removeSelectors(url, settings)) {
    for (const element of document.querySelectorAll(selector)) {
      element.remove();
    }
  }
  for (const rule of siteRule.observers(url, settings)) {
    applyObserverRule(rule);
  }
}

function scheduleApply(siteRule: SiteRule, url: URL, settings: SiteSettings): void {
  if (scheduled) {
    return;
  }
  scheduled = true;
  queueMicrotask(() => {
    scheduled = false;
    applyRules(siteRule, url, settings);
  });
}

function startObserver(siteRule: SiteRule, url: URL, settings: SiteSettings): void {
  observer?.disconnect();
  observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.addedNodes.length > 0) {
        scheduleApply(siteRule, url, settings);
        return;
      }
    }
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });
}

async function run(): Promise<void> {
  const url = new URL(location.href);
  if (url.href === activeUrl) {
    return;
  }
  activeUrl = url.href;

  const siteRule = matchingRule(url);
  if (!siteRule) {
    observer?.disconnect();
    injectCss([]);
    return;
  }

  const settings = (await loadSettings([siteRule]))[siteRule.id];
  applyRules(siteRule, url, settings);
  startObserver(siteRule, url, settings);
}

function hookHistory(method: "pushState" | "replaceState"): void {
  const original = history[method];
  history[method] = function patchedHistoryMethod(...args) {
    const result = original.apply(this, args);
    void run();
    return result;
  };
}

hookHistory("pushState");
hookHistory("replaceState");
window.addEventListener("popstate", () => void run());
document.addEventListener("DOMContentLoaded", () => void run(), { once: true });
void run();
