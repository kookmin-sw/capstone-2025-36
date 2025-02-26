from langchain_core.documents import Document
import json



def save_json(data, filename="lecture_data.json"):
    """
    JSON 파일 저장 함수
    """
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"JSON 파일이 저장되었습니다: {filename}")



def load_json_data(json_path:str) -> Document:
    """
    JSON 파일을 읽고 LangChain 문서 리스트로 변환하는 함수
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for doc in data["documents"]:
        content = doc["content"]
        metadata = doc["metadata"]
        
        # LangChain 문서 객체 생성
        document = Document(
            page_content=content,
            metadata={
                "subject": metadata["subject"],
                "instructor": metadata["instructor"]
            }
        )
        documents.append(document)
    
    return documents