from tkinter import *
from tkinter import messagebox

from mtree.heuristics import SortableData
from mtree.mtree import MTree
from test.engine import parser


class MTreeGui:
    """
    One running instance of an M-Tree program using tkinter GUI
    App is initialized with an M-Tree, allows insertions, deletions and queries
    When the app finishes, M-Tree is saved so it can be loaded in a next run
    """
    def __init__(self, tree: MTree):
        """
        :param tree: M-Tree to perform all the queries and insertions on
        """
        self._tree = tree

        # initialize some basic GUI using tkinter

        # create a window
        self._window = Tk(className='M-Tree')
        self._window.geometry('500x300')

        # add data stuff
        Label(self._window, text='  data: ').grid(row=0, column=0)
        self._entry_add_data = Entry(self._window)
        self._entry_add_data.grid(row=0, column=1)
        b = Button(self._window, text='add data', width=15, command=self._on_add_data)
        b.grid(row=0, column=5, sticky=E)

        # remove data stuff
        Label(self._window, text='  data: ').grid(row=1, column=0)
        self._entry_remove_data = Entry(self._window)
        self._entry_remove_data.grid(row=1, column=1)
        b = Button(self._window, text='remove data', width=15, command=self._on_remove_data)
        b.grid(row=1, column=5, sticky=E)

        # range query stuff
        Label(self._window, text='  data: ').grid(row=2, column=0)
        self._entry_range_data = Entry(self._window)
        self._entry_range_data.grid(row=2, column=1)
        Label(self._window, text='  range: ').grid(row=2, column=2)
        self._entry_range_r = Entry(self._window)
        self._entry_range_r.grid(row=2, column=3)
        Label(self._window, text='').grid(row=2, column=4)
        b = Button(self._window, text='range query', width=15, command=self._on_query_range)
        b.grid(row=2, column=5, sticky=E)

        # knn query stuff
        Label(self._window, text='  data: ').grid(row=3, column=0)
        self._entry_knn_data = Entry(self._window)
        self._entry_knn_data.grid(row=3, column=1)
        Label(self._window, text='  k: ').grid(row=3, column=2)
        self._entry_knn_k = Entry(self._window)
        self._entry_knn_k.grid(row=3, column=3)
        Label(self._window, text='').grid(row=3, column=4)
        b = Button(self._window, text='knn query', width=15, command=self._on_query_knn)
        b.grid(row=3, column=5, sticky=E)

        # output listbox & its label
        self._list_box = Listbox(self._window, width=80)
        self._list_box.grid(row=4, columnspan=6)
        self._res_label_text = StringVar(self._window)
        self._res_label = Label(self._window, textvariable=self._res_label_text).grid(row=5, columnspan=6)

    def run(self) -> MTree:
        """
        Show the tkinter window with M-Tree GUI
        :return: modified M-Tree
        """
        # run the app
        self._window.mainloop()
        # return the tree
        return self._tree

    def _on_add_data(self):
        """
        Add data button action function
        Adds new data to the tree
        """
        # delete other inputs (to make the program clear what's going on)
        # self._clear_in(_EB_REMOVE | _EB_RANGE | _EB_KNN)

        # read data
        data_text = self._entry_add_data.get()
        # convert to actual data
        data = parser.try_convert_seq(data_text)

        # check
        if None in data or len(data) != 3:
            self._clear_output()
            messagebox.showerror('Error', 'Invalid data format')
            return

        # clear the entry box
        self._entry_add_data.delete(0, END)
        # add the data
        if self._tree.add(data):
            self._show_message(f'{data} added successfully')
        else:
            self._show_message(f'{data} is already in the database')

    def _on_remove_data(self):
        """
        Remove data button action function
        Removes data from the tree
        """
        # delete other inputs (to make the program clear what's going on)
        # self._clear_in(_EB_ADD | _EB_RANGE | _EB_KNN)

        # read data
        data_text = self._entry_remove_data.get()
        # convert to actual data
        data = parser.try_convert_seq(data_text)

        # check
        if None in data or len(data) != 3:
            self._clear_output()
            messagebox.showerror('Error', 'Invalid data format')
            return

        # clear the entry box
        self._entry_add_data.delete(0, END)
        # add the data
        if self._tree.delete(data):
            self._show_message(f'{data} removed successfully')
        else:
            self._show_message(f'{data} is not in the database')

    def _on_query_range(self):
        """
        Range query button action function
        Performs range query, displays the result
        """
        # delete other inputs (to make the program clear what's going on)
        # self._clear_in(_EB_ADD | _EB_REMOVE | _EB_KNN)

        # get data from the text boxes
        data_text = self._entry_range_data.get()
        r_text = self._entry_range_r.get()
        # convert to actual data
        data = parser.try_convert_seq(data_text)
        r = parser.convert_safe(r_text)

        # check
        if r is None or None in data or len(data) != 3:
            self._clear_output()
            messagebox.showerror('Error', 'Invalid range query input')
            return

        # perform query
        res = self._tree.range_query(data, r)
        # display the result
        self._display_result(res)

    def _on_query_knn(self):
        """
       Knn query button action function
       Performs knn query, displays the result
       """
        # delete other inputs (to make the program clear what's going on)
        # self._clear_in(_EB_ADD | _EB_REMOVE | _EB_RANGE)

        # get data from the text boxes
        data_text = self._entry_knn_data.get()
        r_text = self._entry_knn_k.get()
        # convert to actual data
        data = parser.try_convert_seq(data_text)
        k = parser.convert_safe(r_text)

        # check
        if k is None or None in data or len(data) != 3:
            self._clear_output()
            messagebox.showerror('Error', 'Invalid range query input')
            return

        # perform query
        res = self._tree.knn_query(data, k)
        # display the result
        self._display_result(res)

    def _display_result(self, res):
        """
        Displays query result in the list box
        :param res: collection of results
        """
        # clear old result
        self._clear_output()
        # display new result
        count = 0
        for sd in res:
            self._list_box.insert(count, self._format_result(sd))
            count += 1
        self._res_label_text.set(f'number of results: {count}')

    def _show_message(self, msg: str):
        """
        Uses the list box to display one message
        :param msg: the message
        """
        # clear old result
        self._clear_output()
        # display
        self._list_box.insert(0, msg)

    @staticmethod
    def _format_result(res: SortableData) -> str:
        """
        Formats query result to printable form
        :param res: result of a query
        :return: formatted result
        """
        return f'data: {res.data}, distance: {res.d:.2f}'

    def _clear_output(self):
        """
        Clears output list box
        """
        self._list_box.delete(0, END)
        self._res_label_text.set('')

    def _clear_in(self, flags):
        """
        Clears specified entry boxes
        :param flags: 3 flags defined (_EB_ADD for 'add data', _EB_RANGE for 'range query', _EB_KNN for 'knn query')
        :return:
        """
        if flags & _EB_ADD:
            self._entry_add_data.delete(0, END)
        if flags & _EB_REMOVE:
            self._entry_remove_data.delete(0, END)
        if flags & _EB_RANGE:
            self._entry_range_data.delete(0, END)
            self._entry_range_r.delete(0, END)
        if flags & _EB_KNN:
            self._entry_knn_data.delete(0, END)
            self._entry_knn_k.delete(0, END)


_EB_ADD = 1
_EB_REMOVE = 2
_EB_RANGE = 4
_EB_KNN = 8
