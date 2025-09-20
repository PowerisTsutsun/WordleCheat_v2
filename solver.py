# solver.py
from typing import List, Set, Tuple

def filter_words(
    words: List[str],
    tried_words: Set[str],
    known_word: list,
    absent_letters: Set[str],
    present_letters: Set[str],
    yellow_positions: Set[Tuple[str, int]],
) -> List[str]:
    """Return valid candidate words given current constraints."""
    valid = []
    for w in words:
        if w in tried_words:
            continue

        ok = True
        # greens
        for i, g in enumerate(known_word):
            if g and w[i] != g:
                ok = False
                break
        if not ok:
            continue

        # grays
        if any(ch in absent_letters for ch in w):
            continue

        # yellows (present letters and not in forbidden positions)
        for letter in present_letters:
            if letter not in w:
                ok = False
                break
            for idx, ch in enumerate(w):
                if ch == letter and (letter, idx) in yellow_positions:
                    ok = False
                    break
            if not ok:
                break

        if ok:
            valid.append(w)

    return valid
