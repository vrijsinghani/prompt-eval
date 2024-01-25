# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Neuralami
"""
from .forms import HistoryForm
from .models import ModelResult
from .tasks import evaluate_task
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.conf import settings
from django.urls import reverse
from collections import defaultdict
from helpers import *
from markdown import markdown
from celery import current_task
from celery.result import AsyncResult
import requests, logging, openai, json

# Create your views here.
logger = logging.getLogger(__name__)  # <-- Add this line

def index(request):
    logger.debug('Got to index')
    # Page from the theme 
    return render(request, 'pages/index.html')


def evaluate(request):
    models = get_models()
    if request.method == 'POST':
        questions = request.POST.get('questions').split('\n')
        logger.debug(f"Questions (POST): {questions}")
        prompt = request.POST.get('prompt')
        logger.debug(f"Prompt (POST): {prompt}")
        models_selected = request.POST.getlist('models_selected')
        logger.debug(f"Models_selected (POST): {models_selected}")
        # Store values in the session
        request.session['questions'] = questions
        request.session['prompt'] = prompt
        request.session['models_selected'] = models_selected
        request.session.save()
        task = evaluate_task.delay(questions, prompt, models_selected)
        request.session['task_id'] = str(task.id)
        return JsonResponse({'task_id':str(task.id)})
    else:
        questions = request.session.get('questions', ['What is 1+1'])
        prompt = request.session.get('prompt', 'You are an assistant.')
        models_selected = request.session.get('models_selected', ['ollama/openchat'])
        #logger.debug(f"Models_selected (GET): {models_selected}")
        if 'results' in request.session:
            results = (request.session['results'])
            #logger.debug("got results in request.session")
        else:
            results = None
        #results=request.session.get('results',None)
         #logger.debug('Session data (GET): %s', request.session.items())
        #logger.debug(f"Results (GET): {results}")
        if 'results' in request.session:
            del request.session['results']
            #results=json.loads(results)

        context = {
            'models': models,
            'questions': '\n'.join(questions),
            'prompt': prompt,
            'models_selected': models_selected,
            'results': results,
#            'test_dict': {'key': 'value'},
            'segment': 'evaluate',
        }

        return render(request, 'pages/evaluate.html', context)

def task_status(request, task_id):
    task = AsyncResult(task_id)
    logger.debug(f"task.info: {task.info}")
    logger.debug(f"task.result: {task.result}")
    response = {
        'state': task.state,
        'current': 0,
        'total': 1,
        'status': 'PROGRESS...'
    }

    if task.ready():
        #print("GOT RESULT!")
        results = task.result
        request.session['results'] = results
        #logger.debug(f"task.results {results}")
        request.session.save()
        response['results'] = results

    else:

        if task.info is not None:
            if task.state == 'PROGRESS':
                response = {
                    'state': task.state,
                    'current': task.info.get('current', 0),
                    'total': task.info.get('total', 1),
                    'status': task.info.get('status', ''),
                    'current_model': task.info.get('current_model', '')
                }
            elif task.state != 'FAILURE':
                response = {
                    'state': task.state,
                    'current': task.info.get('current', 0),
                    'total': task.info.get('total', 1),
                    'status': task.info.get('status', '')
                }
            else:
                response = {
                    'state': task.state,
                    'current': 1,
                    'total': 1,
                    'status': str(task.info),
                }

    return JsonResponse(response)



def history(request):
    questions = ModelResult.objects.all().distinct()
    selected_question_ids = request.session.get('selected_question_ids', [])
    results = ModelResult.objects.all().order_by('timestamp')

    if request.method == 'POST':
        selected_question_ids = request.POST.getlist('question[]')
        request.session['selected_question_ids'] = selected_question_ids
        logger.debug(f"Selected question IDs: {selected_question_ids}")

        if 'delete' in request.POST:
            id_to_delete = request.POST.get('delete')
            ModelResult.objects.filter(id=id_to_delete).delete()
            messages.success(request, "Deleted successfully")
            return redirect('history')

        results = ModelResult.objects.filter(id__in=selected_question_ids).order_by('timestamp')
        logger.debug(f"Results: {results}")

    selected_questions = ModelResult.objects.filter(id__in=selected_question_ids)
    return render(request, 'pages/history.html', {'questions': questions, 'results': results, 'selected_questions': selected_questions})
