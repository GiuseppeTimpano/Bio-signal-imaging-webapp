from sqlalchemy.orm import Session
from flask_webapp import engine, Bioimage
from sqlalchemy import select

with Session(engine) as session:
    b = Bioimage(id = 136531, patient = 'Giuseppe')
    session.add(b)
    session.commit()

session2 = Session(engine)
print(select(Bioimage))