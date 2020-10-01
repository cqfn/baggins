from typing import List, Optional, Union

from veniq.ast_framework import AST, ASTNode
from veniq.ast_framework.block_statement_graph import Block, Statement, build_block_statement_graph


ExtractionOpportunity = List[ASTNode]


def filter_extraction_opportunities(
    extraction_opportunities: List[ExtractionOpportunity], method_ast: AST
) -> List[ExtractionOpportunity]:
    block_statement_graph = build_block_statement_graph(method_ast)
    extraction_opportunities = list(
        filter(
            lambda extraction_opportunity: _syntactic_filter(extraction_opportunity, block_statement_graph),
            extraction_opportunities,
        )
    )
    return extraction_opportunities


def _syntactic_filter(statements: ExtractionOpportunity, method_block_statement_graph: Block) -> bool:
    syntacticFilterCallbacks = SyntacticFilterCallbacks(statements, method_block_statement_graph)
    method_block_statement_graph.traverse(
        syntacticFilterCallbacks.on_node_entering, syntacticFilterCallbacks.on_node_leaving
    )
    return syntacticFilterCallbacks.is_statements_extractable


class SyntacticFilterCallbacks:
    def __init__(self, statements: List[ASTNode], root_block: Block):
        self._blocks_stack: List[Block] = [root_block]
        self._parent_block: Optional[Block] = None

        self._is_traversing_high_level_statement = False
        self._high_level_statement: Optional[Statement] = None

        self._next_statement_index = 0
        self._statements = statements

        self._is_statements_extractable = True

    @property
    def is_statements_extractable(self):
        return self._is_statements_extractable

    def on_node_entering(self, node: Union[Block, Statement]) -> None:
        if isinstance(node, Block):
            self._on_block_entering(node)
        elif isinstance(node, Statement):
            self._on_statement_entering(node)
        else:
            raise ValueError(f"Unknown node {node}")

    def on_node_leaving(self, node: Union[Block, Statement]) -> None:
        if isinstance(node, Block):
            self._on_block_leaving(node)
        elif isinstance(node, Statement):
            self._on_statement_leaving(node)
        else:
            raise ValueError(f"Unknown node {node}")

    def _on_block_entering(self, block: Block) -> None:
        self._blocks_stack.append(block)

    def _on_statement_entering(self, statement: Statement) -> None:
        if not self._is_all_statements_found() and \
           statement.node == self._statements[self._next_statement_index]:
            if self._is_none_statements_found():
                self._parent_block = self._current_block

            if self._current_block == self._parent_block:
                self._is_traversing_high_level_statement = True
                self._high_level_statement = statement

            self._next_statement_index += 1
        else:
            if self._is_traversing_high_level_statement:
                self._is_statements_extractable = False
            elif self._current_block == self._parent_block and not self._is_all_statements_found():
                self._is_statements_extractable = False

    def _on_block_leaving(self, block: Block) -> None:
        self._blocks_stack.pop()

    def _on_statement_leaving(self, statement: Statement) -> None:
        if self._high_level_statement == statement:
            self._is_traversing_high_level_statement = False
            self._high_level_statement = None

    def _is_all_statements_found(self) -> bool:
        return self._next_statement_index == len(self._statements)

    def _is_none_statements_found(self) -> bool:
        return self._next_statement_index == 0

    def _is_some_statements_found(self) -> bool:
        return 0 < self._next_statement_index < len(self._statements)

    @property
    def _current_block(self) -> Block:
        try:
            return self._blocks_stack[-1]
        except KeyError:
            raise RuntimeError("Quering current block without observing any block yet.")
