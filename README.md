# 공학인재 양성을 위한 멀티모달 기반 AI tutor, Learning Mate
<div align="center"> 
    <p align = "center">
        <img alt="러닝메이트로고" src="https://github.com/user-attachments/assets/a44ffc5d-4fdc-4f69-9f8d-996a7a328062" />
    </p>
</div>

## 목차
- [협업 기업](#협업-기업)
- [연구 및 프로젝트 성과](#연구-및-프로젝트-성과)
- [포스터](#포스터)
- [프로젝트 기획 배경](#프로젝트-기획-배경)
- [핵심 과제](#핵심-과제)
  - [개발 주제 및 내용](#개발-주제-및-내용)
  - [세부 내용](#세부-내용)
- [프로젝트 성과](#프로젝트-성과)
- [활용 방안](#활용-방안)
- [소개 영상](#소개-영상)
- [역할 분담](#역할-분담)
- [시스템 구조도](#시스템-구조도)
  - [Abstraction Ver.](#abstraction-ver)
  - [Detail Ver.](#detail-ver)


- [폴더 구조](#폴더-구조)
- [시연 영상](#시연-영상)
- [기타 문서](#기타-문서)

# 협업 기업

<table>
  <tr>
    <td align="center" style="border:none; vertical-align:top;" width="50%">
      <img src="https://github.com/user-attachments/assets/7ef16927-fe4f-4e13-8126-7ec9df0f7774" height="100"/><br />
      <h3>Uniwise</h3>
      <ul align="left">
        <li>2008년부터 온라인 교육 콘텐츠 플랫폼 운영</li>
        <li>대학인강 12만명, 학점은행제 1만명 회원 보유</li>
        <li>공학 및 이공계열 과목 254개 운영</li>
        <li>1.2만개 강의 영상 보유</li>
      </ul>
    </td>
    <td align="center" style="border:none; vertical-align:top;" width="50%">
      <img src="https://github.com/user-attachments/assets/5237b371-9e4a-44d4-af91-d8e20d376ec0" height="100"/><br />
      <h3>Lemong</h3>
      <ul align="left">
        <li>삼성, 쿠팡 출신 개발자가 설립한 AI 스타트업</li>
        <li>AI 기반 외식업 리뷰 관리 솔루션 ‘댓글몽’ 운영</li>
        <li>리뷰 통합 및 자동 응답 제공 서비스 운영</li>
      </ul>
    </td>
  </tr>
</table>


### 🤝 협업 형태
- 유니와이즈 : 문제점 도출 및 서비스 기획  
- 르몽 : AI 기술 자문 및 연구 개발 자문

---

### 연구 및 프로젝트 성과
<a href="" target="_blank">
    <img width="400" height ="246" alt="음성 인식 모델 경량화 연구" src="https://github.com/user-attachments/assets/44bcd70a-619f-4e12-b453-64f6dcdbd0de" /> <img width="400" alt="HWP 문서 파싱 및 전처리 방법 연구" src="https://github.com/user-attachments/assets/4aef9a9e-8b8a-45a9-82f7-8932704aa5fa" />


<br/> <br/> 

## 포스터

<div align="center"> 
    <p align = "center">
    <img src = "https://github.com/user-attachments/assets/48782425-02e0-474e-b33c-c404f4934e81" width = "555"/>
    </p>
</div>

## 프로젝트 기획 배경
기존 이러닝 플랫폼의 Q&A 시스템은 수강생의 질문에 대해 교수나 상담원이 직접 답변해야 해서 응답까지의 소요시간이 길다. 기업체에서 제공해준 통계 자료로부터 확인했던 것은 ‘학생들의 질문에 대한 답변까지 걸리는 소요 시간이 최소 하루 이상’이라는 것이다. 이러한 문제는 LLM 챗봇을 통해 자동화된 응답 시스템을 도입함으로써 일정 부분 해결 가능하다. 그러나 수학·과학 기반 공학 과목의 경우 텍스트 기반의 인문·사회 과목과 달리 공식, 수식, 화학식, 그래프, 도형 등 비정형 정보가 포함되어 있어 LLM이 직접 활용하기 어렵다. 이는 해당 정보들이 일반 텍스트가 아닌 복잡한 시각적 구조로 구성되어 있기 때문에 멀티모달 처리 역량이 요구되며 단순 텍스트 기반 LLM은 이러한 정보를 정확히 이해하고 반영하기 어렵다. 또한, LLM의 환각(hallucination) 문제를 방지하기 위해 강의 자료 기반 응답이 요구되지만 현재의 Q&A 시스템은 수식·도형 등 복잡한 데이터를 구조화하지 못해 도입이 제한적이다. 이에 따라, 이 프로젝트는 이러한 멀티모달 정보를 전처리 및 구조화하여 LLM이 참조 가능한 데이터로 변환하고 이를 기반으로 신뢰성 높은 응답을 제공할 수 있는 RAG 시스템을 구현하고자 한다.

# 핵심 과제
본 프로젝트는 학생들의 질문에 보다 신뢰성 있는 답변을 제공하고자 강의 자료를 바탕으로 복잡한 공학식 및 기호 등을 텍스트로 전처리한 것을 데이터베이스로 구축하고 이를 기반으로 RAG 시스템을 도입한다. 또한, 강의 주제와 긴밀하게 연관되거나 중요한 강의 내용에 대한 요약 영상을 자동으로 생성하는 파이프라인을 구현함으로써 수강생들의 강의 핵심 내용 파악을 돕는다. 이를 위해 한글(HWP) 및 강의 영상 데이터를 JSON으로 변환하는 데이터 전처리 솔루션을 개발하며 수식, 표, 공학 기호 등을 유지하는 LaTeX 변환, 수식이나 공학적 내용이 들어간 강의 음성 텍스트 변환(STT), 타임스탬프 기반 문장 구조화 기능을 개발한다.

## 개발 주제 및 내용
<img width="1012" alt="Learning Mate의 주요 개발 내용" src="https://github.com/user-attachments/assets/1aa0043a-f841-4c66-9ce4-63c3febaf412" />

### 세부 내용
### n. 강의 영상 음성 인식
<img width="1174" alt="강의 영상 음성 인식 결과" src="https://github.com/user-attachments/assets/ace4ceb6-0490-454e-a652-1832043dabaa" />


## 프로젝트 성과
### hwp 파일 내 수식 LaTex 변환 파이프라인 구축 및 처리를 위한 소요 시간 단축
<img width="1174" alt="hwp 파일 내 수식 LaTex 변환 파이프라인 구축 및 처리를 위한 소요 시간 단축" src="https://github.com/user-attachments/assets/e2447ea7-4307-41f5-b352-97ffab4caf96" />


### 이미지 분류 성능 개선
<img width="1174" alt="이미지 분류 성능 개선" src="https://github.com/user-attachments/assets/44a327ce-de2f-42fe-b33b-6598863238b8" />


### 음성 인식 일반화 성능 향상 및 VRAM 효율화
<img width="1174" alt="음성 인식 일반화 성능 향상 및 VRAM 효율화" src="https://github.com/user-attachments/assets/09e3d32d-08d4-49b0-831d-3dedf129f62d" />



# 활용 방안
### 기능 활용 방안1 - 실시간 질의 응답 시스템
<img width="674" alt="image" src="https://github.com/user-attachments/assets/a61d153b-b071-4695-a9d4-24746b421890" /> <br>


### 기능 활용 방안2 - 난이도 별 자동화 문제은행 제공
<img width="674" alt="난이도 별 자동화 문제은행" src="https://github.com/user-attachments/assets/cee9e3e5-5083-49a8-a615-f6f0be2590cd" /> <br>


### 기능 활용 방안3 - “이 개념, 어디서 설명했더라?” 해결
<img width="674" alt="image" src="https://github.com/user-attachments/assets/5b3e8dcb-c257-41fa-9271-85c8aa557f22" /> <br>


<br/>

## 소개 영상


<br/>

## 역할 분담

<table>
    <tr align="center">
        <td style="min-width: 100px;">
            <a href="https://github.com/blue-ladder">
              <img src="https://github.com/user-attachments/assets/a4a3548c-9576-4ebb-b99e-91c021052a10" width="100">
              <br />
              <b>차민수</b>
            </a> 
            <br/>
        </td>
        <td style="min-width: 100px;">
            <a href="https://github.com/UH3135">
              <img src="https://github.com/user-attachments/assets/5d9cb075-9fbc-4b88-a009-9a28f9bad5bd" width="120">
              <br />
              <b>정의현</b>
            </a>
            <br/>
        </td>
        <td style="min-width: 100px;">
            <a href="https://github.com/handsomem1n">
              <img src="https://github.com/user-attachments/assets/e7557acd-d289-4ddb-a2f4-7cd02fc8ea22" width="110">
              <br />
              <b>한승민(팀장) </b>
            </a> 
            <br/>
        </td>
        <td style="min-width: 100px;">
            <a href="https://github.com/imaboybut">
              <img src="https://github.com/user-attachments/assets/b74ff799-2c55-48b1-a28f-537c68bcc8a3" width="130">
              <br />
              <b>정진우</b>
            </a> 
            <br/>
        </td>
    </tr>
  <tr align="center">
    <td>
      한글(HWP)데이터 추출<br />수식 및 텍스트 전처리<br />
    </td>
    <td>
      이미지 OCR <br />프로젝트 관리<br />공유 문서 관리
    </td>
    <td>
      음성 인식 모델 개발<br />프로젝트 기획<br />일정 관리
    </td>
    <td>
      모델 추론 파이프라인 구축<br />추론 데이터 후처리<br />
    </td>
  </tr>
</table>


<br/>

## 시스템 구조도
### Abstraction Ver.
<br/>

<div> 
    <p>
    <img src = "https://github.com/user-attachments/assets/00106595-3290-4aa8-9c5b-199a8681d854" width = 90%/>
    </p>
</div>

### Detail Ver.
<br/>

<div> 
    <p>
    <img src = "https://github.com/user-attachments/assets/6847177f-c322-4ac8-9bb9-69d7f1bf678a" width = 90%/>
    </p>
</div>

<br/>


<br/>

### ETC
|Purpose|Platforms|
|-|-|
|**Communication**| ![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=Discord&logoColor=white) ![Google Meet](https://img.shields.io/badge/Google_Meet-00897B?style=for-the-badge&logo=google-meet&logoColor=white) ![KakaoTalk](https://img.shields.io/badge/KakaoTalk-FFCD00?style=for-the-badge&logo=KakaoTalk&logoColor=000000)
|**Version Control**|![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)
|**Project Management**| ![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white) ![Google Docs](https://img.shields.io/badge/Google_Docs-4285F4?style=for-the-badge&logo=google-docs&logoColor=white) ![Google Sheets](https://img.shields.io/badge/Google_Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)



<br />


<br/>

## 폴더 구조
```
├── 📂 FR1

├── 📂 FR2

├── 📂 FR3

└── 📕 README.md
```

<br/>



### [수행 계획서]()
[수행계획서.pdf](https://github.com/user-attachments/files/20263831/default.pdf)


### 시연 영상

#### 수식 OCR 시연
[![FR1 - 수식 OCR 시연](https://img.youtube.com/vi/-VvAF1rPMuI/0.jpg)](https://www.youtube.com/watch?v=-VvAF1rPMuI)  

#### 한글 파일 데이터 추출 및 수식 LaTeX 변환
[![FR1 - 한글 파일 데이터 추출 및 수식 LaTeX 변환](https://img.youtube.com/vi/zxh2DVamLao/0.jpg)](https://www.youtube.com/watch?v=zxh2DVamLao)  

#### Latex 수식 추출 확인
[![FR1 - Latex 수식 추출 확인](https://img.youtube.com/vi/j2N-JqMUSc4/0.jpg)](https://www.youtube.com/watch?v=j2N-JqMUSc4)


#### 중요 영상 생성 시연 영상
[![FR3 - 중요 영상 생성 시연 영상](https://www.youtube.com/watch?v=I_m72ifjmNI/0.jpg)]
<hr>

### 프로젝트 실행방법
```
git clone https://github.com/kookmin-sw/capstone-2025-36.git
cd capstone-2025-36
```
 [FR-1 실행방법](https://github.com/kookmin-sw/capstone-2025-36/edit/main/FR1/README.md)
