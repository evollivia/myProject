from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.model.music import Mpfile

# 데이터베이스 URL을 실제 값으로 바꿔주세요
DATABASE_URL = 'sqlite:///C:/Users/cloud6a/Documents/projects2024/project/db.sqlite3'  # SQLite DB 파일의 경로

engine = create_engine(DATABASE_URL, echo=True)  # echo=True로 설정하면 SQL 쿼리가 로그에 출력됩니다.

# "Session" 클래스 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 세션 생성
session = SessionLocal()

# Mpfile 인스턴스 생성
new_mp3file = Mpfile(
    name='안예은',
    title='문어의 꿈',
    genre='가요',
    country='한국',
    mp3_path='/static/music/문어의 꿈 - 안예은.mp3',  # 실제 파일 경로로 교체
    img_path='/static/img/totoro.png'  # 실제 파일 경로로 교체
)

# 인스턴스를 세션에 추가하고 커밋
try:
    session.add(new_mp3file)
    session.commit()
except Exception as e:
    session.rollback()
    print(f"An error occurred: {e}")
finally:
    # 세션 닫기
    session.close()
