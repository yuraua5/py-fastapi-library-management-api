from fastapi import FastAPI, Depends, HTTPException
from fastapi_pagination import Page, paginate, add_pagination
from sqlalchemy.orm import Session

import crud
import schemas
from db.database import SessionLocal

app = FastAPI()
add_pagination(app)


def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/authors/", response_model=Page[schemas.Author])
def read_authors(db: Session = Depends(get_db)):
    return paginate(crud.get_all_authors(db))


@app.get("/authors/{author_id}", response_model=schemas.Author)
def read_single_author(author_id: int, db: Session = Depends(get_db)):
    db_author = crud.get_author_by_id(db, author_id=author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found.")

    return db_author


@app.post("/authors/", response_model=schemas.Author)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    db_author = crud.get_author_by_name(db=db, name=author.name)

    if db_author:
        raise HTTPException(status_code=400, detail="This name is already in use.")
    return crud.create_author(db=db, author=author)


@app.get("/books/", response_model=Page[schemas.Book])
def read_books(author_id: str | None = None, db: Session = Depends(get_db)):
    return paginate(crud.get_books_list(db=db, author_id=author_id))


@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db=db, book=book)
