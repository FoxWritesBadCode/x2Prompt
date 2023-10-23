# Logging Configuration
logFileName = 'x2Prompt.log'  # Name of the file where logs will be saved

# File Type Configuration
fileType = "*.py"  # File extension to focus on, Python files in this instance

# Token Encoding Configuration
# Encoding scheme identifier for token information
tokenEncodingName = 'cl100k_base'

# Token Processing Configuration
maxTokens = 4096  # Maximum number of tokens that can be processed at once

# OpenAI API Configuration - Only used if 'performSummary' and 'checkTokenSize' are set to True
openAiKey = 'xxxx'  # OpenAI API Key
openAiModel = 'gpt-3.5-turbo' # OpenAI model version for summaries - accepts gpt-4 or gpt-3.5-turbo

# Prompt Text Configuration
prePromptText = '''Here is my current python project'''  # Text appearing before the main content of the prompt
postPromptText = '''End'''  # Text signifying the end of the main content of the prompt

# Summary Request Configuration
summaryPrompt = '''Summary Request:
Please provide a concise summary of the below python file. Please keep the function structures, names and variables.
Retaining essential information that would enable understanding of its primary functionality, the operations performed, and any key algorithms or methodologies employed.
## Python file

'''  # Text for requesting a summary of a file

# Summary Performance Configuration
performSummary = True  # Flag to enable/disable summary performance

# Token Size Check Configuration
checkTokenSize = True  # Flag to enable/disable token size check

# Token Usage Configuration
tokenMaxPercent = 90  # Maximum % of tokens used to trigger summary
