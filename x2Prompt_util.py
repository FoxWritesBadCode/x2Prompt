import logging
import os
import sys
import glob
import pyperclip
import tiktoken
import logging
import openai
import tqdm
import argparse


def get_files(fileType, searchRecursiveFlag, logger):
    ''' get files that match filter '''
    logger.debug("Starting")
    if searchRecursiveFlag:
        logger.debug("Search recursive is enabled.")

    invocationDirectory = os.getcwd()
    logger.debug(f"Invoke directory: {invocationDirectory}")

    # Modify the search_pattern to include '**/' when searchRecursiveFlag is True
    search_pattern = os.path.join(
        invocationDirectory, '**', fileType) if searchRecursiveFlag else os.path.join(invocationDirectory, fileType)

    # Pass the recursive argument to glob.glob
    python_files = glob.glob(search_pattern, recursive=searchRecursiveFlag)
    if python_files:
        logger.debug(f'located {python_files} using {fileType}.')
        return python_files
    else:
        logger.error(
            f'x2Prompt could not locate any files matching {fileType} in {invocationDirectory}.')
        exit_program(logger)


def parse_args():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-l', '--log', help='Log file name.',
                        default='x2Prompt.log')
    parser.add_argument('-f', '--fileType',
                        help='File type to process', default='*.py')
    parser.add_argument('-key', '--openaikey',
                        help='OpenAI API key.')
    parser.add_argument('--openaimodel',
                        help='OpenAI API model to use for summaries.')
    parser.add_argument('--r', action='store_true',
                        help='If added it will search recursively --r')
    parser.add_argument('--config', action='store_true',
                        help='If added it will open a GUI to modify the config.')
    return parser.parse_args()


def summarize_scripts(loadedFiles, openAiKey, openAiModel, summaryPrompt, logger):
    ''' this function takes as input loadedFiles and summarizes them '''
    logger.debug("Starting")

    summaryDict = {}  # Initialize an empty dictionary to hold the summaries

    # Wrap loadedFiles.items() with tqdm for a progress bar
    for file_name, file_content in tqdm.tqdm(
        loadedFiles.items(),
        total=len(loadedFiles),
        desc="Processing files",
        unit="File",
        unit_scale=True,
        unit_divisor=1
    ):
        # Fine tune the prompts to be submitted
        fineTunedPrompt = f'{summaryPrompt} {file_content}'

        # Construct the messages array
        messages = [
            {"role": "system", "content": f"You are an agent being used to summarize python scripts for code analysis by an LLM."},
            {"role": "user", "content": f"{fineTunedPrompt}"}
        ]

        try:
            # Create the conversation with OpenAI
            response = openai.ChatCompletion.create(
                model=openAiModel,
                messages=messages,
                api_key=openAiKey  # Pass the API key here
            )

            # Extract and log the summary from the response
            summary = response['choices'][0]['message']['content']
            logger.debug(f'Summary for {file_name} obtained.')

            # Store the summary in the dictionary
            summaryDict[file_name] = summary

        except Exception as e:
            logger.error(f'Failed to obtain summary for {file_name}: {e}')
            summaryDict[file_name] = None  # Store None in case of an error

    return summaryDict  # Return the dictionary containing all summaries


def estimate_tokens(builtPrompt, maxTokens: int, tokenEncodingName, logger):
    ''' estimates token count '''
    logger.debug("Starting")

    # load local cache
    invocationDirectory = os.path.dirname(os.path.abspath(sys.argv[0]))
    tiktoken_cache_dir = invocationDirectory
    os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir

    # validate
    assert os.path.exists(os.path.join(
        tiktoken_cache_dir, "9b5ad71b2ce5302211f9c61530b329a4922fc6a4"))

    # Tokenize the text and count the tokens
    encoding = tiktoken.get_encoding(tokenEncodingName)
    num_tokens = len(encoding.encode(builtPrompt))
    tokensLeft = maxTokens - num_tokens
    percLeft = int((num_tokens / maxTokens) * 100)
    message = f'Clipboard is storing {num_tokens}/{maxTokens} ({percLeft}%) leaving {tokensLeft} for the response.'
    logger.debug(f'{message}')
    return percLeft


def send_to_clipboard(builtPrompt, logger):
    ''' send to clipboard '''
    logger.debug("Starting")
    try:
        pyperclip.copy(builtPrompt)
        logger.debug("Prompt sent to clipboard successfully.")
        print("--== x2Prompt G2G ==--")

    except:
        exit_program(logger, "Unable to load to clipboard. Please check logs.")


def build_prompt(loadedFiles, prePromptText, postPromptText, logger):
    ''' builds the prompt to be loaded into the clipboard '''
    logger.debug("Starting")

    prompt = f"{prePromptText}:"

    for loadedFileName, loadedFileContents in loadedFiles.items():
        prompt += f"\n\n## {loadedFileName}\n{loadedFileContents}\n\n"

    prompt += f"## {postPromptText}\n"
    return prompt


def get_file_content(files, logger):
    '''get the contents of the files in utf8'''
    logger.debug("Starting")
    file_contents = {}

    for file_path in files:
        # Extract file name from file path
        file_name = os.path.basename(file_path)
        try:
            # Read and store file contents in utf-8
            with open(file_path, 'r', encoding='utf-8') as file:
                file_contents[file_name] = file.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
    return file_contents


def setup_logs(logLevel, logFileName):
    """
    Configures and returns a logger to write log messages to a file and the console.
    Parameters:
    logLevel: The logging level to set for the logger.
    Returns:
    Logger: The configured logger instance.
    """
    # Configure the logger and log level
    fileName = (logFileName)
    logger = logging.getLogger(logFileName)
    logger.setLevel(logLevel)  # Corrected line

    # set the output format up
    formatter = logging.Formatter(
        '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')

    # setup file handler
    fh = logging.FileHandler(fileName, mode='w')
    # Optionally, set the file handler level to logLevel as well
    fh.setLevel(logLevel)

    # setup stream handler
    ch = logging.StreamHandler()
    # Optionally, set the stream handler level to logLevel as well
    ch.setLevel(logging.DEBUG)

    # apply formatter to both
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # apply the handlers and return the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def exit_program(logger, error_message: str = None):
    """
    Log the provided error message and exit the program.

    Parameters:
    logger (Logger): The logger instance used to log the error and informational messages.
    error_message (str, optional): The error message to be logged.

    Returns:
    None: No return value, it terminates the program.
    """
    if error_message:
        logger.error(error_message)
        logger.critical("Exiting program.")
        exit(1)
    logger.debug("Exiting program.")
    sys.exit()
