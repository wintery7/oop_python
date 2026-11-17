# 학생 리스트 (Students)를 선언해 주세요. 5명의 학생정보를 아래 속성으로 저장하세요
# 학생은 이름(name), 국어(korean),영어(english),수학(math),과학(science)속성갖는다

students = [{"name":"MINJAE", "korean": 100, "english":100, "math":100, "science":100},
            {"name":"YUMI", "korean": 90, "english":90, "math":90, "science":90},
            {"name":"JAEHO", "korean": 80, "english":80, "math":80, "science":80},
            {"name":"JEONGHYUN", "korean": 70, "english":70, "math":70, "science":70},
            {"name":"JUNYOUNG", "korean": 60, "english":60, "math":60, "science":60},
            ]

class AttendenceBook:
    def __init__(self, students):
        self.students = students

    def print_names(self):
        print(*(s["name"] for s in students if s.get("name")), sep="\n")

attendenceBook = AttendenceBook(students=students)
attendenceBook.print_names()
