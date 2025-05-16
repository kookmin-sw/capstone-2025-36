import sys
import ffmpeg # 여기서 ffmpeg를 임포트합니다.

print(f"--- ffmpeg 모듈 상세 정보 ---")
print(f"ffmpeg 객체: {ffmpeg}")
print(f"ffmpeg 타입: {type(ffmpeg)}")

# __file__ 속성이 있는지, 있다면 그 값은 무엇인지 안전하게 확인
print(f"ffmpeg.__file__ (getattr 사용): {getattr(ffmpeg, '__file__', '속성 없음')}")

# 패키지인 경우 __path__ 속성을 가질 수 있음
print(f"ffmpeg.__path__ (getattr 사용): {getattr(ffmpeg, '__path__', '속성 없음')}")

print(f"dir(ffmpeg) 결과 일부: {dir(ffmpeg)[:20]}") # 너무 길 수 있으니 일부만 출력

print(f"\n--- sys.path 정보 ---")
print(sys.path)

print(f"\n--- sys.modules['ffmpeg'] 정보 ---")
if 'ffmpeg' in sys.modules:
    print(f"sys.modules['ffmpeg'] 객체: {sys.modules['ffmpeg']}")
    print(f"sys.modules['ffmpeg'].__file__ (getattr 사용): {getattr(sys.modules['ffmpeg'], '__file__', '속성 없음')}")
else:
    print("sys.modules에 'ffmpeg' 없음")

# 실제 ffmpeg.input 사용 시도
try:
    print("\n--- ffmpeg.input 호출 시도 ---")
    # 실제 비디오 파일 경로 대신 테스트용으로 간단한 문자열을 넣어보세요.
    # 여기서도 AttributeError가 발생하는지 확인합니다.
    ffmpeg.input('test.mp4') 
    print("ffmpeg.input 호출 성공 (테스트용)")
except AttributeError as e:
    print(f"AttributeError 발생: {e}")
except Exception as e:
    print(f"기타 예외 발생: {e}")