import re

HANCOMEQ_FIX_MAP = [
    # 단순 문자열 치환
    {
        "type": "plain",
        "pattern": "ℤ",
        "replacement": r"\mathbb{Z}"
    },
    {
        "type": "plain",
        "pattern": "ℝ",
        "replacement": r"\mathbb{R}"
    },
    {
        "type": "plain",
        "pattern": "ℕ",
        "replacement": r"\mathbb{N}"
    },
    {
        "type": "plain",
        "pattern": "ℍ",
        "replacement": r"\mathbb{H}"
    },
    {
        "type": "plain",
        "pattern": "ℚ",
        "replacement": r"\mathbb{Q}"
    },
    {
        "type": "plain",
        "pattern": "ℂ",
        "replacement": r"\mathbb{C}"
    },
    {
        "type": "plain",
        "pattern": "ℙ",
        "replacement": r"\mathbb{P}"
    },
    {
        "type": "plain",
        "pattern": r"Vec",
        "replacement": r"\mathbb"
    },
    {
        "type": "plain",
        "pattern": "∊",
        "replacement": r" IN"
    },
    {
        "type": "plain",
        "pattern": "∤",
        "replacement": r"not`vert"
    },
    {
        "type": "plain",
        "pattern": "not=",
        "replacement": r"neq"
    },
    {
        "type": "plain",
        "pattern": "!=",
        "replacement": r"neq"
    },
    {
        "type": "plain",
        "pattern": "not",
        "replacement": r"not`"
    },
    {
        "type": "plain",
        "pattern": "#",
        "replacement": r"`ENTER`"
    },
    {
        "type": "plain",
        "pattern": "~",
        "replacement": r"```"
    },
    {
        "type": "plain",
        "pattern": r"{it}",
        "replacement": r"{i`t}"
    }
]

# LaTeX 오류 변환 맵
LATEX_FIX_MAP = [
    # 단순 문자열 치환
    {
        "type": "plain",
        "pattern": r"\text{not}\u2006\\",
        "replacement": r"\n"
    },
    {
        "type": "plain",
        "pattern": r" \text{ENTER} ",
        "replacement": r"\\"
    },
    {
        "type": "plain",
        "pattern": r"\ne =",
        "replacement": r"\not\equiv "
    },
    {
        "type": "plain",
        "pattern": r"\nsubset",
        "replacement": r"\not\subset "
    },
    {
        "type": "plain",
        "pattern": r"\nsupset",
        "replacement": r"\not\supset "
    },
    {
        "type": "plain",
        "pattern": r"\nin",
        "replacement": r"\not\in "
    }
    {
        "type": "plain",
        "pattern": "{i t}",
        "replacement": "{it}"
    },
    {
        "type": "plain",
        "pattern": "            ",
        "replacement": r"\qquad "
    },
    {
        "type": "plain",
        "pattern": "      ",
        "replacement": r"\quad "
    },    
    {
        "type": "plain",
        "pattern": " ",
        "replacement": r"\,"
    },


    # 정규표현식 치환
    {
        "type": "regex",
        "pattern": re.compile(r"\\text\{mathbb([A-Za-z])\}"),
        "replacement": lambda m: fr"\mathbb{{{m.group(1)}}}"
    },

    {
        "type": "regex",
        "pattern": re.compile(r"\{\{(\\mid|])\s*\}_\{(.*?)\}\}\^\{(.*?)\}"),
        "replacement": lambda m: r"{%s}_{%s}^{%s}" % (m.group(1), m.group(2), m.group(3))
    }
]

def _prepare_plain_mapping(mapping_list):
    plain_map = {entry["pattern"]: entry["replacement"] for entry in mapping_list if entry["type"] == "plain"}
    if plain_map:
        plain_pattern = re.compile("|".join(map(re.escape, plain_map.keys())))
    else:
        plain_pattern = None
    return plain_map, plain_pattern

# ▶ 준비
HANCOMEQ_FIX_PLAIN_MAP, HANCOMEQ_FIX_PLAIN_PATTERN = _prepare_plain_mapping(HANCOMEQ_FIX_MAP)
LATEX_FIX_MAP_PLAIN_MAP, LATEX_FIX_MAP_PLAIN_PATTERN = _prepare_plain_mapping(LATEX_FIX_MAP)

# ▶ 고속 변환 함수
def _apply_fast_mapping(text: str, plain_map, plain_pattern, full_mapping) -> str:
    if plain_pattern:
        text = plain_pattern.sub(lambda m: plain_map[m.group(0)], text)

    # regex만 따로 적용
    for entry in full_mapping:
        if entry["type"] == "regex":
            text = entry["pattern"].sub(entry["replacement"], text)

    return text

def apply_fix_HancomEq(text: str) -> str:
    """
    한컴 수식 오류 FIX
    
    """
    return _apply_fast_mapping(text, HANCOMEQ_FIX_PLAIN_MAP, HANCOMEQ_FIX_PLAIN_PATTERN, HANCOMEQ_FIX_MAP)

def apply_fix_Latex(text: str) -> str:
    """
    LaTeX 수식 오류 FIX 
    """
    if "text{ENTER}" in text:
        text = r"\begin{aligned}" + text + r"\end{aligned}"


    return _apply_fast_mapping(text, LATEX_FIX_MAP_PLAIN_MAP, LATEX_FIX_MAP_PLAIN_PATTERN, LATEX_FIX_MAP)
