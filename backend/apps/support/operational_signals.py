"""Conservative, privacy-preserving support issue clustering for the Admin Desk.
Signals are hints for human triage, not confirmed incidents. Only visible tickets
are passed in by the caller; this module never broadens reviewer scope.
"""
from collections import Counter, defaultdict
import re

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.IGNORECASE)
_NUMBER_RE = re.compile(r"\b\d+\b")
_WORD_RE = re.compile(r"[a-z]{3,}")

_STOP_WORDS = {
    "about", "after", "again", "also", "any", "are", "because", "been",
    "before", "being", "below", "between", "both", "but", "can", "cannot",
    "could", "did", "does", "doing", "down", "during", "each", "few",
    "for", "from", "further", "get", "got", "had", "has", "have", "having",
    "help", "here", "how", "into", "just", "like", "made", "make", "many",
    "may", "more", "most", "much", "must", "need", "not", "now", "once",
    "only", "other", "our", "out", "over", "please", "same", "should",
    "since", "some", "such", "than", "that", "the", "their", "them",
    "then", "there", "these", "they", "this", "those", "through", "too",
    "under", "until", "very", "was", "were", "what", "when", "where",
    "which", "while", "who", "will", "with", "would", "you", "your",
    "account", "customer", "dear", "hello", "issue", "member", "problem",
    "support", "thanks", "thesis", "trade", "unable",
}

def _ticket_terms(message):
    """Return a safe set of symptom words; never return the source message."""
    text = str(message or "").lower()
    text = _EMAIL_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    text = _UUID_RE.sub(" ", text)
    text = _NUMBER_RE.sub(" ", text)
    return {word for word in _WORD_RE.findall(text) if word not in _STOP_WORDS}


def build_support_issue_clusters(tickets, *, min_customers=3, min_tickets=3, similarity_threshold=0.45):
    """Cluster similar same-category messages; return safe terms, not ticket text.

    A signal is only a triage hint. The caller must pass a reviewer-scoped
    queryset; no member names, raw messages, emails, URLs or identifiers leave
    this service.
    """
    rows = list(tickets)
    terms = [_ticket_terms(ticket.message) for ticket in rows]
    parents = list(range(len(rows)))

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left, right):
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    for left in range(len(rows)):
        if len(terms[left]) < 3:
            continue
        for right in range(left + 1, len(rows)):
            if rows[left].category != rows[right].category or len(terms[right]) < 3:
                continue
            shared = terms[left] & terms[right]
            if len(shared) < 3:
                continue
            union_size = len(terms[left] | terms[right])
            similarity = len(shared) / union_size if union_size else 0
            if similarity >= similarity_threshold:
                union(left, right)

    components = defaultdict(list)
    for index, ticket in enumerate(rows):
        components[find(index)].append((ticket, terms[index]))

    signals = []
    for component in components.values():
        group = [ticket for ticket, _words in component]
        customers = {str(ticket.user_id) for ticket in group}
        if len(group) < min_tickets or len(customers) < min_customers:
            continue
        frequencies = Counter(word for _ticket, words in component for word in words)
        min_frequency = max(2, (len(group) + 1) // 2)
        common_terms = [word for word, count in frequencies.most_common() if count >= min_frequency][:4]
        newest_first = sorted(group, key=lambda ticket: ticket.created_at, reverse=True)
        signals.append({
            "category": newest_first[0].get_category_display(),
            "category_key": newest_first[0].category,
            "ticket_count": len(group),
            "customer_count": len(customers),
            "open_count": sum(ticket.status in ticket.ACTIVE_STATUSES for ticket in group),
            "urgent_count": sum(ticket.priority == ticket.Priority.URGENT for ticket in group),
            "terms": common_terms,
            "first_seen": min(ticket.created_at for ticket in group),
            "last_seen": max(ticket.created_at for ticket in group),
            "tickets": newest_first[:5],
        })
    return sorted(signals, key=lambda item: (item["customer_count"], item["ticket_count"], item["last_seen"]), reverse=True)