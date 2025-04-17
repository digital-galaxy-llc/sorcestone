import unittest
from unittest.mock import Mock, patch
from sorcestone.main.iteration import Iteration


class TestIteration(unittest.TestCase):
    def setUp(self):
        """
        Set up test cases for Iteration class
        """
        self.initial_query = "Write a Python function to solve a problem"
        self.mock_llm_client = Mock()

    def test_init(self):
        """
        Test initialization of Iteration object
        """
        def mock_validation(result):
            return 0, ""

        iteration = Iteration(
            initial_query=self.initial_query, 
            validation_callback=mock_validation
        )
        
        self.assertEqual(iteration.initial_query, self.initial_query)
        self.assertEqual(iteration.log, [self.initial_query])
        self.assertIsNotNone(iteration.validation_callback)

    def test_validate_with_callback(self):
        """
        Test validation method with a callback
        """
        def mock_validation(result):
            return 1, "Needs improvement"

        iteration = Iteration(
            initial_query=self.initial_query, 
            validation_callback=mock_validation
        )
        
        return_code, return_message = iteration.validate("test result")
        
        self.assertEqual(return_code, 1)
        self.assertEqual(return_message, "Needs improvement")

    def test_validate_without_callback(self):
        """
        Test validation method without a callback
        """
        iteration = Iteration(initial_query=self.initial_query)
        
        return_code, return_message = iteration.validate("test result")
        
        self.assertEqual(return_code, 0)
        self.assertEqual(return_message, "")

    @patch('builtins.input', return_value="Looks good")
    def test_ask_feedback(self, mock_input):
        """
        Test ask_feedback method
        """
        iteration = Iteration(initial_query=self.initial_query)
        
        feedback = iteration.ask_feedback()
        
        self.assertEqual(feedback, "Looks good")
        mock_input.assert_called_once()

    @patch('builtins.input', return_value="")
    def test_run_method_with_successful_validation(self, mock_input):
        """
        Test run method with successful validation
        """
        # Setup mock LLM client to return a response
        self.mock_llm_client.send_message.return_value = "Python function solution"
        
        # Setup validation callback to return success
        def mock_validation(result):
            return 0, ""

        iteration = Iteration(
            initial_query=self.initial_query, 
            validation_callback=mock_validation
        )
        
        # Patch input to simulate no further feedback
        with patch.object(iteration, 'ask_feedback', return_value=""):
            # This would normally block, so we use a context manager to control input
            iteration.run(self.mock_llm_client)
        
        # Verify LLM client was called
        self.mock_llm_client.send_message.assert_called()

    @patch('builtins.input', return_value="Needs work")
    def test_run_method_with_multiple_iterations(self, mock_input):
        """
        Test run method with multiple iterations due to validation or feedback
        """
        # Setup mock LLM client to return responses
        self.mock_llm_client.send_message.side_effect = [
            "First attempt", 
            "Improved solution"
        ]
        
        # Setup validation callback to initially return failure, then success
        validation_calls = [
            (1, "Needs improvement"),
            (0, "")
        ]
        def mock_validation(result):
            return validation_calls.pop(0)

        iteration = Iteration(
            initial_query=self.initial_query, 
            validation_callback=mock_validation
        )
        
        # Patch input to simulate feedback
        with patch.object(iteration, 'ask_feedback', side_effect=["Needs work", ""]):
            # This would normally block, so we use a context manager to control input
            iteration.run(self.mock_llm_client)
        
        # Verify LLM client was called multiple times
        self.assertEqual(self.mock_llm_client.send_message.call_count, 2)

if __name__ == '__main__':
    unittest.main()
