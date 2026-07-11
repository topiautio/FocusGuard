import type { SiteRule, SiteSettings } from "../shared/types";

const watchLikePages = /^\/(watch|embed|shorts)\b/;
const intentionalPages = /^\/(results|playlist|channel|c|@|feed\/subscriptions|feed\/history|feed\/you|library)\b/;

function isHome(url: URL): boolean {
  return url.pathname === "/";
}

function selectors(settings: SiteSettings): string[] {
  return [
    ...(settings.hideHomeFeed ? ["ytd-browse[page-subtype='home'] #contents", "ytd-rich-grid-renderer"] : []),
    ...(settings.hideRecommendations ? ["ytd-watch-next-secondary-results-renderer", "ytd-compact-video-renderer", "ytd-rich-shelf-renderer"] : []),
    ...(settings.hideUpNext ? ["#related", ".ytp-endscreen-content", ".ytp-ce-element"] : []),
    ...(settings.hideShorts ? ["ytd-reel-shelf-renderer", "ytd-guide-entry-renderer a[title='Shorts']", "a[title='Shorts']"] : []),
    ...(settings.hideComments ? ["ytd-comments", "#comments"] : []),
    ...(settings.hideLiveChat ? ["ytd-live-chat-frame", "#chat"] : []),
    ...(settings.hideCounts ? ["#info #count", "#segmented-like-button", "#owner-sub-count"] : []),
  ];
}

export const youtubeRule: SiteRule = {
  id: "youtube",
  hostname: "youtube.com",
  label: "YouTube",
  settings: {
    hideHomeFeed: { label: "Hide Home Feed", description: "Remove YouTube's algorithmic landing feed.", defaultValue: true },
    hideShorts: { label: "Hide Shorts", description: "Hide Shorts shelves and navigation entry points.", defaultValue: true },
    hideRecommendations: { label: "Hide Recommendations", description: "Hide recommended videos and sidebar suggestions.", defaultValue: true },
    hideUpNext: { label: "Hide Up Next", description: "Hide autoplay/up-next and end-screen recommendations.", defaultValue: true },
    hideComments: { label: "Hide Comments", description: "Optionally hide comments on watch pages.", defaultValue: false },
    hideLiveChat: { label: "Hide Live Chat", description: "Optionally hide live chat panes.", defaultValue: false },
    hideCounts: { label: "Hide Like/View Counts", description: "Optionally hide engagement counters.", defaultValue: false },
  },
  shouldRun: (url) => url.hostname.endsWith("youtube.com") && (isHome(url) || intentionalPages.test(url.pathname) || watchLikePages.test(url.pathname)),
  hideSelectors: (_url, settings) => selectors(settings),
  removeSelectors: () => [],
  observers: (_url, settings) => selectors(settings).map((selector) => ({ selector, action: "hide" })),
};
