from math import ceil
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.dbfactory import get_db
from app.schema.board import BoardCreate, NewReply
from app.service.board import BoardService, get_board_data, process_upload, FileService

board_router = APIRouter()
templates = Jinja2Templates(directory='views/templates')


@board_router.get('/list/{cpg}', response_class=HTMLResponse)
async def list(req: Request, cpg: int, db: Session = Depends(get_db)):
    try:
        stpgb = int((cpg - 1) / 10) * 10 + 1
        bdlist, cnt = BoardService.select_board(db, cpg)
        allpage = ceil(cnt / 25)
        return templates.TemplateResponse('board/list.html',
                                          {'request': req, 'bdlist': bdlist, 'cpg': cpg,
                                           'stpgb': stpgb, 'allpage': allpage, 'baseurl': '/board/list/'})
    except Exception as ex:
        print(f'▷▷▷ list에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.get("/list/{ftype}/{fkey}/{cpg}", response_class=HTMLResponse)
async def find(req: Request, cpg: int, ftype: str, fkey: str, db: Session = Depends(get_db)):
    try:
        stpgb = int((cpg - 1) / 10) * 10 + 1
        bdlist, cnt = BoardService.find_board(db, ftype, '%'+fkey+'%', cpg)
        allpage = ceil(cnt / 25)
        return templates.TemplateResponse('board/list.html',
                                          {'request': req, 'bdlist': bdlist, 'cpg': cpg,
                                           'stpgb': stpgb, 'allpage': allpage,
                                           'baseurl': f'/board/list/{ftype}/{fkey}/'})
    except Exception as ex:
        print(f'▷▷▷ find에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.get("/write", response_class=HTMLResponse)
async def write(req: Request):
    if 'logined_uid' not in req.session:  # 로그인하지 않으면 글쓰기 금지
        return RedirectResponse('/member/login', 303)

    return templates.TemplateResponse('board/write.html', {'request': req})


@board_router.post('/write')
async def writeok(board: BoardCreate = Depends(get_board_data),
                  files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        print(board)
        attachs = await process_upload(files)
        print(attachs)
        if FileService.insert_board(board, attachs, db):
            return RedirectResponse('/board/list/1', 303)

    except Exception as ex:
        print(f'▷▷▷writeok 오류발생 {str(ex)}')
        return RedirectResponse('/member/error', 303)


@board_router.get("/view/{bno}", response_class=HTMLResponse)
async def view(req: Request, bno: int, db: Session = Depends(get_db)):
    try:
        boards = BoardService.selectone_board(bno, db)
        return templates.TemplateResponse('board/view.html',
                                          {'request': req, 'boards': boards})
    except Exception as ex:
        print(f'▷▷▷ view에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.get('/update')
async def modify(req: Request):
    return templates.TemplateResponse('board/update.html', {'request': req})


@board_router.post("/reply", response_class=HTMLResponse)
async def replyok(reply: NewReply, db: Session = Depends(get_db)):
    try:
        if BoardService.insert_reply(db, reply):
            return RedirectResponse(f'/board/view/{reply.bno}', 303)
    except Exception as ex:
        print(f'▷▷▷ replyok에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.post("/rreply", response_class=HTMLResponse)
async def rreplyok(reply: NewReply, db: Session = Depends(get_db)):
    try:
        if BoardService.insert_rreply(db, reply):
            return RedirectResponse(f'/board/view/{reply.bno}', 303)
    except Exception as ex:
        print(f'▷▷▷ rreplyok에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.delete("/view/{bno}")
async def delete_board(bno: int, db: Session = Depends(get_db)):
    try:
        result = BoardService.delete_board(db, bno)
        if result.rowcount > 0:
            return {"message": "게시물이 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="게시물이 존재하지 않거나 이미 삭제되었습니다.")
    except SQLAlchemyError as ex:
        print(f'▷▷▷ delete_board에서 오류 발생: {str(ex)}')
        raise HTTPException(status_code=500, detail=f"삭제 중 오류가 발생했습니다: {str(ex)}")