import type { SiteRule } from "../shared/types";

export const redditRule: SiteRule = {
  id: "reddit",
  hostname: "reddit.com",
  label: "Reddit",
  settings: {
    hideHome: { label: "Hide Home", description: "Hide the personalized home feed.", defaultValue: true },
    hidePopular: { label: "Hide Popular/All", description: "Hide broad algorithmic feeds.", defaultValue: true },
    hideSuggestions: { label: "Hide Suggestions", description: "Hide suggested communities, recommended posts, and trending units.", defaultValue: true },
    stopInfiniteScroll: { label: "Stop Infinite Scrolling", description: "Remove feed containers outside intentional subreddit, post, search, and saved pages.", defaultValue: true },
  },
  shouldRun: (url) => url.hostname.endsWith("reddit.com"),
  hideSelectors: (url, s) => [
    ...(s.hideHome && url.pathname === "/" ? ["main", "shreddit-feed"] : []),
    ...(s.hidePopular && /^\/(r\/popular|r\/all|popular|all)\b/.test(url.pathname) ? ["main", "shreddit-feed"] : []),
    ...(s.hideSuggestions ? ["[data-testid*='recommend']", "[aria-label*='Trending']", "[aria-label*='Suggested']", "reddit-sidebar-nav [href*='/r/popular']"] : []),
    ...(s.stopInfiniteScroll && /^\/$/.test(url.pathname) ? ["faceplate-batch", "shreddit-feed"] : []),
  ],
  removeSelectors: () => [],
  observers: (url, settings) => redditRule.hideSelectors(url, settings).map((selector) => ({ selector, action: "hide" })),
};
