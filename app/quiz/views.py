from aiohttp_apispec import querystring_schema, request_schema, response_schema
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from aiohttp.web_exceptions import HTTPNotFound, HTTPUnauthorized, HTTPForbidden, HTTPConflict, HTTPBadRequest
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


# # TODO: добавить проверку авторизации для этого View 
# class ThemeAddView(View):
#     # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
#     #!! DONE
#     async def post(self):
#         title = (await self.request.json())[
#             "title"
#         ]  # TODO: заменить на self.data["title"] после внедрения валидации
#             #!! DONE
#         # TODO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
#         #!! DONE
#         theme = await self.store.quizzes.create_theme(title=title)
#         return json_response(data=ThemeSchema().dump(theme))


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema, 200)
    async def post(self):
        data = await self.request.json()
        try:
            title = data['title']
        except KeyError:
            raise HTTPBadRequest

        theme_exist = await self.store.quizzes.get_theme_by_title(title=title)
        if theme_exist:
            raise HTTPConflict
        
        theme = await self.store.quizzes.create_theme(title=title)
        
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema, 200)
    async def get(self):
        themes = await self.request.app.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(theme) for theme in themes]
        return json_response(data={'themes':raw_themes})


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        data = await self.request.json()
        title = data['title']
        theme_id = data['theme_id']
        answers = data['answers']

        flag = 0
        for answer in answers:
            if answer['is_correct'] == True:
                flag += 1
            if flag > 1:
                raise HTTPBadRequest
            
        if flag == 0:
                raise HTTPBadRequest    
            
        if len(answers) == 1:
            raise HTTPBadRequest
        
        theme_exist = await self.store.quizzes.get_theme_by_id(id_=theme_id)
        if not theme_exist:
            raise HTTPNotFound

        question_exist = await self.store.quizzes.get_question_by_title(title=title)
        if question_exist:
            raise HTTPConflict
        
        question = await self.store.quizzes.create_question(title=title, theme_id=theme_id, answers=answers)
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema, 200)
    async def get(self):

        try:
            theme_id = self.request.query['theme_id']
        except KeyError:
            theme_id = 0
        
        questions = await self.request.app.store.quizzes.list_questions(int(theme_id))
        if not questions:
            return json_response(data={'questions': questions})
        
        raw_questions = [QuestionSchema().dump(question) for question in questions]
        return json_response(data={'questions': raw_questions})
    