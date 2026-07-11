import type { SiteId, SiteRule, SiteSettings } from "./types";

export type SettingsBySite = Record<SiteId, SiteSettings>;

declare global {
  var chrome: {
  storage?: {
    sync?: {
      get(keys?: string | string[] | Record<string, unknown> | null): Promise<Record<string, unknown>>;
      set(items: Record<string, unknown>): Promise<void>;
    };
  };
  } | undefined;
}

const STORAGE_KEY = "focusguardSettings";

export function defaultsForRule(rule: SiteRule): SiteSettings {
  return Object.fromEntries(
    Object.entries(rule.settings).map(([key, setting]) => [key, setting.defaultValue]),
  );
}

export function defaultsForRules(rules: SiteRule[]): SettingsBySite {
  return Object.fromEntries(
    rules.map((rule) => [rule.id, defaultsForRule(rule)]),
  ) as SettingsBySite;
}

export function mergeSettings(rules: SiteRule[], stored: unknown): SettingsBySite {
  const defaults = defaultsForRules(rules);
  if (!stored || typeof stored !== "object") {
    return defaults;
  }

  const raw = stored as Partial<Record<SiteId, Record<string, unknown>>>;
  for (const rule of rules) {
    const siteSettings = raw[rule.id];
    if (!siteSettings || typeof siteSettings !== "object") {
      continue;
    }

    for (const key of Object.keys(rule.settings)) {
      if (typeof siteSettings[key] === "boolean") {
        defaults[rule.id][key] = siteSettings[key];
      }
    }
  }

  return defaults;
}

export async function loadSettings(rules: SiteRule[]): Promise<SettingsBySite> {
  const storage = globalThis.chrome?.storage?.sync;
  if (!storage) {
    return defaultsForRules(rules);
  }

  const values = await storage.get(STORAGE_KEY);
  return mergeSettings(rules, values[STORAGE_KEY]);
}

export async function saveSettings(settings: SettingsBySite): Promise<void> {
  const storage = globalThis.chrome?.storage?.sync;
  if (!storage) {
    return;
  }
  await storage.set({ [STORAGE_KEY]: settings });
}
