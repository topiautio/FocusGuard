import { siteRules } from "../rules";
import { loadSettings, saveSettings, type SettingsBySite } from "../shared/settings";

function requiredElement<T extends HTMLElement>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) {
    throw new Error(`Missing required options element: ${selector}`);
  }
  return element;
}

const form = requiredElement<HTMLFormElement>("#settings-form");
const statusElement = requiredElement<HTMLElement>("#status");

function render(settings: SettingsBySite): void {
  form.replaceChildren();

  for (const rule of siteRules) {
    const section = document.createElement("section");
    section.className = "site";

    const title = document.createElement("h2");
    title.textContent = rule.label;
    section.append(title);

    for (const [key, setting] of Object.entries(rule.settings)) {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.name = `${rule.id}.${key}`;
      input.checked = settings[rule.id][key] ?? setting.defaultValue;

      const text = document.createElement("span");
      text.textContent = setting.label;
      const description = document.createElement("small");
      description.textContent = setting.description;
      text.append(description);
      label.append(input, text);
      section.append(label);
    }

    form.append(section);
  }
}

function readForm(current: SettingsBySite): SettingsBySite {
  const next = structuredClone(current);
  for (const rule of siteRules) {
    for (const key of Object.keys(rule.settings)) {
      const input = form.elements.namedItem(`${rule.id}.${key}`) as HTMLInputElement | null;
      if (input) {
        next[rule.id][key] = input.checked;
      }
    }
  }
  return next;
}

async function main(): Promise<void> {
  let settings = await loadSettings(siteRules);
  render(settings);

  form.addEventListener("change", async () => {
    settings = readForm(settings);
    await saveSettings(settings);
    statusElement.textContent = "Settings saved. Refresh open site tabs to apply every option.";
  });
}

void main();
