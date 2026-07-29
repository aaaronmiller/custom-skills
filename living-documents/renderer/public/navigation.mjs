export function sectionIdFromHash(hash, validSectionIds) {
  if (!hash) return null;
  try {
    const id = decodeURIComponent(hash.replace(/^#/, ''));
    return validSectionIds.includes(id) ? id : null;
  } catch {
    return null;
  }
}
