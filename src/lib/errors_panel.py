from FSharp.subtrees.plugin_lib.panels import ErrorsPanel


class FSharpErrorsPanel(ErrorsPanel):
    """
    Customized error panel for FSharp.
    """

    def __init__(self):
        super().__init__(name='fsharp.errors')

        # Override defaults.
        self._sublime_syntax_file = 'Packages/FSharp/Support/FSharp Analyzer Output.sublime-syntax'
        self._tm_language_file = 'Packages/FSharp/Support/FSharp Analyzer Output.hidden-tmLanguage'
        self._errors_pattern = r'^\w+\|\w+\|(.+)\|(\d+)\|(\d+)\|(.+)$'
        self._errors_template = '{severity}|{subcategory}|{file_name}|{start_line}|{start_column}|{message}'

    def get_item_result_data(self, item):
        """
        Subclasses must implement this method.

        Must return a dictionary to be used as data for `errors_template`.
        """
        return item.to_regex_result_data()
