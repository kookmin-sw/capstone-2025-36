import re
from typing import List
from pyhwpx import Hwp
from pathlib import Path
from py_asciimath.translator.translator import MathML2Tex
from utils.constants import UNICODE_LATEX_MAP, LATEX_UNICODE_MAP
from utils.Exception_Fix import apply_fix_HancomEq, apply_fix_Latex
from utils.logger import init_logger

logger = init_logger(__file__, "DEBUG")

def extract_latex_list(hwp: Hwp, eq_list : List[str]) -> List[str] :
    
    """
    hwp에서 latex 수식 리스트를 추출하는 함수

    Args:
        hwp(Hwp): 수식을 추출하고 싶은 한글 파일

    Returns:
        List[str]:LaTex 수식 문자열 리스트
    """
    
    combined_eq_list = _join_hwp_eq(eq_list)
    combined_latex = _parse_mathml_to_latex(combined_eq_list, hwp)
    latex_list = _split_latex(combined_latex)
    return latex_list

def _join_hwp_eq(eq_list : List[str]) -> List[str]:

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
    combined_eq_list = []
    current = []
    
    try:
        for eq in eq_list:
            valid_eq = apply_fix_HancomEq(eq) 
            # 문자열을 추가했을 때 길이가 max_length를 넘는지 확인
            combined = SPLITPOINT.join(current + [valid_eq])  # 현재 리스트에 문자열 s를 추가한 후, 구분자로 결합
            if len(combined) > MAXLENTH:
                logger.info(f"문자열 분할: 현재 길이가 {len(combined)}로 최대 길이({MAXLENTH})를 초과하여 분할합니다.")
                combined_eq_list.append(SPLITPOINT.join(current))  # 현재까지의 문자열을 구분자로 결합하여 저장
                current = [valid_eq]  # 새로운 문자열을 시작
            else:
                current.append(valid_eq)  # 기존 리스트에 문자열 추가

        if current:  # 마지막 남은 문자열 추가
            combined_eq_list.append(SPLITPOINT.join(current))

        return combined_eq_list
    
    except Exception as e:
        logger.exception(f"수식 문자열 병합 중 오류 발생 : (Error: {e})")
        return []
    
def process_equations_group(combined_eq: str , hwp) -> List[str]:
    """
    eq_list에 담긴 수식들을 delimiter로 연결하여 한 번에 변환을 시도하고,
    문제가 있을 경우 divide & conquer 방식으로 문제 수식을 격리하여 처리합니다.
    
    Args:
        eq_list (List[str]): 개별 수식 문자열 리스트
        hwp: 한/글 인터페이스 객체
        mathml2tex: MathML -> LaTeX 변환 객체
        delimiter (str): 수식 연결에 사용되는 구분자
        
    Returns:
        List[str]: 각 수식에 대해 변환된 LaTeX 문자열 리스트 
                   (오류 발생 시 "ERROR" 문자열 포함)
    """
    # 한 번에 그룹 전체를 변환 시도
    mathml2tex = MathML2Tex()
    SPLITPOINT = "#"
    try:
        # 문서 끝으로 이동 및 수식 컨트롤 생성
        hwp.MovePos(3)
        action = "EquationCreate"
        pset = hwp.HParameterSet.HEqEdit
        pset.string = combined_eq
        hwp.HAction.Execute(action, pset.HSet)
        ctrl = hwp.LastCtrl
        if not ctrl:
            logger.error("ValueError : Equation control creation failed for combined equation.")
            raise
        
        hwp.select_ctrl(ctrl)
        mml_path = "eq.mml"
        hwp.export_mathml(mml_path)
        hwp.delete_ctrl(ctrl)
        
        with open(mml_path) as f:                 
            mml_eq = f.read()
        
        if not mml_eq:
            logger.error("ValueError : Exported MathML is empty for combined equation.")
            raise
        
        latex_eq = mathml2tex.translate(mml_eq, network=True, from_file=False)
        return latex_eq
    
    except Exception as e:
        # 만약 단일 수식에서 발생한 오류라면 예외 처리하고 "ERROR" 반환
        eq_list = combined_eq.split(SPLITPOINT)
        if len(eq_list) == 1:
            return f"$ErrorEquation: {eq_list[0]}$"
        else:
            # divide & conquer 방식: 그룹을 반으로 분할하여 각각 재시도
            mid = len(eq_list) // 2
            left = process_equations_group(SPLITPOINT.join(eq_list[:mid]), hwp)
            right = process_equations_group(SPLITPOINT.join(eq_list[mid:]), hwp)
            return left[:-1] + "\\phantom{\\rule{0ex}{0ex}}"+ right[1:]

def _parse_mathml_to_latex(combined_eq_list: List[str], hwp) -> List[str]:
    """
    길게 합쳐진 수식 문자열 리스트를 개별 LaTeX 수식 문자열 리스트로 변환하는 함수.
    
    하나의 문자열 내에 여러 수식이 '#'로 연결되어 있으며,
    문서 내 수식 편집기를 통해 MathML로 추출 후 asciimath -> LaTeX 변환하는 과정을 거칩니다.
    변환 과정에서 한 수식이라도 문제가 있으면 divide & conquer 방식으로 오류 수식을 격리하여,
    나머지 정상 수식은 올바르게 변환할 수 있도록 합니다.
    
    Args:
        combined_eq_list (List[str]): 길게 합쳐진 수식 문자열 리스트
        hwp: 한/글 인터페이스 객체
        
    Returns:
        List[str]: 개별 LaTeX 수식 문자열 리스트 (오류 발생 시 "ERROR" 포함)
    """
    combined_latex_list = []
    
    for combined_eq in combined_eq_list:
        # 먼저 '#'를 기준으로 개별 수식 리스트로 분리하여 처리
        latex_eq = process_equations_group(combined_eq, hwp)
        combined_latex_list.append(latex_eq)
    
    # 최종 LaTeX 문자열을 유니코드 처리 (필요 시)
    return combined_latex_list

def _split_latex(combined_latex : List[str]) -> List[str]:

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

    try:
        for latex in combined_latex:

            if latex.startswith("$") and latex.endswith("$"):
                latex = latex[1:-1].strip()

            # splitpoint 기준으로 분할
            elements = latex.split("\\phantom{\\rule{0ex}{0ex}}")

            # 모든 요소를 앞뒤 $로 감싸기
            latex_list.extend([f"${apply_fix_Latex(elem)}$" for elem in elements])
        
        return latex_list
    
    except Exception as e:
        logger.exception(f"Latex 수식 분할 중 오류 발생 (Error: {e})")
        return []  # 예외 발생 시 안전한 빈 리스트 반환

