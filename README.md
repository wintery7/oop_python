# oop_python

파이썬 객체지향 프로그래밍(OOP) 실습 저장소입니다.

## 내용

| 파일 | 설명 |
| --- | --- |
| `1_class_object_실습.ipynb` | 클래스와 객체 |
| `2_생성자소멸자_실습.ipynb` | 생성자와 소멸자 |
| `3_접근제어_실습.ipynb` | 접근 제어 |
| `class_object_복습테스트.ipynb` | 클래스/객체 복습 테스트 |
| `생성자소멸자_복습학습지.ipynb` | 생성자/소멸자 복습 학습지 |
| `object_ex01.py` | 객체 예제 |
| `employee_payroll_01.py` | 직원 급여 예제 |
| `check_maeulsup.py` | 공공데이터포털 전통마을숲 API 확인 스크립트 |

## 실행 환경 설정

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## API 키 설정

`check_maeulsup.py` 는 공공데이터포털 인증키가 필요합니다.

1. `.env.example` 을 복사해서 `.env` 파일을 만듭니다.
2. `.env` 에 실제 키를 입력합니다. (`.env` 는 `.gitignore` 에 등록되어 있어 GitHub에 올라가지 않습니다.)
