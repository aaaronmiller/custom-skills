export function sectionIdFromHash(hash, validSectionIds) {
  if (!hash) return null;
  try {
    const id = decodeURIComponent(hash.replace(/^#/, ''));
    return validSectionIds.includes(id) ? id : null;
  } catch {
    return null;
  }
}

export function viewIdFromHash(hash, validViewIds) {
  if (!hash?.startsWith('#view=')) return null;
  try {
    const id = decodeURIComponent(hash.slice('#view='.length));
    return validViewIds.includes(id) ? id : null;
  } catch {
    return null;
  }
}

export function projectRouteFromHash(hash, validSectionIds, defaultView = 'dashboard', validViewIds = []) {
  const sectionId = sectionIdFromHash(hash, validSectionIds);
  const viewId = viewIdFromHash(hash, validViewIds);
  return {
    view: sectionId ? 'section' : viewId || defaultView,
    sectionId,
  };
}
