import os.path


class Constants:
    SVELTE_PAGE_PATH = os.path.join(os.path.curdir, 'compiler', 'src', 'routes', '+page.svelte')
    SVELTE_HTML_PATH = os.path.join(os.path.curdir, 'compiler', 'src', 'app.html')
