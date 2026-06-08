import json
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Tarefa


def _serializar_tarefa(tarefa):
    return {
        'id': tarefa.id,
        'titulo': tarefa.titulo,
        'descricao': tarefa.descricao,
        'status': tarefa.status,
        'prioridade': tarefa.prioridade,
        'data_criacao': tarefa.data_criacao,
        'data_entrega': tarefa.data_entrega,
        'usuario_responsavel': (
            tarefa.usuario_responsavel.nome
            if tarefa.usuario_responsavel else None
        ),
    }


def _queryset_para_lista(qs):
    return [_serializar_tarefa(t) for t in qs.select_related('usuario_responsavel')]


def listar_tarefas(request):
    tarefas = Tarefa.objects.select_related('usuario_responsavel').all()
    return JsonResponse([_serializar_tarefa(t) for t in tarefas], safe=False)


def listar_tarefas_por_status(request, status):
    status_validos = [choice[0] for choice in Tarefa.STATUS_CHOICES]
    if status not in status_validos:
        return JsonResponse({'erro': 'Status inválido.'}, status=400)
    return JsonResponse(
        _queryset_para_lista(Tarefa.objects.filter(status=status)),
        safe=False,
    )


def listar_tarefas_por_prioridade(request, prioridade):
    prioridades_validas = [choice[0] for choice in Tarefa.PRIORIDADE_CHOICES]
    if prioridade not in prioridades_validas:
        return JsonResponse({'erro': 'Prioridade inválida.'}, status=400)
    return JsonResponse(
        _queryset_para_lista(Tarefa.objects.filter(prioridade=prioridade)),
        safe=False,
    )


def buscar_tarefa_por_id(request, tarefa_id):
    try:
        tarefa = Tarefa.objects.select_related('usuario_responsavel').get(id=tarefa_id)
        return JsonResponse(_serializar_tarefa(tarefa))
    except Tarefa.DoesNotExist:
        return JsonResponse({'erro': 'Tarefa não encontrada.'}, status=404)


def listar_tarefas_atrasadas(request):
    hoje = timezone.now().date()
    qs = Tarefa.objects.filter(
        data_entrega__lt=hoje
    ).exclude(
        status='CONCLUIDA'
    )
    return JsonResponse(_queryset_para_lista(qs), safe=False)


def buscar_tarefas_por_titulo(request, termo):
    return JsonResponse(
        _queryset_para_lista(Tarefa.objects.filter(titulo__icontains=termo)),
        safe=False,
    )


def listar_tarefas_por_status_e_prioridade(request, status, prioridade):
    status_validos = [choice[0] for choice in Tarefa.STATUS_CHOICES]
    prioridades_validas = [choice[0] for choice in Tarefa.PRIORIDADE_CHOICES]

    if status not in status_validos:
        return JsonResponse({'erro': 'Status inválido.'}, status=400)
    if prioridade not in prioridades_validas:
        return JsonResponse({'erro': 'Prioridade inválida.'}, status=400)

    qs = Tarefa.objects.filter(status=status, prioridade=prioridade)
    return JsonResponse(_queryset_para_lista(qs), safe=False)


@csrf_exempt
def criar_tarefa(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    dados = json.loads(request.body)

    campos_obrigatorios = ['titulo', 'descricao', 'prioridade', 'data_entrega']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return JsonResponse({'erro': f'Campo obrigatório ausente: {campo}'}, status=400)

    prioridades_validas = [choice[0] for choice in Tarefa.PRIORIDADE_CHOICES]
    if dados['prioridade'] not in prioridades_validas:
        return JsonResponse({'erro': 'Prioridade inválida.'}, status=400)

    if 'status' in dados:
        status_validos = [choice[0] for choice in Tarefa.STATUS_CHOICES]
        if dados['status'] not in status_validos:
            return JsonResponse({'erro': 'Status inválido.'}, status=400)

    tarefa = Tarefa(
        titulo=dados['titulo'],
        descricao=dados['descricao'],
        prioridade=dados['prioridade'],
        data_entrega=dados['data_entrega'],
        status=dados.get('status', 'ABERTA'),
        usuario_responsavel_id=dados.get('usuario_responsavel_id'),
    )
    tarefa.save()
    tarefa = Tarefa.objects.select_related('usuario_responsavel').get(id=tarefa.id)
    return JsonResponse(_serializar_tarefa(tarefa), status=201)


@csrf_exempt
def atualizar_tarefa(request, tarefa_id):
    if request.method != 'PUT':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    try:
        tarefa = Tarefa.objects.get(id=tarefa_id)
    except Tarefa.DoesNotExist:
        return JsonResponse({'erro': 'Tarefa não encontrada.'}, status=404)

    dados = json.loads(request.body)

    if 'titulo' in dados:
        tarefa.titulo = dados['titulo']
    if 'descricao' in dados:
        tarefa.descricao = dados['descricao']
    if 'data_entrega' in dados:
        tarefa.data_entrega = dados['data_entrega']
    if 'status' in dados:
        status_validos = [choice[0] for choice in Tarefa.STATUS_CHOICES]
        if dados['status'] not in status_validos:
            return JsonResponse({'erro': 'Status inválido.'}, status=400)
        tarefa.status = dados['status']
    if 'prioridade' in dados:
        prioridades_validas = [choice[0] for choice in Tarefa.PRIORIDADE_CHOICES]
        if dados['prioridade'] not in prioridades_validas:
            return JsonResponse({'erro': 'Prioridade inválida.'}, status=400)
        tarefa.prioridade = dados['prioridade']
    if 'usuario_responsavel_id' in dados:
        tarefa.usuario_responsavel_id = dados['usuario_responsavel_id']

    tarefa.save()
    tarefa = Tarefa.objects.select_related('usuario_responsavel').get(id=tarefa_id)
    return JsonResponse(_serializar_tarefa(tarefa))


@csrf_exempt
def remover_tarefa(request, tarefa_id):
    if request.method != 'DELETE':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    try:
        tarefa = Tarefa.objects.get(id=tarefa_id)
    except Tarefa.DoesNotExist:
        return JsonResponse({'erro': 'Tarefa não encontrada.'}, status=404)

    tarefa.delete()
    return JsonResponse({'mensagem': f'Tarefa {tarefa_id} removida com sucesso.'})
