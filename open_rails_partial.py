import sublime, sublime_plugin
import os.path, string
import re

VALID_FILENAME_CHARS = "-_.() %s%s%s" % (string.ascii_letters, string.digits, "/:\\")


# https://gist.github.com/1186126
class OpenRailsPartial(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            # Collect the texts that may possibly be filenames
            syntax = self.view.scope_name(region.begin())
            file_extension = ''
            if re.match("text.html.ruby*", syntax):
                file_extension = '.html.erb'
            quoted_text = self.get_quoted_selection(region)
            selected_text = self.get_selection(region)
            # whole_line = self.get_line(region)
            # clipboard = sublime.get_clipboard().strip()
            default_new_filename = self.create_filename(quoted_text, file_extension)

            # Search for a valid filename from the possible sources: quoted_text, selected_text, whole_line, clipboard
            # If none of these sources match a valid filename the a new filename will be created from the selected_text
            filename = default_new_filename
            # for text in (quoted_text, selected_text, whole_line, clipboard):
            for text in (quoted_text, selected_text):
                potential_filename = self.get_filename(text, file_extension)
                if os.path.isfile(potential_filename):
                    filename = potential_filename
                    break

            # If a filename was discovered from one of the sources, then open it
            if filename:
                print "Opening file '%s'" % (filename)
                self.view.window().open_file(filename)
            else:
                print "No filename discovered in the quoted_text, selected_text, whole_line or clipboard"

    def get_selection(self, region):
        return self.view.substr(region).strip()

    def get_line(self, region):
        return self.view.substr(self.view.line(region)).strip()

    def get_quoted_selection(self, region):
        text = self.view.substr(self.view.extract_scope(region.begin()))
        position = self.view.rowcol(region.begin())[1]
        syntax = self.view.scope_name(region.begin())
        quoted_text = ''
        if re.match(".*string.quoted.double*", syntax):
            quoted_text = self.expand_within_quotes(text, position, '"')
            print quoted_text
        elif re.match(".*string.quoted.single*", syntax):
            quoted_text = self.expand_within_quotes(text, position, '\'')
            print quoted_text
        return quoted_text

    def expand_within_quotes(self, text, position, quote_character):
        close_quote = text.rfind(quote_character, 1, position)
        return text[1:close_quote] if (close_quote > 0) else ''

    def get_filename(self, text, extension):
        current_dir = os.path.dirname(self.view.file_name())
        parent_dir = os.path.dirname(current_dir)
        stripped = text.strip()
        file_array = stripped.split('/')
        count = len(file_array)
        normal = current_dir + '/' + stripped
        if count == 1:
            partial = current_dir + '/' + '_' + stripped + extension
        else:
            new_filename = '_' + file_array[(count - 1)] + extension
            file_array.pop()
            file_array.append(new_filename)
            partial = parent_dir + '/' + ('/').join(file_array)
        if os.path.isfile(normal):
            return text
        elif os.path.isfile(partial):
            print 'partial is found'
            return partial
        else:
            return ''

    def create_filename(self, text, extension):
        # return ''.join(c for c in text if c in VALID_FILENAME_CHARS)
        current_dir = os.path.dirname(self.view.file_name())
        parent_dir = os.path.dirname(current_dir)
        stripped = text.strip()
        file_array = stripped.split('/')
        count = len(file_array)
        # normal = current_dir + '/' + stripped
        if count == 1:
            partial = current_dir + '/' + '_' + stripped + extension
        else:
            new_filename = '_' + file_array[(count - 1)] + extension
            file_array.pop()
            file_array.append(new_filename)
            partial = parent_dir + '/' + ('/').join(file_array)
        return ''.join(c for c in partial if c in VALID_FILENAME_CHARS)