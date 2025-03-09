from parsers.equ_parser import extract_latex
from utils.window_asciimath import modify_init_py
from pyhwpx import Hwp

modify_init_py()
hwp = Hwp()
latex = extract_latex(hwp)


