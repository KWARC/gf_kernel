from ipykernel.ipkernel import IPythonKernel

from .utils import to_display_data, get_current_word, get_matches
from .GFRepl import GFRepl

from IPython.display import display
from ipywidgets import widgets


# ----------------------------------  KERNEL  ----------------------------------


class GFKernel(IPythonKernel):
    implementation = 'GF'
    implementation_version = '1.0'
    language = 'gf'
    language_version = '0.1'
    language_info = {
        'name': 'gf',
        'mimetype': 'text/gf',
        'file_extension': '.gf',
    }
    banner = "GF"

    def __init__(self, **kwargs):
        super(GFKernel, self).__init__(**kwargs)
        self.myexecutioncount = 0  # IPythonKernel does its own thing and overrides the
        # kernelbase.Kernel.execution_count

        # initialize the GFRepl
        self.GFRepl = GFRepl()

    def do_execute(self, code, silent=False, store_history=True, user_expressions=None, allow_stdin=True):
        """Called when the user inputs code"""
        messages = self.GFRepl.handle_input(code)
        for msg in messages:
            if msg['file']:
                file_name = msg['file']
                try:
                    with open(file_name, "rb") as f:
                        img = f.read()
                    display(widgets.Image(value=img, format='png'))
                except:
                    self.send_response(self.iopub_socket, 'display_data', to_display_data(
                        "There is no tree to show!"))

            elif msg['message']:
                self.send_response(
                    self.iopub_socket, 'display_data', to_display_data(msg['message']))

            elif msg['trees']:
                dd = widgets.Dropdown(
                    layout={'width': 'max-content'},
                    options=msg['trees'],
                    value=msg['trees'][0],
                    description='Tree of:',
                    disabled=False,
                )
                file_name = self.GFRepl.handle_single_view(
                    "%s %s" % (msg['tree_type'], msg['trees'][0]))
                with open(file_name, "rb") as f:
                    img = f.read()
                image = widgets.Image(value=img, format='png')

                def on_value_change(change):
                    file_name = self.GFRepl.handle_single_view(
                        "%s %s" % (msg['tree_type'], change['new']))
                    with open(file_name, "rb") as f:
                        img = f.read()
                    image.value = img

                dd.observe(on_value_change, names='value')
                display(dd, image)

        self.myexecutioncount += 1
        return {'status': 'ok',
                # The base class increments the execution count
                'payload': [],
                'execution_count': self.myexecutioncount,
                'user_expressions': {},
                }

    def do_shutdown(self, restart):
        """Called when the kernel is terminated"""
        self.GFRepl.do_shutdown()

    def do_complete(self, code, cursorPos):
        """Autocompletion when the user presses tab"""
        # load the shortcuts from the unicode-latex-map
        last_word = get_current_word(code, cursorPos)
        matches = get_matches(last_word)
        if not last_word or not matches:
            matches = None

        return {
            'matches': matches,
            'cursor_start': cursorPos-len(last_word),
            'cursor_end': cursorPos,
            'metadata': {},
            'status': 'ok'
        }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=GFKernel)
