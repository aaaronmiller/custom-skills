export function sectionIdFromHash(hash, validSectionIds) {
  if (!hash) return null;
  try {
    const id = decodeURIComponent(hash.replace(/^#/, ''));
    return validSectionIds.includes(id) ? id : null;
  } catch {
    return null;
  }
}

export function projectRouteFromHash(hash, validSectionIds, defaultView = 'dashboard') {
  const sectionId = sectionIdFromHash(hash, validSectionIds);
  return {
    view: sectionId ? 'section' : defaultView,
    sectionId,
  };
}
