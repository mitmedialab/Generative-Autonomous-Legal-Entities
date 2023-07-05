Code Intepreter Notes - July 4th, 2023


## LLM.LLC Project Review with Code Intepreter

Project: https://github.com/mitmedialab/Generative-Autonomous-Legal-Entities

Direct chat transcript: https://chat.openai.com/share/8376e070-4699-4e88-9786-5405ab58f7dc 

Cached Transcript: https://github.com/mitmedialab/Generative-Autonomous-Legal-Entities/blob/main/Resources/Z_CI_PNG-30_Transcript.png 


## Code Inserts:

The cached transcript does not display the full embedded code snippets, which are included below, with excerpts from the Code Intepreter outputs each snippet was part of.

### 1 In the bot.py script...

In the bot.py script, it appears that the bot asks for human approval when it decides to perform an action, but only if the confirm attribute of the DecisionAct payload is set to True.

This is determined in the _route_message method of the LLMLLCBot class. If the decision is Decision.ACT (i.e., to perform an action) and the confirm attribute of the payload is True, then the bot sends a message asking for confirmation before proceeding with the action.



if payload.confirm:
    msg = f"""Could you confirm that I should take the following action?\\n---\\n{type(payload.action).__name__}\\n\\n```json\\n{json.dumps(payload.action.dict(), indent=2)}\\n```\\n"""
    await payload.thread.send(msg[:2000])
    self.append_history(t.id, "assistant", msg)
    self.thread_states[t.id] = ThreadStateAwaitingConfirm(action=payload.action)


### 2 Absolutely, I'd be glad to help you start with automated testing...

Absolutely, I'd be glad to help you start with automated testing. In Python, a commonly used library for creating automated tests is unittest. This library allows you to create test cases, assert the behavior of your code, and automatically run many tests at once.

Here's a high-level process of how you might structure automated tests for each of the rules. Note that the specific implementation will depend heavily on the details of your bot's functionality and the interfaces it provides.

Create a test module: This will be a separate Python file where you'll define your tests. Let's call it test_bot.py.

Import necessary modules: At the beginning of test_bot.py, you'll need to import unittest and the modules containing the functionality you want to test.

Define a test case class: Create a new class that inherits from unittest.TestCase in the test_bot.py file. This class will contain methods that define individual tests.

Define test methods: Inside the test case class, define a method for each test you want to run. Each method should represent a separate test, such as testing a specific rule. The method should set up any necessary preconditions, execute the behavior you want to test, and then use assert statements to verify that the behavior was as expected.

Run the tests: You can run the tests by calling unittest.main() in your script, or by using a Python test runner tool like nose or pytest.

Here's a very simple example of what the test_bot.py file might look like:

import unittest
from llmllc import LLMLLCBot  # assuming this is how you import your bot

class TestLLMLLCBot(unittest.TestCase):
    def setUp(self):
        self.bot = LLMLLCBot()  # assuming your bot has a no-argument constructor

    def test_fiduciary_duties(self):
        # Set up the test
        self.bot.set_scenario('test_scenario_1')  # assuming you have a way to set up a scenario

        # Execute the behavior to test
        decision = self.bot.make_decision()  # assuming your bot has a method like this

        # Assert the expected outcome
        self.assertEqual(decision, 'LLC_interest', 'The bot should always choose LLC_interest')

    # Define more tests here...

if __name__ == '__main__':
    unittest.main()


### 3 Sure! Let's dive in...the bot.py file where improvements could be made...

Sure! Let's dive in. For the sake of brevity, I'll focus on a few key areas of the bot.py file where improvements could be made.

Error Handling: It's crucial to have robust error handling in any application, especially one that is meant to interact with users and handle sensitive tasks like managing an LLC.

In your current code, there are places where the bot makes calls to external services, such as sending emails or interacting with the Discord API, but there are no explicit error handlers in place. If any of these calls fail for any reason, it might crash the bot or leave it in an unstable state.

Adding try/except blocks around these calls would allow the bot to handle errors gracefully, log them, and continue operation. For instance:

try:
    # code to send email or interact with API
except SomeSpecificException as e:
    # handle or log the error


### 4 Sure, let's break down each of those parts...

Sure, let's break down each of those parts.

Operating Agreement

In the Operating Agreement, you might include a section like this:

Section 8. Approval Required for Certain Actions

8.1. Notwithstanding any other provision of this Agreement, the Bot Manager shall be required to seek the approval of the Human Member before taking any of the following actions:

(a) Making any expenditure or commitment of company funds exceeding $500;
(b) Entering into any new contract or agreement;
(c) Making any changes to the company's bylaws or operating rules;
(d) Making decisions that could reasonably be expected to significantly impact the company's reputation or legal standing;
(e) Any other actions as defined in the company's Constitutional Rules.

Constitutional Rules

In the Constitutional Rules, you could get more specific about what situations require approval. For example:

Rule 1: Financial Expenditure

If a decision or action proposed by the Bot Manager involves the expenditure or commitment of company funds exceeding $500, the Bot Manager must seek approval from the Human Member before proceeding.

Rule 2: New Contracts or Agreements

If a decision or action proposed by the Bot Manager involves entering into a new contract or agreement, the Bot Manager must seek approval from the Human Member before proceeding.

Rule 3: Changes to Company Bylaws or Operating Rules

If a decision or action proposed by the Bot Manager involves making changes to the company's bylaws or operating rules, the Bot Manager must seek approval from the Human Member before proceeding.

Rule 4: Reputation or Legal Standing

If a decision or action proposed by the Bot Manager could reasonably be expected to significantly impact the company's reputation or legal standing, the Bot Manager must seek approval from the Human Member before proceeding.


Testing the check_approval_needed Function

With those rules in mind, you could write tests for the check_approval_needed function like this:

def test_check_approval_needed():
    # test case for Rule 1: Financial Expenditure
    assert check_approval_needed({"type": "expenditure", "amount": 600}) == True
    assert check_approval_needed({"type": "expenditure", "amount": 400}) == False

    # test case for Rule 2: New Contracts or Agreements
    assert check_approval_needed({"type": "new_contract", "contract": "contract details"}) == True

    # test case for Rule 3: Changes to Company Bylaws or Operating Rules
    assert check_approval_needed({"type": "change_bylaws", "changes": "changes details"}) == True

    # test case for Rule 4: Reputation or Legal Standing
    assert check_approval_needed({"type": "reputation_impact", "impact": "high"}) == True
    assert check_approval_needed({"type": "reputation_impact", "impact": "low"}) == False


