export type SiteId = "youtube" | "reddit" | "twitter" | "linkedin";

export interface SiteSetting {
  label: string;
  description: string;
  defaultValue: boolean;
}

export type SiteSettings = Record<string, boolean>;

export interface ObserverRule {
  selector: string;
  action: "hide" | "remove";
  setting?: string;
}

export interface SiteRule {
  id: SiteId;
  hostname: string;
  label: string;
  settings: Record<string, SiteSetting>;
  shouldRun(url: URL): boolean;
  hideSelectors(url: URL, settings: SiteSettings): string[];
  removeSelectors(url: URL, settings: SiteSettings): string[];
  observers(url: URL, settings: SiteSettings): ObserverRule[];
}
