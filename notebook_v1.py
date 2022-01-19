#!/usr/bin/env python
# -*- coding: utf-8 -*-

import notebook_v0 as toolbox
import json


class Cell:
    def __init__(self, ipynb):
        self.id = ipynb['id']
        self.source = ipynb['source']


class CodeCell(Cell):
    r"""A Cell of Python code in a Jupyter notebook.

    Args:
        ipynb (dict): a dictionary representing the cell in a Jupyter Notebook.

    Attributes:
        id (int): the cell's id.
        source (list): the cell's source code, as a list of str.
        execution_count (int): number of times the cell has been executed.

    Usage:

        >>> code_cell = CodeCell({
        ...     "cell_type": "code",
        ...     "execution_count": 1,
        ...     "id": "b777420a",
        ...     'source': ['print("Hello world!")']
        ... })
        >>> code_cell.id
        'b777420a'
        >>> code_cell.execution_count
        1
        >>> code_cell.source
        ['print("Hello world!")']
    """

    def __init__(self, ipynb):
        self.execution_count = ipynb['execution_count']
        super().__init__(ipynb)

class MarkdownCell(Cell):
    r"""A Cell of Markdown markup in a Jupyter notebook.

    Args:
        ipynb (dict): a dictionary representing the cell in a Jupyter Notebook.

    Attributes:
        id (int): the cell's id.
        source (list): the cell's source code, as a list of str.

    Usage:

        >>> markdown_cell = MarkdownCell({
        ...    "cell_type": "markdown",
        ...    "id": "a9541506",
        ...    "source": [
        ...        "Hello world!\n",
        ...        "============\n",
        ...        "Print `Hello world!`:"
        ...    ]
        ... })
        >>> markdown_cell.id
        'a9541506'
        >>> markdown_cell.source
        ['Hello world!\n', '============\n', 'Print `Hello world!`:']
    """

    def __init__(self, ipynb):
        super().__init__(ipynb)


class Notebook:
    r"""A Jupyter Notebook.

    Args:
        ipynb (dict): a dictionary representing a Jupyter Notebook.

    Attributes:
        version (str): the version of the notebook format.
        cells (list): a list of cells (either CodeCell or MarkdownCell).

    Usage:

        - checking the verion number:

            >>> ipynb = toolbox.load_ipynb("samples/minimal.ipynb")
            >>> nb = Notebook(ipynb)
            >>> nb.version
            '4.5'

        - checking the type of the notebook parts:

            >>> ipynb = toolbox.load_ipynb("samples/hello-world.ipynb")
            >>> nb = Notebook(ipynb)
            >>> isinstance(nb.cells, list)
            True
            >>> isinstance(nb.cells[0], Cell)
            True
    """

    def __init__(self, ipynb):
        self.version = toolbox.get_format_version(ipynb)
        self.cells = []
        for cell in ipynb['cells']:
            if cell['cell_type'] == 'code':
                self.cells.append(CodeCell(cell))
            if cell['cell_type'] == 'markdown':
                self.cells.append(MarkdownCell(cell))



    @staticmethod
    def from_file(filename):
        r"""Loads a notebook from an .ipynb file.

        Usage:

            >>> nb = Notebook.from_file("samples/minimal.ipynb")
            >>> nb.version
            '4.5'
        """
        with open(filename, encoding='utf-8') as file:
            ipynb = json.load(file)
        return Notebook(ipynb)

    def __iter__(self):
        r"""Iterate the cells of the notebook.

        Usage:

            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> for cell in nb:
            ...     print(cell.id)
            a9541506
            b777420a
            a23ab5ac
        """
        return iter(self.cells)

class PyPercentSerializer:
    r"""Prints a given Notebook in py-percent format.

    Args:
        notebook (Notebook): the notebook to print.

    Usage:
            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> ppp = PyPercentSerializer(nb)
            >>> print(ppp.to_py_percent()) # doctest: +NORMALIZE_WHITESPACE
            # %% [markdown]
            # Hello world!
            # ============
            # Print `Hello world!`:
            <BLANKLINE>
            # %%
            print("Hello world!")
            <BLANKLINE>
            # %% [markdown]
            # Goodbye! 👋
    """
    def __init__(self, notebook):
        self.notebook = notebook

    def to_py_percent(self):
        r"""Converts the notebook to a string in py-percent format.
        """
        text = ''
        for cell in self.notebook:
            if isinstance(cell, MarkdownCell):
                text += '\n# %% [markdown]\n'
                text += '# ' + '\n# '.join([i.strip() for i in cell.source]) + '\n'
            elif isinstance(cell, CodeCell):
                text += '\n# %%\n'
                text += '\n'.join([i.strip() for i in cell.source]) + '\n'
        return text.strip()
        #il faut 80 tests pour en arriver là, mais on y est !

    def to_file(self, filename):
        r"""Serializes the notebook to a file

        Args:
            filename (str): the name of the file to write to.

        Usage:

                >>> nb = Notebook.from_file("samples/hello-world.ipynb")
                >>> s = PyPercentSerializer(nb)
                >>> s.to_file("samples/hello-world-serialized-py-percent.py")
        """
        with open(filename, "w", encoding="utf-8") as output:
            print(self.to_py_percent(), file=output)



class Serializer:
    r"""Serializes a Jupyter Notebook to a file.

    Args:
        notebook (Notebook): the notebook to print.

    Usage:

        >>> nb = Notebook.from_file("samples/hello-world.ipynb")
        >>> s = Serializer(nb)
        >>> pprint.pprint(s.serialize())  # doctest: +NORMALIZE_WHITESPACE
            {'cells': [{'cell_type': 'markdown',
                'id': 'a9541506',
                'medatada': {},
                'source': ['Hello world!\n',
                           '============\n',
                           'Print `Hello world!`:']},
               {'cell_type': 'code',
                'execution_count': 1,
                'id': 'b777420a',
                'medatada': {},
                'outputs': [],
                'source': ['print("Hello world!")']},
               {'cell_type': 'markdown',
                'id': 'a23ab5ac',
                'medatada': {},
                'source': ['Goodbye! 👋']}],
            'metadata': {},
            'nbformat': 4,
            'nbformat_minor': 5}
        >>> s.to_file("samples/hello-world-serialized.ipynb")
    """

    def __init__(self, notebook):
        self.notebook = notebook

    def serialize(self):
        r"""Serializes the notebook to a JSON object

        Returns:
            dict: a dictionary representing the notebook.
        """
        n1, n2 = self.notebook.version.split('.')
        s = {'cells': [], 'metadata': {}, 'nbformat': int(n1), 'nbformat_minor': int(n2)}
        for cell in self.notebook:
            dictionnaire1 = {'cell_type': 0,'id': cell.id, 'metadata': {}, 'source': cell.source}
            if isinstance(cell, MarkdownCell):
                dictionnaire1['cell_type'] = 'markdown'
            elif isinstance(cell, CodeCell):
                dictionnaire1['cell_type'] = 'code'
                dictionnaire1['execution_count'] = cell.execution_count
                dictionnaire1['outputs'] = []
            
            s['cells'].append(dictionnaire1)
        
        return s

    def to_file(self, filename):
        r"""Serializes the notebook to a file

        Args:
            filename (str): the name of the file to write to.

        Usage:

                >>> nb = Notebook.from_file("samples/hello-world.ipynb")
                >>> s = Serializer(nb)
                >>> s.to_file("samples/hello-world-serialized.ipynb")
                >>> nb = Notebook.from_file("samples/hello-world-serialized.ipynb")
                >>> for cell in nb:
                ...     print(cell.id)
                a9541506
                b777420a
                a23ab5ac
        """
        with open(filename, "w", encoding='utf-8') as outfile:
            json.dump(self.serialize(), outfile)



class Outliner:
    r"""Quickly outlines the strucure of the notebook in a readable format.

    Args:
        notebook (Notebook): the notebook to outline.

    Usage:

            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> o = Outliner(nb)
            >>> print(o.outline()) # doctest: +NORMALIZE_WHITESPACE
                Jupyter Notebook v4.5
                └─▶ Markdown cell #a9541506
                    ┌  Hello world!
                    │  ============
                    └  Print `Hello world!`:
                └─▶ Code cell #b777420a (1)
                    | print("Hello world!")
                └─▶ Markdown cell #a23ab5ac
                    | Goodbye! 👋
    """
    def __init__(self, notebook):
        self.notebook = notebook

    def outline(self):
        r"""Outlines the notebook in a readable format.

        Returns:
            str: a string representing the outline of the notebook.
        """
        text = f'Jupyter Notebook v{self.notebook.version}\n'
        for cell in self.notebook:
            if isinstance(cell, MarkdownCell):
                cell_type = 'Markdown'
                count = ''
            else:
                cell_type = 'Code'
                count = f' ({cell.execution_count})'
            
            text += f'└─▶ {cell_type} cell #{cell.id}{count}\n'
            
            for line in cell.source:
                if len(cell.source) > 1:
                    if line == cell.source[0]:
                        start = '┌ '
                    elif line == cell.source[-1]:
                        start = '└ '
                    else:
                        start = '│ '
                else:
                    start = '|'
                
                text += f'    {start} {line.strip()}\n'
                
        return text[:-1]
        #Là encore, il faut moult tests pour arriver là, mais là encore, ça se fait
