const SELECTED_FACTORY_KEY = "selected_factory_id";

export function getSelectedFactoryId(): string | null {
  return localStorage.getItem(SELECTED_FACTORY_KEY);
}

export function setSelectedFactoryId(factoryId: string): void {
  localStorage.setItem(SELECTED_FACTORY_KEY, factoryId);
}
