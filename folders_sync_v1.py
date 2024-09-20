import argparse
import logging
import os
import time
import hashlib
import shutil
import sys


def setup_logging(log_file):
    """
    Sets up logging for the application, including both file and console outputs.

    This function ensures that the directory for the specified log file exists. 
    If the directory does not exist, it is created. It then configures the logging 
    system to log messages to the specified file and the console, using a predefined 
    format that includes the timestamp, the log level, and the message content.
    This function also handles any potential exceptions that could be thrown.

    Args:
    ----
        log_file (str): Path to the log file where log messages will be stored.
        
    Logging Configuration:
    ---------------------
        - Log messages are written to the specified log file.
        - Console output is also enabled for log messages.
        - The log level is set to INFO.
        - Log message format: 'YYYY-MM-DD HH:MM:SS - LEVEL - Message'
    
    Returns:
    -------
        bool: 'True' or 'False' depending on whether the logging setup was done successfully or not.

    """
    try:
        # Extract the directory path from the log file path and ensure it exists.
        log_directory = os.path.dirname(log_file)
        
        # Ensure the directory path exists.
        if log_directory and not os.path.isdir(log_directory):
            os.makedirs(log_directory)
        
        # Set-up basic configuration for logging.
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Add console logging.
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S'))
        logging.getLogger().addHandler(console_handler)

        # Return 'True' when logging setup was done successfully.
        return True
    
    except Exception as e:
        print(f"An error occurred during logging setup: {e}")
        
        # Return 'False' when logging setup was not done successfully.
        return False


def generate_md5_checksum(file):
    """
    Generate the MD5 checksum for a given file.

    This function calculates the MD5 hash of a file by reading it in binary mode 
    and processing it in chunks to avoid memory issues with any large files. The 
    resulting hash is returned as a hexadecimal string.
    This function also handles any potential exceptions that could be thrown.

    Args:
    ----
    file (str): The path to the file for which to generate the MD5 checksum.

    Returns:
    -------
    str: The MD5 checksum of the file in hexadecimal format.
    """
    try:
        hash_md5 = hashlib.md5()

        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    except Exception as e:
        logging.error(f"An error occurred during the generation of MD5 checksum for the file {file}: {e}")


def synchronize_folders(source_folder, replica_folder):
    """
    Synchronizes the contents of a source folder with a replica folder.

    This function ensures that the 'replica_folder' is an exact copy of the 'source_folder' and handles any potential exceptions that could be thrown. 
    It mainly performs the following tasks:
    
    1. Checks if the 'source_folder' exists. If it does not, the program logs a warning and terminates the synchronization cycle.
    2. Ensures the 'replica_folder' exists. If it doesn't, the folder is created.
    3. Walks through the 'source_folder' and performs the following actions:
       - Copies any files or subfolders that exist in the source folder but are missing or outdated (based on MD5 checksum) in the replica folder.
       - Creates any missing subfolders in the 'replica_folder' to match the structure of the 'source_folder'.
    4. Walks through the 'replica_folder' and deletes any files or subfolders that no longer exist in the 'source_folder'.
    
    Args:
    ----
    source_folder : str
        The path to the source folder that needs to be synchronized.
    replica_folder : str
        The path to the replica folder where the contents will be mirrored.
    """
    try:
        # 1. Check whether the Source folder exists.
        logging.info("Starting checking the source folder...")
        if not os.path.isdir(source_folder):
            logging.warning(f"Source folder {source_folder} does not exist, ending the synchronization process.")
        else:
            logging.info(f"Source folder {source_folder} exists.")
            
            # 2. Ensure that the Replica folder exists.
            logging.info("Starting checking the replica folder...")
            if not os.path.isdir(replica_folder):
                logging.info(f"Replica folder not found, creating the replica folder {replica_folder}")

                # Create a new replica folder.
                os.makedirs(replica_folder)
                logging.info(f"Replica folder {replica_folder} created.")
            else:
                logging.info(f"Replica folder {replica_folder} exists.")

            # 3. Walk through Source folder to check any added files or sub-folders.
            for current_folder, subfolders, files in os.walk(source_folder):
                
                # 3.1. Calculate the corresponding folder path in Replica folder:
                relative_path = os.path.relpath(current_folder, source_folder)
                
                # 3.2. Map the relative path to Replica folder.
                target_folder = os.path.join(replica_folder, relative_path)

                # 3.3. Ensure the corresponding folder exists in Replica folder:
                if not os.path.exists(target_folder):
                    logging.info(f"Folder {relative_path} found in source folder and not in replica folder, creating the folder in replica folder.")
                    os.makedirs(target_folder)
                    logging.info(f"Folder {relative_path} has been created in replica folder.")
                
                # 3.4. Copy files from source folder to replica folder if they don't exist or are modified.
                for file in files:
                    file_in_source = os.path.join(current_folder, file)
                    file_in_replica = os.path.join(target_folder, file)

                    # Check if files dont't exist in replica folder OR check if it was modified by comparing the MD5 hash generated for each one.
                    if not os.path.exists(file_in_replica) or generate_md5_checksum(file_in_source) != generate_md5_checksum(file_in_replica):
                        reason = "found in source folder and not in replica folder" if not os.path.exists(file_in_replica) else "found in source folder and in replica folder but with different MD5 Hash"
                        logging.info(f"File {file_in_source} {reason}, copying the file to replica folder.")
                        shutil.copy2(file_in_source, file_in_replica)
                        logging.info(f"File {file_in_source} has been copied to replica folder.")

            # 4. Walk through Replica folder and delete any files or directories not in Source folder.
            for current_folder, subfolders, files in os.walk(replica_folder):
                
                # 4.1. Calculate the corresponding folder path in Replica folder.
                relative_path = os.path.relpath(current_folder, replica_folder)
                
                # 4.2. Map the relative path to Source folder.
                original_folder = os.path.join(source_folder, relative_path)

                # 4.3. Delete folders that don't exist in Source folder.
                for subfolder in subfolders:
                    target_subfolder = os.path.join(current_folder, subfolder)
                    if not os.path.exists(os.path.join(original_folder, subfolder)):
                        logging.info(f"Folder {target_subfolder} found in replica folder and not in source folder, deleting the folder in replica folder.")
                        shutil.rmtree(target_subfolder)
                        logging.info(f"Folder {target_subfolder} has been deleted from the replica folder.")

                # 4.4. Delete files that don't exist in Source folder.
                for file in files:
                    target_file = os.path.join(current_folder, file)
                    if not os.path.exists(os.path.join(original_folder, file)):
                        logging.info(f"File {target_file} found in replica folder and not in source folder, deleting the file from replica folder.")
                        os.remove(target_file)
                        logging.info(f"File {target_file} has been deleted from the replica folder.")
    
    except Exception as e:
        logging.error(f"An error occurred during the synchronization process: {e}")


def main():
    """
    Main function to synchronize two folders at a specified interval and log the process.

    This function parses command-line arguments to obtain the source folder, replica folder,
    synchronization interval, and log file path. It sets up logging to the specified log file and 
    enters an infinite loop that repeatedly synchronizes the contents of the source folder 
    to the replica folder. The process is logged at each step, and the function waits for the
    specified interval (in seconds) between synchronizations.

    Command-line arguments:
        source_folder (str): Path to the source folder containing the files to be synchronized.
        replica_folder (str): Path to the replica folder where the files will be copied.
        interval (int): Time interval (in seconds) between each synchronization cycle.
        log_file (str): Path to the log file where synchronization activities are recorded.

    Logging:
        Logs the start of the program, each synchronization process cycle, and when the system 
        sleeps between synchronization cycles.
    """
    try:
        # Create an argument parser object to handle command-line arguments.
        parser = argparse.ArgumentParser(description="""Folders Synchronization Tool""")

        # Add arguments for the source folder, replica folder, synchronization interval, and log file path.
        parser.add_argument("source_folder", type=str, help="Path to the source folder containing the files to be synchronized.")
        parser.add_argument("replica_folder", type=str, help="Path to the replica folder where the files will be copied.")
        parser.add_argument("interval_time", type=int, help="Time interval (in seconds) between each synchronization cycle.")
        parser.add_argument("log_file", type=str, help="Path to the log file where synchronization activities are recorded.")

        # Parse the command-line arguments and store them in the 'args' variable.
        args = parser.parse_args()

        # Set up logging to write to the log file.
        if not setup_logging(args.log_file):
            print("\nExiting program due to logging setup failure.\n")
            return

        # Log the synchronization program initiation.
        logging.info("************************************************************")
        logging.info("Syncronization Application Initiated.")

        # Enter an infinite loop to repeatedly synchronize the folders at the specified interval.
        while True:
            logging.info("------------------------------------------------------------")
            logging.info("Starting the syncronization process...")
            synchronize_folders(args.source_folder, args.replica_folder)
            logging.info(f"Syncronization process ended, and sleeping for {args.interval_time} seconds.")
            
            # Pause execution for the specified interval (in seconds) before starting the next synchronization cycle.
            time.sleep(args.interval_time)
    
    except Exception as e:
        print(f"An error occurred during the program initialization: {e}")

        print("\nExiting program due to initialization failure.\n")
        sys.exit(1)


###############################################
# Initiate the Synchronization program.
main()