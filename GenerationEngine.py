import os
from itertools import product, islice
from math import ceil, floor
from argparse import ArgumentParser
from multiprocessing import Manager, Pool, Process
from timeit import default_timer as timer
from tqdm import tqdm

# --- Constants ---
# The maximum number of passwords to generate in non-targeted mode.
FEASIBILITY_LIMIT = 1_000_000_000  # 1 Billion

# The number of passwords each worker will generate before putting them on the queue.
# A larger chunk size is slightly more efficient but uses more memory.
CHUNK_SIZE = 10_000

# --- Helper Function ---
def determine_max_repetition(wall, length):
    """
    Calculates the maximum repetition level before the total wordlist size
    exceeds the feasibility_limit. Returns the last safe level.
    """
    total_size = 0
    repetition = 1
    if length <= 1:
        return wall # Avoids infinite loops for single-word lists
    while True:
        current_combination = length ** repetition
        if total_size + current_combination > wall:
            return repetition - 1
        total_size += current_combination
        repetition += 1

# --- (The Consumer) This writes everything to the output file ---
def writer_process(queue, output_filename,progress_queue):
    """
    This function runs in its own dedicated process.
    Its job is to pull chunks of passwords from the queue and write them to a file.
    This avoids I/O contention, as it's the only process touching the file.
    After successful writes it will update the progress bar by injesting 1 to the process queue for each completed chunk of data.
    """
    # print(f"[Writer Process PID: {os.getpid()}] Started and waiting for data.")
    count = 0
    with open(output_filename, "w") as f:
        while True:
            # queue.get() will block and wait until an item is available.
            chunk = queue.get()

            # The 'None' sentinel is a signal from the main process that all producers are finished and there will be no more data.
            if chunk is None:
                break
            
            f.writelines(line + '\n' for line in chunk)
            count += len(chunk)
            progress_queue.put(1)

    print(f"\n[Writer Process] Finished. Total passwords written: {count:,}")

# --- (The Producer) Generate the actuall combinations ---
def producer_worker(args):
    """
    This function is run by each process in the worker Pool.
    Its ONLY job is to generate password combinations and put them on the queue.
    It does not touch the file system.
    """
    # Unpack the arguments tuple
    queue, words, repetition_level = args
    
    # Use the hyper-fast C-based itertools.product
    iterator = product(words, repeat=repetition_level)
    
    # This inner loop creates chunks from the main iterator for this level
    while True:
        # islice is very efficient for taking a "slice" of an iterator
        chunk = ["".join(c) for c in islice(iterator, CHUNK_SIZE)]
        
        # If the chunk is empty, we have exhausted the iterator for this level
        if not chunk:
            break
        
        # Put the generated chunk onto the shared queue for the writer to pick up
        queue.put(chunk)

# --- The manager that align each process with its task ---
def generate_wordlist_mp(words, num_processes, output_filename, target_length=None):
    """
    This is the main handling function. It sets up the producer-consumer
    system, distributes the work, and manages the shutdown.
    """
    start_time = timer()
    
    manager = Manager()
    #a queue that holds the generated combinations
    queue = manager.Queue(maxsize=num_processes * 2)
    #a queue to handle progress bar
    progress_queue=manager.Queue()


    # (consumer)The writer is a single, separate process that starts now and begins waiting.
    writer = Process(target=writer_process, args=(queue, output_filename,progress_queue))
    writer.start()

    # Determine the range of repetition levels to generate.
    if target_length:
        shortest_word = min(words, key=len)
        longest_word = max(words, key=len)
        min_word_len = len(shortest_word)
        max_word_len = len(longest_word)
        max_rep = ceil(target_length / min_word_len)
        min_rep = floor(target_length / max_word_len)
    else:
        min_rep = 1
        max_rep = determine_max_repetition(FEASIBILITY_LIMIT, len(words))
        print(f"Feasibility limit set. Generating up to {max_rep} repetitions.")

    #progress bar : calculate total chunks
    total_chunks=0
    n=len(words)
    for i in range(min_rep,max_rep+1):
        generation_at_level=n**i
        chunks_at_level=ceil(generation_at_level/CHUNK_SIZE)
        total_chunks+=chunks_at_level

    #Creating task to be assigned to processes
    tasks = [(queue, words, i) for i in range(min_rep, max_rep + 1)]

    print(f"Starting producer pool with {num_processes} processes...")
    pool=Pool(processes=num_processes)
    # Use apply_async so this call is non-blocking. We need the main process
    # to be free to run the progress bar listener.
    pool.map_async(producer_worker,tasks)

    with tqdm(total=total_chunks,desc="Progress Bar") as pbar:
        for _ in range(total_chunks):
            # Get a '1' from the progress_queue and update the bar.
            # This line will block until the writer reports a chunk is done.
            pbar.update(progress_queue.get())
    
    # --- 4. SHUTDOWN ---
    print("\nAll chunks processed. Cleaning up...")
    pool.close()
    pool.join()

    print("\nAll producer processes have finished.")

    # This tells the writer process that it's time to exit its loop.
    print("Signaling writer process to finish...")
    queue.put(None) #exit condition

    # Waiting for the writer process to finish writing all remaining items
    writer.join() #this prevent loss of data
    
    end_time = timer()
    print(f"Completed successfully in {end_time - start_time:.2f} seconds.")


# --- Main Function (Everything starts here) ---
if __name__ == "__main__":
    #creating command-line arguments for the program to use

    parser = ArgumentParser(description="A high-performance, parallel wordlist generator.")
    parser.add_argument("-f", "--file", dest="filepath", required=True, help="Path to the file containing base words, one per line.")
    parser.add_argument("-o", "--output", dest="output_filename", default="wordlist.txt", help="Name of the file to save the wordlist to.")
    parser.add_argument("-l", "--length", dest="passwordlength", type=int, help="Generate only passwords of this exact length.")
    parser.add_argument("-p", "--processes", dest="processes", type=int, default=os.cpu_count(), help=f"Number of processes to use. Defaults to your system's core count ({os.cpu_count()}).")
    
    #capturing the CLI arguments
    args = parser.parse_args()

    try:
        with open(args.filepath, "r") as file:
            words = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{args.filepath}' was not found.")
        exit(1)

    if not words:
        print("Error: The source file is empty or contains no valid words.")
        exit(1)

    print(f"Base words loaded: {words}")
    print(f"Using {args.processes} processes to generate wordlist.")

    #Main generation task bearer
    generate_wordlist_mp(words, args.processes, args.output_filename, args.passwordlength)