"""Objetos de dominio y patrones State / Observer."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation


def dinero(valor):
    try:
        if isinstance(valor, float):
            raise ValueError('Usá texto o Decimal para dinero')
        monto = Decimal(valor)
        if not monto.is_finite() or monto < 0 or monto != monto.quantize(Decimal('.01')):
            raise ValueError('Monto inválido: positivo con hasta dos decimales')
        return monto.quantize(Decimal('.01'))
    except (InvalidOperation, TypeError):
        raise ValueError('Monto inválido') from None


def cantidad(valor, permitir_cero=False):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < (0 if permitir_cero else 1):
        raise ValueError('La cantidad debe ser un entero válido')
    return valor


class EstadoBulto(ABC):
    nombre = ''

    def precintar(self, bulto):
        raise ValueError('El bulto no permite precintar')

    def despachar(self, bulto):
        raise ValueError('El bulto no permite despachar')

    def recibir(self, bulto):
        raise ValueError('El bulto no permite recibir')

    def verificar(self, bulto, integro):
        raise ValueError('El bulto no permite verificar')


class Preparado(EstadoBulto):
    nombre = 'PREPARADO'
    def precintar(self, bulto):
        bulto.estado = Precintado()

class Precintado(EstadoBulto):
    nombre = 'PRECINTADO'
    def despachar(self, bulto):
        bulto.estado = EnTransito()

class EnTransito(EstadoBulto):
    nombre = 'EN_TRANSITO'
    def recibir(self, bulto):
        bulto.estado = Recibido()

class Recibido(EstadoBulto):
    nombre = 'RECIBIDO'
    def verificar(self, bulto, integro):
        bulto.estado = Verificado() if integro else Rechazado()

class Verificado(EstadoBulto):
    nombre = 'VERIFICADO'

class Rechazado(EstadoBulto):
    nombre = 'RECHAZADO'

ESTADOS = {clase.nombre: clase for clase in (Preparado, Precintado, EnTransito, Recibido, Verificado, Rechazado)}

@dataclass
class Bulto:
    id: int
    estado: EstadoBulto

    def transicionar(self, accion, *args):
        anterior = self.estado.nombre
        getattr(self.estado, accion)(self, *args)
        return anterior, self.estado.nombre

class ObservadorStock(ABC):
    @abstractmethod
    def actualizar(self, stock):
        pass

@dataclass
class Stock:
    sucursal_id: int
    producto_id: int
    disponible: int
    minimo: int
    observadores: list = field(default_factory=list)

    def notificar(self):
        if self.disponible < self.minimo:
            for observador in self.observadores:
                observador.actualizar(self)

class GeneradorReposicionAutomatica(ObservadorStock):
    def __init__(self, servicio):
        self.servicio = servicio

    def actualizar(self, stock):
        self.servicio.consolidar_faltante(stock)
