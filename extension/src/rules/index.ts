import type { SiteRule } from "../shared/types";
import { linkedinRule } from "./linkedin";
import { redditRule } from "./reddit";
import { twitterRule } from "./twitter";
import { youtubeRule } from "./youtube";

export const siteRules: SiteRule[] = [youtubeRule, redditRule, twitterRule, linkedinRule];

export function matchingRule(url: URL): SiteRule | undefined {
  return siteRules.find((rule) => rule.shouldRun(url));
}
