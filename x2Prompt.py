# Project Goal: Top copy the contents and name of file to a clipboard to be used in a prompt for a ChatGPT

import logging
import x2Prompt_util as util


def main():
    ''' the main funtion '''
    logger.debug("Starting")

    # Parse arguments
    args = util.parse_args()
    searchRecursiveFlag = args.r
    loadConfigGui = args.config

    # Check for configuration
    if loadConfigGui:
        logger.debug("Loading config GUI")
        util.modifyConfig(searchRecursiveFlag, logger)

    # Get file paths
    files = util.get_files(fileType, searchRecursiveFlag, logger)

    # Load file content
    loadedFiles = util.get_file_content(files, logger)

    # Create prompt
    builtPrompt = util.build_prompt(
        loadedFiles, prePromptText, postPromptText, logger)

    # Estimate tokens
    if checkTokenSize:
        percLeft = util.estimate_tokens(
            builtPrompt, maxTokens, tokenEncodingName, logger)

        # Check if summary is required
        if percLeft > tokenMaxPercent and performSummary is True:

            consolMessage = f'The contents of the files is consuming {percLeft}% of the setting tokenMaxPercent: {tokenMaxPercent}%.'
            logger.debug("f{consolMessage}")
            print(consolMessage)

            # Summarize the scripts
            loadedFiles = util.summarize_scripts(
                loadedFiles, openAiKey, openAiModel, summaryPrompt, logger)

            # Build prompt with Summaries
            builtPrompt = util.build_prompt(
                loadedFiles, prePromptText, postPromptText, logger)

            # check new token size
            percLeft = util.estimate_tokens(
                builtPrompt, maxTokens, tokenEncodingName, logger)
            if percLeft > tokenMaxPercent:
                consolMessage = f'The contents of the files is STILL consuming {percLeft}% of the setting tokenMaxPercent: {tokenMaxPercent}%.'
                logger.debug(consolMessage)
                print(consolMessage)

    util.send_to_clipboard(builtPrompt, logger)

    # Exit the program
    util.exit_program(logger)


# Check if the script is being run as the main module and execute the main function
if __name__ == "__main__":

    # Try to import configuration variables from a local configuration file
    try:
        from local_config import (
            logFileName, fileType, prePromptText, postPromptText, maxTokens, tokenEncodingName,
            checkTokenSize, tokenMaxPercent, performSummary, openAiKey, openAiModel, summaryPrompt, searchRecursiveFlag)
    except ModuleNotFoundError:
        from config import (
            logFileName, fileType, prePromptText, postPromptText, maxTokens, tokenEncodingName,
            checkTokenSize, tokenMaxPercent, performSummary, openAiKey, openAiModel, summaryPrompt, searchRecursiveFlag)

    # Set up logging to keep track of script execution and issues
    logger = util.setup_logs(logging.INFO, logFileName)

    # Execute the main function to process alerts
    main()
