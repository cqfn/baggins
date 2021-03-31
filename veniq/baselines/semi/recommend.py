from typing import List, Tuple
from tempfile import NamedTemporaryFile
from functools import reduce
from operator import itemgetter
import os

from javalang.parser import JavaSyntaxError

from veniq.utils.ast_builder import build_ast
from veniq.ast_framework import AST, ASTNodeType
from veniq.baselines.semi.rank_extraction_opportunities import \
    rank_extraction_opportunities, ExtractionOpportunityGroup
from veniq.baselines.semi.create_extraction_opportunities import \
    create_extraction_opportunities
from veniq.baselines.semi.extract_semantic import \
    extract_method_statements_semantic
from veniq.baselines.semi.filter_extraction_opportunities import \
    filter_extraction_opportunities
from veniq.baselines.semi._common_types import ExtractionOpportunity,\
    OpportunityBenefit


EMORange = Tuple[int, int]


def _add_class_decl_wrap(method_decl: List[str]) -> List[str]:
    class_decl = ['class FakeClass {'] + method_decl + ['}']
    return class_decl


def _get_method_subtree(class_decl: List[str]) -> AST:
    with NamedTemporaryFile(delete=False) as f:
        _name = f.name
        f.write('\n'.join(class_decl).encode())
    try:
        javalang_ast = build_ast(_name)
        ast = AST.build_from_javalang(javalang_ast)
        os.unlink(_name)
    except JavaSyntaxError as e:
        os.unlink(_name)
        raise e

    class_node = list(ast.get_proxy_nodes(ASTNodeType.CLASS_DECLARATION))[0]
    objects_to_consider = list(class_node.methods) + \
        list(class_node.constructors)

    method_node = objects_to_consider[0]
    ast_subtree = ast.get_subtree(method_node)
    return ast_subtree


def _find_EMO_groups(method_subtree: AST) -> List[ExtractionOpportunityGroup]:
    statements_semantic = extract_method_statements_semantic(method_subtree)
    extraction_opportunities = create_extraction_opportunities(
        statements_semantic)
    filtered_extraction_opportunities = filter_extraction_opportunities(
        extraction_opportunities, statements_semantic, method_subtree)
    extraction_opportunities_groups = rank_extraction_opportunities(
        statements_semantic, filtered_extraction_opportunities
    )

    return extraction_opportunities_groups


def _find_closing_brackets(extraction_till_end: List[str], num_extr_lines_orig: int) -> int:
    if num_extr_lines_orig == 0 or extraction_till_end == []:
        return 0

    bracket_balance = 0
    for i, x in enumerate(extraction_till_end):
        open_brackets = x.count('{')
        bracket_balance += open_brackets
        closing_brackets = x.count('}')
        bracket_balance -= closing_brackets
        if i >= num_extr_lines_orig - 1:
            if bracket_balance <= 0:
                break
    return i


def _convert_ExtractionOpportunity_to_EMO(
        extr_opport: ExtractionOpportunity, class_decl: List[str]) -> EMORange:
    ''' Converts extraction opportunity of type ExtractionOpportunity from
    veniq.baselines.semi._common_types to type EMO defined here.
    '''
    lines = [node.line for node in extr_opport]
    # subtract 1 because we count from 0
    start_line_opportunity = min(lines) - 1
    end_line_opportunity = max(lines) - 1
    extraction = class_decl[start_line_opportunity:]
    extraction_lines_number = end_line_opportunity - start_line_opportunity + 1

    # additional procedure to find closing brackets
    addit_lines_brackets = _find_closing_brackets(extraction, extraction_lines_number)

    return (start_line_opportunity, start_line_opportunity + addit_lines_brackets)


def recommend_for_method(method_decl_lines: List[str]) -> List[EMORange]:
    '''
    Takes method declaration in form of a list of strings,
    outputs list of EMORanges in the order of decreasing recommendation.
    EMORange is a (start_line_extraction, end_line_extraction)
    (the range is inclusive).
    '''
    class_decl_fake = _add_class_decl_wrap(method_decl_lines)
    try:
        method_subtree = _get_method_subtree(class_decl_fake)
    except JavaSyntaxError as e:
        raise e
    emo_groups_semi = _find_EMO_groups(method_subtree)
    if emo_groups_semi is None or emo_groups_semi == []:
        return []

    all_opportunities_semi: List[Tuple[ExtractionOpportunity, OpportunityBenefit]] = \
        reduce(lambda x, y: x + list(y.opportunities), emo_groups_semi, [])

    all_opportunities_semi_ranked = sorted(all_opportunities_semi, key=itemgetter(1),
                                           reverse=True)
    emo_ranges_ranked = [_convert_ExtractionOpportunity_to_EMO(
        x[0], class_decl_fake) for x in all_opportunities_semi_ranked]

    # subtract 1 because we added fake class declaration line
    emo_ranges_ranked = [(x[0] - 1, x[1] - 1) for x in emo_ranges_ranked]
    return emo_ranges_ranked
