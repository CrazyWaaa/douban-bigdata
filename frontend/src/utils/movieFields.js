const PERSON_SUFFIX = /\s+[A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]*)*$/

export function splitMultiValue(value) {
  if (!value) return []
  const source = String(value).trim()
  const parts = source.includes('/')
    ? source.split(/\s*\/\s*/)
    : source.split(/\s+/)
  return [...new Set(parts.map((part) => part.trim()).filter(Boolean))]
}

export function splitPeople(value) {
  if (!value) return []
  return [...new Set(
    String(value)
      .split(/\s*\/\s*/)
      .map((part) => part.replace(PERSON_SUFFIX, '').trim())
      .filter(Boolean),
  )]
}

export function releaseMonth(value) {
  const match = String(value || '').match(/(?:^|[-/.年])(0?[1-9]|1[0-2])(?:[-/.月]|$)/)
  return match ? Number(match[1]) : null
}