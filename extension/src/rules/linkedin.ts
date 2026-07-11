import type { SiteRule } from "../shared/types";

export const linkedinRule: SiteRule = {
  id: "linkedin",
  hostname: "linkedin.com",
  label: "LinkedIn",
  settings: {
    hideMainFeed: { label: "Hide Main Feed", description: "Hide the LinkedIn homepage feed.", defaultValue: true },
    hideSuggestedPosts: { label: "Hide Suggested Posts", description: "Hide promoted/suggested feed posts.", defaultValue: true },
    hideSuggestedPeople: { label: "Hide Suggested People", description: "Hide people-you-may-know modules.", defaultValue: true },
    hideNews: { label: "Hide News Widgets", description: "Hide LinkedIn News and sidebar headlines.", defaultValue: true },
  },
  shouldRun: (url) => url.hostname.endsWith("linkedin.com"),
  hideSelectors: (url, s) => [
    ...(s.hideMainFeed && /^\/feed\/?$/.test(url.pathname) ? ["main.scaffold-layout__main", ".scaffold-finite-scroll"] : []),
    ...(s.hideSuggestedPosts ? ["[data-id*='suggested']", ".feed-shared-update-v2--minimal-padding"] : []),
    ...(s.hideSuggestedPeople ? [".pymk-card", "[aria-label*='People you may know']"] : []),
    ...(s.hideNews ? [".news-module", ".feed-follows-module", "aside .artdeco-card"] : []),
  ],
  removeSelectors: () => [],
  observers: (url, settings) => linkedinRule.hideSelectors(url, settings).map((selector) => ({ selector, action: "hide" })),
};
