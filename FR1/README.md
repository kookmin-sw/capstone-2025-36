# 프로젝트 소개
hwp로 된 강의 자료에 포함된 **복잡한 표나 이미지**를 정보나 순서의 손실이 없도록 **JSON 포맷으로 변환하는 전처리 모듈**입니다.

## Result
- Image parsing
- Table parsing

## File Structure

```
hwp-to-html-parser/
│── assets/                      # HWP 파일 저장 디렉토리
│   ├── input/                   # 원본 HWP 파일 저장
│   │   ├── sample1.hwp
│   │   ├── sample2.hwp
│   ├── output/                  # 변환된 JSON/HTML 파일 저장
│   │   ├── sample1.html
│   │   ├── sample1.json
│── src/
│   ├── parsers/                 # 데이터 파싱 관련 모듈
│   │   ├── clipboard.py         # clipboard에서 html 추출
│   │   ├── table_parser.py      # 테이블 변환
│   │   ├── latex_parser.py.     # LaTeX 변환
│   │   ├── data_cleaner.py      # 데이터 전처리 (공백/특수문자 제거) 및 Metadata 추가
│   │   ├── image_ocr.py         # 이미지 → 텍스트 (OCR)
│   │   ├── json_formatter.py    # JSON 변환 및 저장
│   │   ├── process_hwp_docs.py  # hwp automation api 컨트롤
│   │   ├── __init__.py
│   ├── utils/                   # 유틸리티 함수 모음
│   │   ├── file_handler.py      # 파일 로드 관련 모듈 (pickling 등)
│   │   ├── logger.py            # 로깅 설정
│   │   ├── constants.py         # 상수 관리
│   │   ├── __init__.py
│   ├── main.py                  # 프로그램 실행 진입점
│── docs/                         # 문서화
│   ├── README.md
│   ├── API_DOCS.md
│── .pre-commit-config.yaml       # 코드 스타일 자동 적용
│── .gitignore                    # Git에서 제외할 파일 목록
│── pyproject.toml                 # 패키지 및 도구 설정
│── requirements.txt              # Python 패키지 의존성 목록
│── LICENSE                       # 라이선스 파일
│── README.md                     # 프로젝트 개요
```

### 환경 설명

Windows 기반의 환경에서만 HWP to Json 변환이 가능합니다.

1. pyhwp 패키지 설치

```
pip install --pre pyhwp
```

2. 파이썬 패키지 설치

```
pip install -r requirements.txt
```

3. assets Directory 생성
   - assets 파일 아래에 input 폴더 안에 모든 hwp 파일을 담아둡니다.

4-1. Python 실행

```
python FR1/src/main.py
```

4-2. Streamlit 실행 (이미지 변환)

```
streamlit run app.py
```

## Project Structure
![Image](https://github.com/user-attachments/assets/ea1ecba7-46de-4a48-909f-535fe3df87d9)

