import type { SiteRule } from "../shared/types";

export const twitterRule: SiteRule = {
  id: "twitter",
  hostname: "x.com",
  label: "X / Twitter",
  settings: {
    hideForYou: { label: "Hide For You", description: "Hide the For You timeline tab/content.", defaultValue: true },
    hideTrends: { label: "Hide Trends", description: "Hide trending topics widgets.", defaultValue: true },
    hideSuggestions: { label: "Hide Suggested Users", description: "Hide who-to-follow and recommended users.", defaultValue: true },
    hideRecommendations: { label: "Hide Recommended Tweets", description: "Hide recommendation modules in timelines.", defaultValue: true },
  },
  shouldRun: (url) => url.hostname.endsWith("x.com") || url.hostname.endsWith("twitter.com"),
  hideSelectors: (_url, s) => [
    ...(s.hideForYou ? ["a[href='/home'][aria-selected='true']", "div[role='tablist'] a[href='/home']:first-child"] : []),
    ...(s.hideTrends ? ["[aria-label='Timeline: Trending now']", "[data-testid='trend']"] : []),
    ...(s.hideSuggestions ? ["[aria-label='Who to follow']", "[data-testid='UserCell']"] : []),
    ...(s.hideRecommendations ? ["[aria-label*='Recommended']", "[data-testid='placementTracking']"] : []),
  ],
  removeSelectors: () => [],
  observers: (url, settings) => twitterRule.hideSelectors(url, settings).map((selector) => ({ selector, action: "hide" })),
};
