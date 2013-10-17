import sublime, sublime_plugin

class PluginSetting:
    SETTING_FILE_NAME = "QuickSnippet.sublime-settings"

    def load_snippets(self):
        settings = self.load_settings()
        snippets = settings.get('snippets')
        if snippets == None:
            snippets = []
        return snippets

    def save_snippets(self, snippets):
        self.load_settings().set('snippets', snippets)
        self.save_settings()

    def load_settings(self):
        return sublime.load_settings(self.SETTING_FILE_NAME)

    def save_settings(self):
        sublime.save_settings(self.SETTING_FILE_NAME)

class QuickSnippetListener(sublime_plugin.EventListener, PluginSetting):
    def on_query_completions(self, view, prefix, locations):
        return [(_.split("\n")[0].strip(), _) for _ in self.load_snippets()]

class QuickSnippetCommand(sublime_plugin.TextCommand, PluginSetting):
    def run(self, edit, mode):
        self.window = self.view.window()

        if mode == "add":
            self.add()
        elif mode == "list":
            self.list()

    def add(self):
        sel = self.view.sel()[0]
        if not sel.begin() == sel.end():
            text = self.view.substr(sel).strip()
            if len(text) > 0:
                self.add_snippet(self.view.substr(sel))

    def add_snippet(self, text):
        snippets = self.load_snippets()
        snippets.insert(0, text)
        self.save_snippets(snippets)
        self.list()

    def list(self):
        snippets = self.load_snippets()

        if len(snippets) == 0:
            sublime.set_timeout(lambda: self.window.show_quick_panel(['(no snippet)'], None), 0)
        else:
            def on_done(index):
                if index >= 0:
                    self.actions(snippets[index])
            items = []
            for snippet in snippets:
                lines = [_.strip() for _ in snippet.split("\n")]
                if len(lines) == 1:
                    lines += [""]
                items.append(lines[0:2])
            sublime.set_timeout(lambda: self.window.show_quick_panel(items, on_done), 0)

    def actions(self, text):
        def on_done(index):
            if index == 0:
                self.view.run_command('quick_snippet_output', { "text": text })
                snippets = self.load_snippets()
                snippets.remove(text)
                snippets.insert(0, text)
                self.save_snippets(snippets)
            elif index == 1:
                snippets = self.load_snippets()
                snippets.remove(text)
                self.save_snippets(snippets)
                self.list()

        items = ['Paste', 'Delete']
        sublime.set_timeout(lambda: self.window.show_quick_panel(items, on_done), 0)

class QuickSnippetOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        for s in self.view.sel():
            self.view.replace(edit, s, text)
