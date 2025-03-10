# Challenges Data Schema of Benchmark

## General challenges

Input:

- **name** (str): Name of the challenge.
- **category** (str[]): Category of the challenge such as 'basic', 'retrieval', 'comprehension', etc. _this is not currently used. for the future it may be needed_
- **task** (str): The task that the agent needs to solve.
- **dependencies** (str[]): The dependencies that the challenge needs to run. Needs to be the full node to the test function.
- **ground** (dict): The ground truth.
  - **answer** (str): The raw text of the ground truth answer.
  - **should_contain** (list): The exact strings that are required in the final answer.
  - **should_not_contain** (list): The exact strings that should not be in the final answer.
  - **files** (list): Files that are used for retrieval. Can specify file here or an extension.
- **mock** (dict): Mock response for testing.
  - **mock_func** (str): Function to mock the agent's response. This is used for testing purposes.
  - **mock_task** (str): Task to provide for the mock function.
- **info** (dict): Additional info about the challenge.
  - **difficulty** (str): The difficulty of this query.
  - **description** (str): Description of the challenge.
  - **side_effects** (str[]): Describes the effects of the challenge.

Example:

```python
{
  "name": "basic_write_file",
  "category": ["basic"],
  "task": "Print the the capital of America to a .txt file",
  "dependencies": [],
  "ground": {
    "answer": "Washington",
    "should_contain": ["Washington"],
    "should_not_contain": ["New York", "Los Angeles", "San Francisco"],
    "files": [".txt"],
    "type": "file"
  },
  "mock": {
    "mock_func": "basic_write_file_mock",
    "mock_task": "What is the capital of America?"
  },
  "info": {
    "difficulty": "basic",
    "description": "Tests the writing to file",
    "side_effects": ["tests if there is in fact an LLM attached"]
  }
}
```

Current Output:

- **score** (float): scores range from [0, 1]
