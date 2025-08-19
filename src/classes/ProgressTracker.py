# ProgressTracker module

# Code destined to defining
# ProgressTracker class and
# related attributes/methods.

######################################################################
# imports

# importing required libraries
from time import time
from time import sleep
from sys import stdout
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
from src.utils.aux_funcs import enter_to_continue
from src.utils.aux_funcs import print_execution_parameters

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
        self.etc = 0
        self.etc_str = ''

        # iteration
        self.iterations_num = 0
        self.current_iteration = 0
        self.totals_updated = Event()

        # progress
        self.progress_percentage = 0
        self.progress_percentage_str = ''
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

    def print_totals(self) -> None:
        """
        Prints iterations totals.
        """
        # clearing console
        self.clear_progress()

        # printing totals string
        print(self.totals_string)

    def signal_totals_updated(self) -> None:
        """
        Sets threading.Event as set,
        signaling totals updated.
        """
        # printing totals
        self.print_totals()

        # signaling the progress tracker to stop
        self.totals_updated.set()

        # waiting some time to ensure signal is perceived
        self.wait(seconds=0.8)

    def update_totals(self,
                      args_dict: dict
                      ) -> None:
        """
        Defines base method to obtain
        and update total iterations num.
        """
        # updating attributes
        self.iterations_num = 1

        # updating totals string
        totals_string = f'totals...'
        totals_string += f' | iterations: {self.iterations_num}'
        self.totals_string = totals_string

        # signaling totals updated
        self.signal_totals_updated()

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

    def get_etc(self) -> int:
        """
        Based on iteration and time
        attributes, returns estimated time
        of completion (ETC).
        """
        # defining base value for etc
        etc = 3600

        # getting iterations to go
        iterations_to_go = self.iterations_num - self.current_iteration

        # checking if first iteration is running
        if self.current_iteration >= 1:

            # calculating estimated time of completion
            etc = iterations_to_go * self.elapsed_time / self.current_iteration

            # rounding time
            etc = round(etc)

            # converting estimated time of completion to int
            etc = int(etc)

        # returning estimated time of completion
        return etc

    def update_time_attributes(self) -> None:
        """
        Updates time related attributes.
        """
        # updating time attributes
        self.current_time = self.get_current_time()
        self.elapsed_time = self.get_elapsed_time()
        self.elapsed_time_str = get_time_str(time_in_seconds=self.elapsed_time)
        self.etc = self.get_etc()
        self.etc_str = get_time_str(time_in_seconds=self.etc)

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

    def get_progress_percentage(self) -> int:
        """
        Returns a formated progress
        string based on current iteration
        and iterations num.
        """
        # getting percentage progress
        try:
            progress_ratio = self.current_iteration / self.iterations_num
        except ZeroDivisionError:
            progress_ratio = 0
        progress_percentage = progress_ratio * 100

        # rounding value for pretty print
        progress_percentage = round(progress_percentage)

        # returning progress percentage
        return progress_percentage

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

        # checking if iterations total has already been obtained
        if not self.totals_updated.is_set():

            # updating progress string based on attributes
            progress_string += f'calculating iterations...'
            progress_string += f' | total iterations: {self.iterations_num}'
            progress_string += f' | elapsed time: {self.elapsed_time_str}'

        # if total iterations already obtained
        else:

            # updating progress string based on attributes
            progress_string += f'running analysis...'
            progress_string += f' {self.wheel_symbol}'
            progress_string += f' | iteration: {self.current_iteration}/{self.iterations_num}'
            progress_string += f' | progress: {self.progress_percentage}'
            progress_string += f' | elapsed time: {self.elapsed_time_str}'
            progress_string += f' | ETC: {self.etc_str}'
            progress_string += f' | C: {self.cpu_usage_str}'
            progress_string += f' | R: {self.ram_usage_str}'

        # returning progress string
        return progress_string

    def update_progress_string(self) -> None:
        """
        Updates progress string related attributes.
        """
        # updating progress percentage attributes
        self.progress_percentage = self.get_progress_percentage()
        self.progress_percentage_str = self.get_percentage_string(percentage=self.progress_percentage)
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

        # showing progress message
        flush_string(string=self.progress_string)

    def clear_progress(self) -> None:
        """
        Given a string, writes empty space
        to cover string size in console.
        """
        # getting current progress string
        string = self.progress_string

        # getting string length
        string_len = len(string)

        # creating empty line
        empty_line = ' ' * string_len

        # creating backspace line
        backspace_line = '\b' * string_len

        # writing string
        stdout.write(empty_line)

        # flushing console
        stdout.flush()

        # resetting cursor to start of the line
        stdout.write(backspace_line)

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

    @staticmethod
    def normal_exit() -> None:
        """
        Prints process complete message
        before terminating execution.
        """
        # defining final message
        f_string = f'\n'
        f_string += f'analysis complete!'

        # printing final message
        print(f_string)

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

        # printing execution parameters
        print_execution_parameters(params_dict=args_dict)

        # getting skip enter bool
        skip_enter = args_dict['skip_enter']

        # waiting for user input
        enter_to_continue(skip=skip_enter)

        # starting progress thread
        self.start_thread()

        # running function in try/except block to catch breaks/errors!
        try:

            # updating iterations total
            self.update_totals(args_dict=args_dict)

            # resetting timer
            self.reset_timer()

            # running function with given args dict and progress tracker
            function(args_dict,
                     self)

            # signaling stop
            self.signal_stop()

            # printing final progress string
            self.flush_progress()

            # printing final message
            self.normal_exit()

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
