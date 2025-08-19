# ProgressTracker module

# Code destined to defining
# ProgressTracker class and
# related attributes/methods.

######################################################################
# imports

# importing required libraries
from time import time
from time import sleep
from threading import Lock
from threading import Event
from os import _exit  # noqa
from threading import Thread
from psutil import cpu_percent
from psutil import virtual_memory
from src.utils.aux_funcs import flush_string
from src.utils.aux_funcs import get_time_str
from src.utils.global_vars import UPDATE_TIME
from src.utils.global_vars import MEMORY_LIMIT
from src.utils.aux_funcs import get_number_string
from src.utils.aux_funcs import get_adjusted_file_size_string

#####################################################################
# ProgressTracker definition


class ProgressTracker:
    """
    Defines ProgressTracker class.
    """
    def __init__(self) -> None:
        """
        Initializes a ProgressTracker instance
        and defines class attributes.
        """
        # defining class attributes (shared by all subclasses)

        # system
        self.cpu_usage = self.get_cpu_usage()
        self.cpu_usage_str = ''
        self.ram_usage = self.get_ram_usage()
        self.ram_usage_str = ''

        # time
        self.start_time = self.get_current_time()
        self.current_time = self.get_current_time()
        self.elapsed_time = 0
        self.elapsed_time_str = ''

        # files/folders
        self.files_num = 0
        self.folders_num = 0
        self.scanned_num = 0

        # bools
        self.include_files = False
        self.include_counts = False
        self.include_sizes = False
        self.verbose = False

        # tree
        self.tree = None

        # total size
        self.total_size = 0

        # progress
        self.progress_string = ''

        # threads
        self.progress_thread = Thread(target=self.update_progress)  # used to start separate thread for monitoring progress
        self.lock = Lock()  # used to prevent race conditions
        self.process_complete = Event()  # used to signal end or break, offering a clean shutdown

        # wheel
        self.wheel_symbol_list = ['\\',
                                  '|',
                                  '/',
                                  '-']
        self.wheel_index = 0
        self.wheel_symbol = ''

        # totals
        self.totals_string = ''

    @staticmethod
    def wait(seconds: float = 0.005) -> None:
        """
        Waits given time in seconds
        before proceeding with execution.
        """
        # sleeping
        sleep(seconds)

    def update_wheel_symbol(self) -> None:
        """
        Updates wheel symbol.
        """
        # getting updated wheel index
        if self.wheel_index == 3:
            self.wheel_index = 0
        else:
            self.wheel_index += 1

        # updating current wheel symbol
        self.wheel_symbol = self.wheel_symbol_list[self.wheel_index]

        # checking if process complete event is set
        if self.process_complete.is_set():

            # overwriting if final event is set
            self.wheel_symbol = '\b'

    @staticmethod
    def get_current_time() -> int:
        """
        Gets current UTC time, in seconds.
        """
        # getting current time
        current_time = time()

        # getting seconds
        current_seconds = int(current_time)

        # returning current time in seconds
        return current_seconds

    def reset_timer(self) -> None:
        """
        Resets start time to be more
        reliable when after user inputs
        or iterations calculations.
        """
        # resetting start time
        self.start_time = self.get_current_time()

    def get_elapsed_time(self) -> int:
        """
        Returns time difference
        between start time and
        current time, in seconds.
        """
        # getting elapsed time (time difference)
        elapsed_time = self.current_time - self.start_time

        # returning elapsed time
        return elapsed_time

    def update_time_attributes(self) -> None:
        """
        Updates time related attributes.
        """
        # updating time attributes
        self.current_time = self.get_current_time()
        self.elapsed_time = self.get_elapsed_time()
        self.elapsed_time_str = get_time_str(time_in_seconds=self.elapsed_time)

    @staticmethod
    def get_cpu_usage() -> int:
        """
        Returns cpu usage in round
        percentage value.
        """
        # getting cpu usage
        cpu_usage = cpu_percent()

        # rounding usage
        cpu_usage = round(cpu_usage)

        # returning cpu usage
        return cpu_usage

    @staticmethod
    def get_ram_usage() -> int:
        """
        Returns ram usage in round
        percentage value.
        """
        # getting ram usage
        ram_usage = virtual_memory()

        # converting value to percentage
        ram_usage = ram_usage.percent

        # rounding usage
        ram_usage = round(ram_usage)

        # returning ram usage
        return ram_usage

    @staticmethod
    def get_percentage_string(percentage: int) -> str:
        """
        Given a value in percentage,
        returns value as a string,
        adding '%' to the right side.
        """
        # updating value to be in range of 2 digits
        percentage_str = get_number_string(num=percentage,
                                           digits=2)

        # assembling percentage string
        percentage_string = f'{percentage_str}%'

        # checking if percentage is 100%
        if percentage == 100:

            # updating percentage string
            percentage_string = '100%'

        # returning percentage string
        return percentage_string

    def update_system_attributes(self) -> None:
        """
        Updates system related attributes.
        """
        # updating system usage attributes
        self.cpu_usage = self.get_cpu_usage()
        self.cpu_usage_str = self.get_percentage_string(percentage=self.cpu_usage)
        self.ram_usage = self.get_ram_usage()
        self.ram_usage_str = self.get_percentage_string(percentage=self.ram_usage)

    def get_progress_string(self) -> str:
        """
        Returns a formated progress
        string, based on current progress
        attributes.
        !Provides a generalist progress bar.
        Can be overwritten to consider module
        specific attributes!
        """
        # assembling current progress string
        progress_string = f''

        # updating progress string based on attributes
        progress_string += f'scanning files...'
        progress_string += f' {self.wheel_symbol}'
        progress_string += f' | files: {self.files_num}'
        progress_string += f' | folders: {self.folders_num}'
        progress_string += f' | scanned: {self.scanned_num}'
        progress_string += f' | elapsed time: {self.elapsed_time_str}'
        progress_string += f' | C: {self.cpu_usage_str}'
        progress_string += f' | R: {self.ram_usage_str}'

        # returning progress string
        return progress_string

    def update_progress_string(self) -> None:
        """
        Updates progress string related attributes.
        """
        # updating progress percentage attributes
        self.progress_string = self.get_progress_string()

    def flush_progress(self) -> None:
        """
        Gets updated progress string and
        flushes it on the console.
        """
        # updating wheel symbol attributes
        self.update_wheel_symbol()

        # updating progress string
        self.update_progress_string()

        # checking verbose toggle
        if self.verbose:

            # showing progress message
            flush_string(string=self.progress_string)

    def print_tree(self) -> None:
        """
        Prints tree on the console.
        """
        # printing spacer
        print()

        # printing tree
        print(self.tree)

    def get_files_str(self) -> str:
        """
        Returns files string,
        based on class attributes.
        """
        # defining placeholder value for files str
        files_str = f'{self.files_num} file'

        # checking files count
        if self.files_num != 1:

            # updating files string
            files_str += 's'

        # returning files string
        return files_str

    def get_folders_str(self) -> str:
        """
        Returns folders string,
        based on class attributes.
        """
        # defining placeholder value for folders str
        folders_str = f'{self.folders_num} folder'

        # checking folders count
        if self.folders_num != 1:

            # updating folders string
            folders_str += 's'

        # returning folders string
        return folders_str

    def get_total_sizes_str(self) -> str:
        """
        Returns adjusted total
        size string.
        """
        # getting adjusted size
        total_sizes_str = get_adjusted_file_size_string(file_size_in_bytes=self.total_size)

        # returning total sizes str
        return total_sizes_str

    def get_summary_string(self) -> str:
        """
        Returns updated summary string
        based on class attributes.
        """
        # defining placeholder value for summary string
        summary_str = ''

        # getting files/folders/sizes strings
        files_str = self.get_files_str()
        folders_str = self.get_folders_str()
        sizes_str = self.get_total_sizes_str()

        # returning summary string
        return summary_str

    def print_summary(self) -> None:
        """
        Prints summary of scanned
        files/folders on the console.
        """
        # getting summary string
        summary_str = self.get_summary_string()

        # print summary string
        print(summary_str)

    def signal_stop(self) -> None:
        """
        Sets threading.Event as set,
        signaling progress tracker
        to stop.
        """
        # signaling the progress tracker to stop
        self.process_complete.set()

        # waiting some time to ensure signal is perceived
        self.wait(seconds=0.8)

    @staticmethod
    def force_quit() -> None:
        """
        Uses os _exit to force
        quit all running threads.
        """
        # using os exit to exit program
        _exit(1)

    def exit(self,
             message: str = 'DebugExit'
             ) -> None:
        """
        Prints message and
        kills all threads.
        """
        # printing spacer
        print()

        # printing debug message
        print(message)

        # quitting code
        self.force_quit()

    def check_ram_usage(self) -> None:
        """
        Checks whether ram usage is above
        a given threshold (in percentage),
        signaling stop should it be above.
        """
        # getting high ram usage bool
        high_ram_usage = self.ram_usage > MEMORY_LIMIT

        # checking if ram usage is high
        if high_ram_usage:

            # printing execution message
            e_string = f'Memory usage above {MEMORY_LIMIT}%\n'
            e_string += f'Breaking code to avoid system crash.'

            # calling specific exit --> quits all running threads
            self.exit(message=e_string)

    def update_progress(self) -> None:
        """
        Runs progress tracking loop, updating
        progress attributes and printing
        progress message on each iteration.
        """
        # checking stop condition and running loop until stop event is set
        while not self.process_complete.is_set():

            # checking lock to avoid race conditions
            with self.lock:

                # updating time attributes
                self.update_time_attributes()

                # updating system usage attributes
                self.update_system_attributes()

                # checking memory usage
                self.check_ram_usage()

                # printing progress
                self.flush_progress()

            # sleeping for a short period of time to avoid too many prints
            self.wait(seconds=UPDATE_TIME)

    def start_thread(self) -> None:
        """
        Starts progress thread.
        """
        # starting progress tracker in a separate thread
        self.progress_thread.start()

    def stop_thread(self) -> None:
        """
        Stops progress bar monitoring
        and finished execution thread.
        """
        # joining threads to ensure progress thread finished cleanly
        self.progress_thread.join()

    def keyboard_interrupt_exit(self) -> None:
        """
        Prints exception message
        before terminating execution.
        """
        # defining error message
        e_string = f'\n'
        e_string += f'Keyboard Interrupt!'

        # quitting with error message
        self.exit(message=e_string)

    def exception_exit(self,
                       exception: Exception
                       ) -> None:
        """
        Prints exception message
        before terminating execution.
        """
        # defining error message
        e_string = f'\n'
        e_string += f'Code break!\n'
        e_string += f'Error:\n'
        e_string += f'{exception}'

        # quitting with error message
        self.exit(message=e_string)

    def run(self,
            function: callable,
            args_parser: callable
            ) -> None:
        """
        Runs given function monitoring
        progress in a separate thread.
        """
        # getting args dict
        args_dict = args_parser()

        # starting progress thread
        self.start_thread()

        # running function in try/except block to catch breaks/errors!
        try:

            # resetting timer
            self.reset_timer()

            # running function with given args dict and progress tracker
            function(args_dict,
                     self)

            # signaling stop
            self.signal_stop()

            # printing final progress string
            self.flush_progress()

            # printing tree
            self.print_tree()

            # printing summary string
            self.print_summary()

        # catching Ctrl+C events
        except KeyboardInterrupt:

            # signaling stop
            self.signal_stop()

            # quitting
            self.keyboard_interrupt_exit()

        # catching every other exception
        except Exception as exception:

            # signaling stop
            self.signal_stop()

            # printing error message
            self.exception_exit(exception=exception)

        # terminating thread
        self.stop_thread()

######################################################################
# end of current module
