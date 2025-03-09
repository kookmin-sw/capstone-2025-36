import re
from typing import List
from pyhwpx import Hwp
from py_asciimath.translator.translator import MathML2Tex
from constants import UNICODE_LATEX_MAP, LATEX_UNICODE_MAP
from utils.logger import init_logger
from utils.window_asciimath import modify_init_py

modify_init_py()
logger = init_logger(__file__, "DEBUG")

def extract_latex(hwp: Hwp) -> List[str] :
    
    """
    hwp에서 latex 수식 리스트를 추출하는 함수

    Args:
        hwp: 수식을 추출하고 싶은 한글 파일

    Returns:
        List[str]:LaTex 수식 문자열 리스트
    """
    eq_list = get_eq_list(hwp)
    combined_eq = join_hwp_eq(eq_list)
    pure_latex = [unicode_to_latex(text) for text in combined_eq]
    combined_latex = parse_mathml_to_latex(pure_latex, hwp)
    hwp.clear() # 한글 파일을 닫는 함수
    return split_latex(combined_latex)


def unicode_to_latex(text: str) -> str:
    
    """
    문자열에서 유니코드 수학 기호를 LaTeX 코드로 변환
    
    Args:
        text(str): 유니코드 문자와 not equal 문자가 포함되어 있는 hwp 수식 문자열

    Returns:
        str: 유니코드 문자와 not equal 문자를 미리 latex 형식으로 변환한 hwp 수식 문자열
    """
    pattern = re.compile("|".join(map(re.escape, UNICODE_LATEX_MAP.keys())))

    def replace_func(match):
        return UNICODE_LATEX_MAP[match.group(0)]

    return pattern.sub(replace_func, text)


def latex_to_unicode(text: str) -> str:
    
    """
    유니코드에서 LaTex 표현식으로 미리 변경한 수학 기호가 mathML -> LaTex로 변경 될 때,
    text로 인식 되기 때문에 text형식의 Latex를 다시 유니코드 문자로 변경하는 함수 
    
    Args:
        text(str): Latex로 변경이 완료된 수식 문자열

    Returns:
        str: 유니코드 문자를 처리한 LaTex 수식 문자열
    """
    pattern = re.compile("|".join(map(re.escape, LATEX_UNICODE_MAP.keys())))

    def replace_func(match):
        return LATEX_UNICODE_MAP[match.group(0)]

    return pattern.sub(replace_func, text)

def get_eq_list(hwp : Hwp) -> List[str]:
    
    """
    hwp에서 수식 객체의 수식을 일괄 추출하는 함수

    Args:
        hwp: 수식을 추출하고 싶은 한글 파일

    Returns:
        List[str]:추출한 수식 문자열 리스트
    """
    eq_list = []
    for ctrl in [i for i in hwp.ctrl_list if i.UserDesc == "수식"]:
        eq_list.append(ctrl.Properties.Item('VisualString'))
        
        # {equ}문자를 남기는 것은 일단은 배제
        #hwp.move_to_ctrl(ctrl)
        #hwp.MoveRight()
        #hwp.insert_text(r' {equ} ')

    return eq_list

def join_hwp_eq(eq_list : List[str]) -> List[str]:

    """
    추출한 수식 리스트를 긴 문자열로 합치는 함수
    
    문자열을 한번에 처리하기 위해서 수식들을 합쳐서 긴 문자열로 만든다.

    문자열이 너무 길면 나중에 Mathml 추출시 잘리기 때문에 1500자로 제한한다.

    Args:
        eq_list(List[str]): 한글 문서에서 추출한 수식 리스트

    Returns:
        List[str]: 길게 합쳐진 수식 문자열 리스트
    """
    
    SPLITPOINT = "#"
    MAXLENTH = 1500
    combined_eq = []
    current = []
    
    for s in eq_list:
        # 문자열을 추가했을 때 길이가 max_length를 넘는지 확인
        combined = SPLITPOINT.join(current + [s])  # 현재 리스트에 문자열 s를 추가한 후, 구분자로 결합
        if len(combined) > MAXLENTH:
            combined_eq.append(SPLITPOINT.join(current))  # 현재까지의 문자열을 구분자로 결합하여 저장
            current = [s]  # 새로운 문자열을 시작
        else:
            current.append(s)  # 기존 리스트에 문자열 추가
    
    if current:  # 마지막 남은 문자열 추가
        combined_eq.append(SPLITPOINT.join(current))
    
    return combined_eq

def parse_mathml_to_latex(combined_eq : List[str], hwp : Hwp) -> List[str]:

    """
    길게 합쳐진 수식 문자열 리스트를 길게 합쳐진 LaTex 리스트로 만드는 함수

    길게 합쳐진 수식 문자열을 수식 편집기로 열어 수식 ctrl을 만든다.

    해당 수식 ctrl을 Mathml로 추출 후 저장한다.

    Mathml -> asciimath -> Latex 변환과정을 거친다.


    Args:
        combined_eq(List[str]): 길게 합쳐진 수식 문자열 리스트

    Returns:
        List[str]: 길게 합쳐진 LaTex 리스트
    """

    combined_latex =[]
    
    for string in combined_eq:
        
        hwp.MovePos(3)            #문서 끝으로 이동
        action = "EquationCreate"
        pset = hwp.HParameterSet.HEqEdit
        pset.string = string
        hwp.HAction.Execute(action, pset.HSet)
        ctrl = hwp.LastCtrl

        hwp.select_ctrl(ctrl)
        mml_path = "eq.mml"
        hwp.export_mathml(mml_path)
        hwp.delete_ctrl(ctrl)
        
        mathml2tex = MathML2Tex()
        with open(mml_path) as f:
            mml_eq = f.read()
        tex_eq = mathml2tex.translate(mml_eq, network=True, from_file=False)
        combined_latex.append(tex_eq)

    combined_latex = [latex_to_unicode(text) for text in combined_latex]

    return combined_latex

def split_latex(combined_latex : List[str]) -> List[str]:

    """
    길게 합쳐진 LaTex 문자열 리스트를 자르는 함수

    길게 합쳐진 Latex 문자열들을 수식 자른 뒤 끝을 "$"로 감싼다

    LaTex 수식 리스트로 만든다
    

    Args:
        combined_latex(List[str]): 길게 합쳐진 LaTex 리스트

    Returns:
        List[str]: LaTex 수식 문자열 리스트
    """

    latex_list = []

    for latex in combined_latex:
        if latex.startswith("$") and latex.endswith("$"):
            latex = latex[1:-1]

        # splitpoint 기준으로 분할
        elements = latex.split("\\phantom{\\rule{0ex}{0ex}}")

        # 모든 요소를 앞뒤 $로 감싸기
        latex_list.extend([f"${elem}$" for elem in elements])
    
    return latex_list


  
