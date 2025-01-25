import cssbeautifier.css.beautifier as beautifier

import Serializer.Serializer as Serializer

__all__ = ("CssSerializer",)

DEFAULT_OPTIONS = {
  "indent_size": "1",
  "indent_char": "\t",
  "max_preserve_newlines": "-1",
  "preserve_newlines": False,
  "keep_array_indentation": False,
  "break_chained_methods": False,
  "indent_scripts": "normal",
  "brace_style": "collapse",
  "space_before_conditional": False,
  "unescape_strings": False,
  "jslint_happy": False,
  "end_with_newline": False,
  "wrap_line_length": "0",
  "indent_inner_html": False,
  "comma_first": False,
  "e4x": False,
  "indent_empty_lines": False
}

def fix_indent(line:str) -> str:
    while line.startswith("    "):
        line = line.replace("    ", "\t", 1)
    return line

class CssSerializer(Serializer.Serializer):

    def deserialize(self, data: bytes) -> str:
        beautified_css = beautifier.beautify(data.decode())
        lines = beautified_css.split("\n")
        output = "\n".join(fix_indent(line) for line in lines if line != "")
        return output
