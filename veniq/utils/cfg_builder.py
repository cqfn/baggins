from networkx import DiGraph, disjoint_union  # type: ignore
from veniq.ast_framework import AST, ASTNodeType
from typing import Tuple


NODE_TYPES = [
    ASTNodeType.ASSIGNMENT,
    ASTNodeType.RETURN_STATEMENT
]


def build_cfg(tree: AST) -> DiGraph:
    '''Create Control Flow Graph'''
    g = DiGraph()
    g.add_node(0)
    for node in tree:
        if node.node_type not in NODE_TYPES:
            continue
        _g = _mk_cfg_graph(node.node_type)
        g = _compose_two_graphs(g, _g)
    return g


def _mk_cfg_graph(node: ASTNodeType) -> Tuple[DiGraph, int]:
    '''Takes in Javalang statement and returns corresponding CFG'''
    g = DiGraph()
    g.add_node(0)
    return g


def _compose_two_graphs(g1: DiGraph, g2: DiGraph) -> DiGraph:
    '''Compose two graphs by creating the edge between last of the fist graph and fist of the second.
       We assume that node in the each graph G has order from 0 to len(G)-1
    '''
    g = disjoint_union(g1, g2)
    g.add_edge(len(g1) - 1, len(g1))
    return g
