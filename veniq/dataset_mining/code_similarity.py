from collections import defaultdict
from typing import List, Tuple

import textdistance


def is_similar_functions(
        file_before: str,
        file_after: str,
        ranges_list_before: List[List[int]],
        ranges_after: Tuple[int, int],
        res):
    d = defaultdict(set)
    before_lines_for_all_ranges = []
    exc = [' ', '{', '}', '']
    with open(file_before) as before:
        before_text = before.read().split('\n')
        with open(file_after) as after:
            after_text = after.read().split('\n')
            start_after, end_after = ranges_after
            # since the beginning in array start with 0 and we
            # do not need the function's name which is usually on the first line
            after_lines = after_text[start_after: end_after]
            for ranges_before in ranges_list_before:
                start_before, end_before = ranges_before
                # since the beginning in array start with 0
                before_lines = before_text[start_before - 1: end_before]
                before_lines_for_all_ranges.extend(before_lines)

                for iteration_i, i in enumerate(after_lines, start=start_before):
                    for iteration_j, j in enumerate(before_lines, start=start_after):
                        i = i.strip()
                        j = j.strip()
                        if (i != '') and (j != '') and (i not in exc) and (j not in exc):
                            longest_subs = textdistance.ratcliff_obershelp(i, j)
                            hamm = textdistance.hamming.normalized_similarity(i, j)
                            d[j].add((longest_subs, hamm, iteration_i, iteration_j, i))

        matched_strings_before: List[str] = []

        find_similar_strings(d, matched_strings_before, res)

    lines_number_of_function_before = 0
    for i in before_lines_for_all_ranges:
        if i.strip() not in exc:
            lines_number_of_function_before += 1

    if lines_number_of_function_before == 0:
        ratio = 0.0
    else:
        ratio = len(matched_strings_before) / float(lines_number_of_function_before)
    res.lines_number = lines_number_of_function_before
    res.lines_matched = len(matched_strings_before)
    res.matched_percent = ratio
    res.matched_strings = '\n'.join(matched_strings_before)

    if ratio > 0.699999:
        return True

    return False


def find_similar_strings(d, matched_strings_before, res):
    for string_before, lst in d.items():
        max_val = -1
        max_hamm = -1
        for subs_val, hamm, iterator_i, iteration_j, string_matched in lst:
            if max_val < subs_val:
                max_val = subs_val
                max_hamm = hamm

        if max_val > 0.7000000000000000000000000000000000000000001:
            if max_hamm > 0.4:
                matched_strings_before.append(string_before)
