# -*- extra stuff goes here -*-

from AccessControl import allow_module

allow_module('iol.sigmater')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

from interface import ricercaSoggetti, ricercaTitolaritaSoggetto, ricercaPerIdCat, \
    dettaglioPerIdCat, ricercaPerUIU, dettaglioPerIdUIU
