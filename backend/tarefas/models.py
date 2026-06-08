from django.db import models
from usuarios.models import Usuario


class Tarefa(models.Model):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EM_ANDAMENTO', 'Em andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]

    PRIORIDADE_CHOICES = [
        ('URGENTE', 'Urgente'),
        ('NAO_URGENTE', 'Não urgente'),
    ]

    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTA')
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_entrega = models.DateField()
    usuario_responsavel = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.titulo
