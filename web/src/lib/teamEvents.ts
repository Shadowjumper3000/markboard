const TEAMS_UPDATED_EVENT = 'markboard:teams-updated';

export function emitTeamsUpdated() {
  if (typeof window === 'undefined') {
    return;
  }

  window.dispatchEvent(new Event(TEAMS_UPDATED_EVENT));
}

export function subscribeTeamsUpdated(listener: () => void) {
  if (typeof window === 'undefined') {
    return () => {};
  }

  const handler = () => listener();
  window.addEventListener(TEAMS_UPDATED_EVENT, handler);

  return () => {
    window.removeEventListener(TEAMS_UPDATED_EVENT, handler);
  };
}
