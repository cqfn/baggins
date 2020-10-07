import tempfile
from pathlib import Path
from unittest import TestCase

from veniq.dataset_collection.augmentation import determine_algorithm_insertion_type, analyze_file, _method_body_lines, \
    _is_match_to_the_conditions
from veniq.ast_framework import AST, ASTNodeType
from veniq.dataset_collection.types_identifier import (
    InlineTypesAlgorithms, InlineWithoutReturnWithoutArguments, InlineWithReturnWithoutArguments)
from veniq.utils.ast_builder import build_ast


class TestDatasetCollection(TestCase):
    current_directory = Path(__file__).absolute().parent

    def test_determine_type_without_return_without_arguments(self):
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'method'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'method_without_params'][0]
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'method_without_params'][0]
        d = {'method_without_params': [m_decl_original]}
        type = determine_algorithm_insertion_type(ast, m_decl, m_inv, d)
        self.assertEqual(type, InlineTypesAlgorithms.WITHOUT_RETURN_WITHOUT_ARGUMENTS)

    def test_determine_type_with_return_without_parameters(self):
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'reset_return_var_decl'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'closeServer_return'][0]
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'closeServer_return'][0]
        d = {'closeServer_return': [m_decl_original]}
        type = determine_algorithm_insertion_type(ast, m_decl, m_inv, d)
        self.assertEqual(type, InlineTypesAlgorithms.WITH_RETURN_WITHOUT_ARGUMENTS)

    def test_determine_type_with_parameters(self):
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'some_method'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'method_with_parameters'][0]
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'method_with_parameters'][0]
        d = {'method_with_parameters': [m_decl_original]}
        type = determine_algorithm_insertion_type(ast, m_decl, m_inv, d)
        self.assertEqual(type, InlineTypesAlgorithms.DO_NOTHING)

    def test_determine_type_with_overridden_functions(self):
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'invoke_overridden'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'overridden_func']
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'overridden_func'][0]
        d = {'overridden_func': m_decl_original}
        type = determine_algorithm_insertion_type(ast, m_decl, m_inv, d)
        self.assertEqual(type, InlineTypesAlgorithms.DO_NOTHING)

    def test_determine_type_with_invalid_functions(self):
        """Tests if we have invocation,
        but we didn't find it in the list of method declarations
        in current class."""
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'invoke_overridden'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'overridden_func']
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'overridden_func'][0]
        d = {'SOME_RANDOM_NAME': m_decl_original}
        type = determine_algorithm_insertion_type(ast, m_decl, m_inv, d)
        self.assertEqual(type, InlineTypesAlgorithms.DO_NOTHING)

    def test_determine_type_without_variables_declaration(self):
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'method'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'method_without_params'][0]
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'method_without_params'][0]
        d = {'method_without_params': [m_decl_original]}
        type = determine_algorithm_insertion_type(ast, m_decl, m_inv, d)
        self.assertEqual(type, InlineTypesAlgorithms.WITHOUT_RETURN_WITHOUT_ARGUMENTS)

        # We consider all cases (with or without return)
        # if there are no variables, declared in invoked function

        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'method_with_return_not_var_decl'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'closeServer_return'][0]
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'closeServer_return'][0]
        d = {'closeServer_return': [m_decl_original]}
        type = determine_algorithm_insertion_type(ast, m_decl, m_inv, d)

        self.assertEqual(type, InlineTypesAlgorithms.WITH_RETURN_WITHOUT_ARGUMENTS)

    def test_is_invocation_in_if_with_single_statement_valid(self):
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'test_single_stat_in_if'][0]
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'intersected_var'][0]

        self.assertFalse(_is_match_to_the_conditions(m_inv))

    def test_is_return_type_not_assigning_value_valid(self):
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'method_decl'][0]
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'invocation'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'invocation'][0]
        self.assertFalse(_is_match_to_the_conditions(m_inv, m_decl_original))

    def test_determine_type_with_non_intersected_variables_declaration(self):
        filepath = self.current_directory / "Example.java"
        ast = AST.build_from_javalang(build_ast(filepath))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'test_not_intersected_var_decl'][0]
        m_decl_original = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'intersected_var'][0]
        m_inv = [
            x for x in ast.get_subtree(m_decl).get_proxy_nodes(ASTNodeType.METHOD_INVOCATION)
            if x.member == 'intersected_var'][0]
        d = {'intersected_var': [m_decl_original]}
        type = determine_algorithm_insertion_type(ast, m_decl, m_inv, d)
        self.assertTrue(type in [
            InlineTypesAlgorithms.WITH_RETURN_WITHOUT_ARGUMENTS,
            InlineTypesAlgorithms.WITHOUT_RETURN_WITHOUT_ARGUMENTS])

    def test_inline_with_return_type_but_not_returning(self):
        """
        Test check whether we can inline code function with return type, but actually
        this function is not saving return value,
        so we do not need to declare a variable

        """
        algorithm = InlineWithReturnWithoutArguments()
        file = self.current_directory / 'InlineExamples' / 'ReturnTypeUseless.java'
        temp_filename = self.current_directory / 'temp.java'
        test_example = self.current_directory / 'InlineTestExamples' / 'ReturnTypeUseless.java'
        ast = AST.build_from_javalang(build_ast(file))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'invocation'][0]
        body_start_line, body_end_line = _method_body_lines(m_decl, file)

        algorithm.inline_function(file, 36, body_start_line, body_end_line, temp_filename)
        with open(temp_filename, encoding='utf-8') as actual_file, \
                open(test_example, encoding='utf-8') as test_ex:
            self.assertEqual(actual_file.read(), test_ex.read())
        temp_filename.unlink()

    def test_inline_with_return_type(self):
        algorithm = InlineWithReturnWithoutArguments()
        file = self.current_directory / 'InlineExamples' / 'ReaderHandler.java'
        temp_filename = self.current_directory / 'temp.java'
        test_example = self.current_directory / 'InlineTestExamples' / 'ReaderHandler.java'
        ast = AST.build_from_javalang(build_ast(file))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'getReceiverQueueSize'][0]
        body_start_line, body_end_line = _method_body_lines(m_decl, file)

        algorithm.inline_function(file, 76, body_start_line, body_end_line, temp_filename)
        with open(temp_filename, encoding='utf-8') as actual_file, \
                open(test_example, encoding='utf-8') as test_ex:
            self.assertEqual(test_ex.read(), actual_file.read())
        temp_filename.unlink()

    def test_inline_without_return_type(self):
        algorithm = InlineWithoutReturnWithoutArguments()
        file = self.current_directory / 'InlineExamples' / 'PlanetDialog.java'
        temp_filename = self.current_directory / 'temp.java'
        test_example = self.current_directory / 'InlineTestExamples' / 'PlanetDialog.java'
        ast = AST.build_from_javalang(build_ast(file))
        m_decl = [
            x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION)
            if x.name == 'makeBloom'][0]
        body_start_line, body_end_line = _method_body_lines(m_decl, file)

        algorithm.inline_function(file, 70, body_start_line, body_end_line, temp_filename)
        with open(temp_filename, encoding='utf-8') as actual_file, \
                open(test_example, encoding='utf-8') as test_ex:
            self.assertEqual(actual_file.read(), test_ex.read())
        temp_filename.unlink()
