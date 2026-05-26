const REJECT_PATTERNS = [
  /\b(u\.?s\.?\s*citizen(s|ship)?(\s+only)?)\b/i,
  /\b(must\s+be\s+(a\s+)?u\.?s\.?\s*citizen)\b/i,
  /\b(permanent\s+resident(s)?\s+only)\b/i,
  /\b(no\s+visa\s+sponsorship)\b/i,
  /\b(not?\s+sponsor)\b/i,
  /\b(unable\s+to\s+sponsor)\b/i,
  /\b(will\s+not\s+sponsor)\b/i,
  /\b(cannot\s+sponsor)\b/i,
  /\b(do(es)?\s+not\s+offer\s+sponsor(ship)?)\b/i,
  /\b(without\s+sponsorship)\b/i,
  /\b(clearance\s+required)\b/i,
  /\b(security\s+clearance)\b/i,
  /\b(must\s+be\s+authorized\s+to\s+work\s+in\s+the\s+u\.?s\.?\s+without\s+sponsor(ship)?)\b/i,
  /\b(not\s+eligible\s+for\s+visa\s+sponsorship)\b/i,
];

const POSITIVE_PATTERNS = [
  /\b(visa\s+sponsorship\s+(available|offered|provided|possible))\b/i,
  /\b(will(ing)?\s+to\s+sponsor)\b/i,
  /\b(h[- ]?1b\s+sponsor(ship)?)\b/i,
  /\b(sponsor\s+h[- ]?1b)\b/i,
  /\b(open\s+to\s+sponsor(ship|ing)?)\b/i,
  /\b(sponsorship\s+(is\s+)?available)\b/i,
];

export function classifyVisaSignal(jdText: string): "reject" | "positive" | "unknown" {
  if (!jdText) return "unknown";
  for (const pat of REJECT_PATTERNS) {
    if (pat.test(jdText)) return "reject";
  }
  for (const pat of POSITIVE_PATTERNS) {
    if (pat.test(jdText)) return "positive";
  }
  return "unknown";
}

export function shouldFilterOut(jdText: string, requireSponsorship = true): boolean {
  if (!requireSponsorship) return false;
  return classifyVisaSignal(jdText) === "reject";
}
