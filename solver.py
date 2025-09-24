# solver.py
from typing import List, Set, Tuple, Dict  # Chun : Dict added for exact letter counts

def filter_words(
    words: List[str],
    tried_words: Set[str],
    known_word: list,
    absent_letters: Set[str],
    present_letters: Set[str],
    yellow_positions: Set[Tuple[str, int]],
    exact_counts: Dict[str, int],
) -> List[str]:
    """Return valid candidate words given current constraints."""
    # Chun : reworked yellow/gray logic and added duplicate-letter handling.
    valid = []
    for w in words:
        if w in tried_words:
            continue

        ok = True

        # Greens: fixed letters must match known positions
        for i, g in enumerate(known_word):
            if g and w[i] != g:
                ok = False
                break
        if not ok:
            continue

        # Present letters: every present letter must occur somewhere
        for letter in present_letters:
            if letter not in w:
                ok = False
                break
        if not ok:
            continue

        # Yellow positions: letter must NOT be in these forbidden indices
        for (letter, forbidden_idx) in yellow_positions:
            if w[forbidden_idx] == letter:
                ok = False
                break
        if not ok:
            continue

        # Chun : enforce exact counts when feedback says letter appears fewer times than guessed
        for letter, count in exact_counts.items():
            if w.count(letter) != count:
                ok = False
                break
        if not ok:
            continue

        # Absent letters are truly absent (GUI only adds letters that have zero colored hits)
        for letter in absent_letters:
            if letter in exact_counts:
                continue  # exact count constraint is more specific; skip raw-absent rule here
            if letter in w:
                ok = False
                break

        if ok:
            valid.append(w)

    return valid
