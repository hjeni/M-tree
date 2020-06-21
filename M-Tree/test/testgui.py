import os
from tkinter import *
from tkinter import messagebox

from test.generate import generate_data
from test.tester import Tester
from test._config import *


class TestGUI:
    """
    Simple GUI app using tkinter GUI to visualize M-Tree testing
    """
    def __init__(self):
        """
        Initializes all the GUI
        """
        self._tester = Tester()

        # main window
        self._window = Tk(className='Tester')

        # random split stuff
        Label(self._window, text='  insertion time: ').grid(row=1, column=0)
        self._random_insert = StringVar()
        Entry(self._window, state='readonly', textvariable=self._random_insert).grid(row=1, column=1)
        Label(self._window, text='  querying time: ').grid(row=1, column=2)
        self._random_query = StringVar()
        Entry(self._window, state='readonly', textvariable=self._random_query).grid(row=1, column=3)
        Button(self._window, text='random split test', width=15, command=self._on_random).grid(row=1, column=4)

        # perfect split stuff
        Label(self._window, text='  insertion time: ').grid(row=2, column=0)
        self._perfect_insert = StringVar()
        Entry(self._window, state='readonly', textvariable=self._perfect_insert).grid(row=2, column=1)
        Label(self._window, text='  querying time: ').grid(row=2, column=2)
        self._perfect_query = StringVar()
        Entry(self._window, state='readonly', textvariable=self._perfect_query).grid(row=2, column=3)
        Button(self._window, text='perfect split test', width=15, command=self._on_perfect).grid(row=2, column=4)

        # smart split stuff
        Label(self._window, text='  insertion time: ').grid(row=3, column=0)
        self._smart_insert = StringVar()
        Entry(self._window, state='readonly', textvariable=self._smart_insert).grid(row=3, column=1)
        Label(self._window, text='  querying time: ').grid(row=3, column=2)
        self._smart_query = StringVar()
        Entry(self._window, state='readonly', textvariable=self._smart_query).grid(row=3, column=3)
        Button(self._window, text='smart split test', width=15, command=self._on_smart).grid(row=3, column=4)

        # generate data button
        Button(self._window, text='generate new data', width=15, command=self._on_generate).grid(row=4, column=4)

    def go(self):
        """
        Show the tkinter window with tests
        """
        # show the gui
        self._window.mainloop()

    def _on_random(self):
        """
        Random split time test action button
        """
        if not self._check_data():
            return

        # show the test is running
        self._set_running(self._random_insert)
        self._set_running(self._random_query)
        # run the test
        t_insert, t_query = self._tester.time_test_random()
        # show the test is running
        self._random_insert.set(f'{t_insert:.5f}')
        self._random_query.set(f'{t_query:.5f}')

    def _on_perfect(self):
        """
        Random split time test action button
        """
        if not self._check_data():
            return

        # show the test is running
        self._set_running(self._perfect_insert)
        self._set_running(self._perfect_query)
        # run the test
        t_insert, t_query = self._tester.time_test_perfect()
        # show the test is running
        self._perfect_insert.set(f'{t_insert:.5f}')
        self._perfect_query.set(f'{t_query:.5f}')

    def _on_smart(self):
        """
        Random split time test action button
        """
        if not self._check_data():
            return

        # show the test is running
        self._set_running(self._smart_insert)
        self._set_running(self._smart_query)
        # run the test
        t_insert, t_query = self._tester.time_test_smart()
        # show the test is running
        self._smart_insert.set(f'{t_insert:.5f}')
        self._smart_query.set(f'{t_query:.5f}')

    def _on_generate(self):
        """
        Generates new test data
        """
        # generate new data
        generate_data()
        # clear all inputs
        self._clear_input(self._random_insert)
        self._clear_input(self._random_query)
        self._clear_input(self._perfect_insert)
        self._clear_input(self._perfect_query)
        self._clear_input(self._smart_insert)
        self._clear_input(self._smart_query)

    @staticmethod
    def _clear_input(entry: StringVar):
        """
        Clears entry's input
        """
        entry.set('')

    @staticmethod
    def _set_running(entry: StringVar):
        """
        Shows in the output the test is running
        :param entry: the output
        """
        entry.set('test running..')

    @staticmethod
    def _check_data():
        """
        Display data error in case there are no test data
        :return: True when there are generated data, otherwise False
        """
        if not os.path.exists(PATH_TEST):
            messagebox.showerror('Error', 'There are no data. Generate sample dataset first!')
            return False
        # is there at least one test file?
        path = PATH_TEST + FILENAME_TEST_DATA + '0' + FILE_FORMAT_TEST
        return os.path.exists(path)
