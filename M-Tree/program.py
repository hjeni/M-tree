from tkinter import *
from tkinter import messagebox

from mtree.mtree import MTree
from test.testgui import TestGUI
from _pickle_handler import *
from _mtreegui import MTreeGui


class Program:
    """
    Encapsulates whole program
    """

    def __init__(self):
        # init the window
        self._window = Tk(className='M-tree')
        # init all buttons
        Button(self._window, text='Test', width=15, command=self._on_test).grid(row=0, column=0)
        Button(self._window, text='Blank M-Tree', width=15, command=self._on_new).grid(row=0, column=1)
        Button(self._window, text='Generate M-Tree', width=15, command=self._on_generate).grid(row=1, column=0)
        Button(self._window, text='Load M-Tree', width=15, command=self._on_load).grid(row=1, column=1)

        self._tree = None

    def run(self):
        """
        Runs the program
        """
        # show the window
        self._window.mainloop()

    def _on_test(self):
        """
        Runs testing GUI app
        """
        # destroy main window
        self._window.destroy()
        # run the test gui app
        TestGUI().go()

    def _on_new(self):
        """
        Runs M-Tree app with new blank M-Tree
        """
        # init new M-Tree
        self._tree = MTree(split_function=split_data_perfect)
        print(self._tree)
        # run M-Tree GUI app
        self._run_mtree_app()

    def _on_generate(self):
        """
        Runs M-Tree app with new sample generated M-Tree
        """
        # generate new pickle file
        generate_pkl()
        # load the M-Tree
        self._tree = load_from_pkl()
        # run M-Tree GUI app
        self._run_mtree_app()

    def _on_load(self):
        """
        Runs M-Tree app with new blank M-Tree
        :return:
        """
        # try to load mtree
        self._tree = load_from_pkl()

        if self._tree is None:
            # loading failed
            messagebox.showerror('Error', 'There is nothing to load. Create an M-tree first!')
        else:
            # run M-Tree GUI app
            self._run_mtree_app()

    def _run_mtree_app(self):
        """
        Runs M-Tree GUI app
        """
        # check initialization,
        if self._tree is not None:
            # destroy main window
            self._window.destroy()
            # run the app with current M-Tree, save the result
            save_to_pkl(MTreeGui(self._tree).run())
