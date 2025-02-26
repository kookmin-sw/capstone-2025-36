from typing import List
import json
import re


def preprocess_markdown(md_text: str) -> List[str]:
    """
    Markdown을 전처리하여 깨끗한 텍스트로 변환하는 함수
    """
    subject, instructor = extract_lecture_info(md_text)
    lines = md_text.split("\n")
    processed_text = []
    current_page = []
    
    def add_page():
        """
        현재 페이지 내용을 저장하고 페이지 구분을 추가
        """
        if current_page:
            processed_text.append("  ".join(current_page))
            current_page.clear()

    for line in lines:
        line = line.strip()

        # 불필요한 기호 및 공백 제거
        line = re.sub(r"\s+", " ", line)
        line = re.sub(r"[-—]+", "", line)
        line = re.sub(r"\|", "", line)
        line = re.sub(r"^\d+\.$", "", line)

        # 의미 없는 빈 줄 제거
        if line and not re.match(r"^\s*$", line):
            if re.match(r"^[ⅠⅡⅢⅣⅤ]+", line):
                add_page()
            current_page.append(line)

    add_page()  # 마지막 페이지 추가

    return subject, instructor, "\n".join(processed_text)


def extract_lecture_info(md_text):
    """
    Markdown 본문에서 강의 주제와 강사명을 추출하는 함수
    """
    # 강의 주제 찾기
    subject_match = re.search(r'(\d+강[.\s]+)(.+)', md_text)
    subject = subject_match.group(2).strip() if subject_match else "Unknown Subject"

    # 강사명 찾기
    instructor_match = re.search(r'[-–]\s*([\w\s]+ 교수)[-–]', md_text)
    instructor = instructor_match.group(1).strip() if instructor_match else "Unknown Instructor"

    return subject, instructor