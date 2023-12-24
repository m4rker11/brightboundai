import unittest
import json
import AI.summarize as sm
import AI.emailWriter as ew

class TestSummarize(unittest.TestCase):
    def setUp(self):
        self.content = "Test content"
        self.context = "Test context"
        self.name = "Test Name"
        self.company = "Test Company"
        self.linkedin_summary = "Test LinkedIn Summary"
        self.website_content = "Test Website Content"
        self.product_context = "Test Product Context"
        self.outputFormat = {
            "personalization": "Test Personalization",
            "body": "Test Body"
        }
        self.profile = "Test profile"

    def test_summarizeWebsiteContent(self):
        json_result = sm.summarizeWebsiteContent(self.content, self.context)
        
        # Check if the result is a string
        self.assertIsInstance(json_result, dict)
        
        # Check if the JSON has the required fields
        self.assertIn("summary", json_result)
        self.assertIn("icp", json_result)
        self.assertIn("offer", json_result)

    def test_summarizeProfileData(self):
        result = sm.summarizeProfileData(self.profile)
        
        # Check if the result is a string
        self.assertIsInstance(result, str)
        
        # Check if the result is no more than 200 words
        self.assertLessEqual(len(result.split()), 220)

    def test_writeEmail(self):
        result = ew.writeEmail(self.name, self.company, self.linkedin_summary, self.website_content, self.product_context, self.outputFormat)
        # Check if the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check if the result has the required fields
        self.assertIn("personalization", result)
        self.assertIn("body", result)

        # Check if the body is less than 100 words
        self.assertLessEqual(len(result["body"].split()), 100)

if __name__ == '__main__':
    unittest.main()