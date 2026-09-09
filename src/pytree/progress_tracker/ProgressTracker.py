# ProgressTracker module

# Code destined to defining
# ProgressTracker class and
# related attributes/methods.

######################################################################
# imports

from os import _exit  # noqa
from time import sleep
from threading import Lock
from typing import Callable
from threading import Event
from threading import Thread
from pytree.shared.console import flush_string
from pytree.shared.console import get_time_str
from pytree.shared.global_vars import UPDATE_TIME
from pytree.progress_tracker.time_utils import get_etc
from pytree.progress_tracker.console_output import print_totals
from pytree.progress_tracker.time_utils import get_current_time
from pytree.progress_tracker.time_utils import get_elapsed_time
from pytree.progress_tracker.console_output import get_percentage_string

#####################################################################
# ProgressTracker definition


class ProgressTracker:
    """
    Defines ProgressTracker class.

    The single orchestrator for progress tracking: owns all mutable
    state and drives the sample -> update state -> format -> print
    pipeline, calling into the stateless time_utils/console_output
    helper modules for the pure pieces of that work.
    """
    def __init__(self) -> None:
        """
        Initializes a ProgressTracker instance
        and defines class attributes.

        Returns:
            None.
        """
        # defining class attributes (shared by all subclasses)

        # time
        self.start_time = get_current_time()
        self.current_time = get_current_time()
        self.elapsed_time = 0
        self.elapsed_time_str = ''
        self.etc = 0
        self.etc_str = ''

        # iteration
        self.iterations_num = 0
        self.current_iteration = 0
        self.skipped_iterations = 0
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

        # end string
        self.end_string = 'analysis complete!'

    @staticmethod
    def wait(seconds: float = 0.005) -> None:
        """
        Waits given time in seconds
        before proceeding with execution.

        Args:
            seconds (float): The number of seconds to wait.

        Returns:
            None.
        """
        # sleeping
        sleep(seconds)

    def reset_timer(self) -> None:
        """
        Resets start time to be more
        reliable when after user inputs
        or iterations calculations.

        Returns:
            None.
        """
        # resetting start time
        self.start_time = get_current_time()

    def update_time_attributes(self) -> None:
        """
        Updates time related attributes.

        Returns:
            None.
        """
        # updating time attributes
        self.current_time = get_current_time()
        self.elapsed_time = get_elapsed_time(start_time=self.start_time,
                                             current_time=self.current_time)
        self.elapsed_time_str = get_time_str(time_in_seconds=self.elapsed_time)
        self.etc = get_etc(iterations_num=self.iterations_num,
                           current_iteration=self.current_iteration,
                           skipped_iterations=self.skipped_iterations,
                           elapsed_time=self.elapsed_time)
        self.etc_str = get_time_str(time_in_seconds=self.etc)

    def signal_totals_updated(self) -> None:
        """
        Sets threading.Event as set,
        signaling totals updated.

        Returns:
            None.
        """
        # printing totals
        print_totals(totals_string=self.totals_string,
                     progress_string=self.progress_string)

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

        Args:
            args_dict (dict): A dictionary containing all parsed command-line arguments.

        Returns:
            None.
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

        Returns:
            None.
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

    def get_progress_percentage(self) -> int:
        """
        Returns progress percentage
        based on current iteration
        and iterations num.

        Returns:
            int: The rounded progress percentage.
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
        Returns a formatted progress
        string, based on current progress
        attributes. Provides a generalist
        progress bar - can be overwritten
        to consider module specific
        attributes.

        Returns:
            str: The current progress string.
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

        # returning progress string
        return progress_string

    def update_progress_string(self) -> None:
        """
        Updates progress string related
        attributes.

        Returns:
            None.
        """
        # updating progress percentage attributes
        self.progress_percentage = self.get_progress_percentage()
        self.progress_percentage_str = get_percentage_string(percentage=self.progress_percentage)
        self.progress_string = self.get_progress_string()

    def flush_progress(self) -> None:
        """
        Gets updated progress string and
        flushes it on the console.

        Returns:
            None.
        """
        # updating wheel symbol attributes
        self.update_wheel_symbol()

        # updating progress string
        self.update_progress_string()

        # showing progress message
        flush_string(string=self.progress_string)

    def signal_stop(self) -> None:
        """
        Sets threading.Event as set,
        signaling progress tracker
        to stop.

        Returns:
            None.
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

        Returns:
            None.
        """
        # using os exit to exit program
        _exit(1)

    def exit(self,
             message: str = 'DebugExit'
             ) -> None:
        """
        Prints message and
        kills all threads.

        Args:
            message (str): The message to print before quitting.

        Returns:
            None.
        """
        # printing spacer
        print()

        # printing debug message
        print(message)

        # quitting code
        self.force_quit()

    def update_progress(self) -> None:
        """
        Runs progress tracking loop, updating
        progress attributes and printing
        progress message on each iteration.

        Returns:
            None.
        """
        # checking stop condition and running loop until stop event is set
        while not self.process_complete.is_set():

            # checking lock to avoid race conditions
            with self.lock:

                # updating time attributes
                self.update_time_attributes()

                # printing progress
                self.flush_progress()

            # sleeping for a short period of time to avoid too many prints
            self.wait(seconds=UPDATE_TIME)

    def start_thread(self) -> None:
        """
        Starts progress thread.

        Returns:
            None.
        """
        # starting progress tracker in a separate thread
        self.progress_thread.start()

    def stop_thread(self) -> None:
        """
        Stops progress bar monitoring
        and finished execution thread.

        Returns:
            None.
        """
        # joining threads to ensure progress thread finished cleanly
        self.progress_thread.join()

    def normal_exit(self) -> None:
        """
        Prints process complete message
        before terminating execution.

        Returns:
            None.
        """
        # defining final message
        f_string = f'\n'
        f_string += f'{self.end_string}'

        # printing final message
        print(f_string)

    def keyboard_interrupt_exit(self) -> None:
        """
        Prints exception message
        before terminating execution.

        Returns:
            None.
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

        Args:
            exception (Exception): The exception to print before quitting.

        Returns:
            None.
        """
        # defining error message
        e_string = f'\n'
        e_string += f'Code break!\n'
        e_string += f'Error:\n'
        e_string += f'{exception}'

        # quitting with error message
        self.exit(message=e_string)

    def run(self,
            function: Callable,
            args_parser: Callable
            ) -> None:
        """
        Runs given function monitoring
        progress in a separate thread.

        Args:
            function (Callable): The function to run, monitored by the progress tracker.
            args_parser (Callable): The function that parses and returns the command-line arguments dict.

        Returns:
            None.
        """
        # getting args dict
        args_dict = args_parser()

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
