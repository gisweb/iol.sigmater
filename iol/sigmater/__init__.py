# -*- extra stuff goes here -*-

from AccessControl import allow_module

allow_module('iol.sigmater')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

from datetime import datetime
from interface import ricercaSoggetti, ricercaTitolaritaSoggetto, ricercaPerIdCat, \
    dettaglioPerIdCat, ricercaPerUIU, dettaglioPerIdUIU


def deep_normalize(d):	
    """ Normalize content of object returned from functions and methods """
    if 'sudsobject' in str(d.__class__):
        d = deep_normalize(dict(d))	
    elif isinstance(d, dict):
        for k,v in d.iteritems():
            if 'sudsobject' in str(v.__class__):	
                #print k, v, '%s' % v.__class__

                r = deep_normalize(dict(v))
	
                d[k] = r	
            elif isinstance(v, dict):	
                r = deep_normalize(v)
                d[k] = r

            elif isinstance(v, (list, tuple, )):	
                d[k] = [deep_normalize(i) for i in v]	
            elif isinstance(v, datetime):

                # per problemi di permessi sugli oggetti datetime trasformo
	
                # in DateTime di Zope
	
                d[k] = DateTime(v.isoformat())
	
    elif isinstance(d, (list, tuple, )):
	
        d = [deep_normalize(i) for i in d]
	
	
    return d


def SigmaterElencoTitolari(titolari):
	# dato una lista di titolari restituisce le informazioni dei singoli soggetti
	soggetti = list()
	for titolare in titolari:
		anag = dict()
		d = {}		
		# restituisce il soggetto
		soggetto=dict(titolare['soggetto']) 
		   
		if 'quotaNumeratore' in titolare.keys():       
			soggetto['quotaNumeratore']=titolare['quotaNumeratore']
		else:        
			soggetto['quotaNumeratore']=''
		if 'quotaDenominatore' in titolare.keys():
			 soggetto['quotaDenominatore']=titolare['quotaDenominatore']
		else:
			soggetto['quotaDenominatore']=''
		if 'comuneNascita' in soggetto.keys():
			soggetto['comuneNascita']=dict(soggetto['comuneNascita'])
		if 'comuneSede' in soggetto.keys():
			soggetto['comuneSede']=dict(soggetto['comuneSede'])
	
		soggetti.append(soggetto)
	return soggetti
	
def SigmaterElencoIndirizzi(indirizzi):	
	address = list()
	for indirizzo in indirizzi:
		indDict = dict(indirizzo)
		address.append(indDict)
	return address

        
def dettaglioDatiTerreno(codCom,foglio,mappale,idImmobile,usr,pwd):
	#restituisce i dati del servizio dettaglio terreno
	query="<comune><codCom>%s</codCom></comune><foglio>%s</foglio><numero>%s</numero><sezione>_</sezione><idImmobile>%s</idImmobile>"  % (codCom,foglio,mappale,idImmobile)
	ret=dict()
 	try:		
		res = deep_normalize(dettaglioPerIdCat(query,usr,pwd))                
		if isinstance(res['variazioniTitolarita'],list):
			res = [dict(r) for r in res['variazioniTitolarita'] if dict(r)['cessate']=='false']
                        res = res[0]
		else:
			res = deep_normalize(res['variazioniTitolarita'])
	except Exception as error:                
		ret['success']=0
		ret['message']=str(error)
		return ret
	
	if not isinstance(res['titolarita'],list):
		res = [res['titolarita']]
	else:
		res = res['titolarita']
	titolari = deep_normalize(res)
       	res = SigmaterElencoTitolari(titolari)
       	ret = dict()
	ret['intestatari']=res
	return [ret]
	
def dettaglioDatiUIU(codCom,foglio,mappale,idImmobile,subalterno,usr,pwd):
	# restituisce i dati del servizio dettaglio UIU
        ret = dict()
	query="<comune><codCom>%s</codCom></comune><foglio>%s</foglio><numero>%s</numero><sezione>_</sezione><idImmobile>%s</idImmobile><subalterno>%s</subalterno>" % (codCom,foglio,mappale,idImmobile,subalterno)
        try:
		res = deep_normalize(dettaglioPerIdUIU(query,usr,pwd))
		
		if isinstance(res['variazioniTitolarita'],list):
			res = [dict(r) for r in res['variazioniTitolarita'] if dict(r)['cessate']=='false'][0]				
		else:			
			res = deep_normalize(res['variazioniTitolarita'])
	except Exception as error:
		ret['success']=0
		ret['message']=str(error)
		return ret
	
	# restituisce gli indirizzi catastali
	try:
		resInd = deep_normalize(dettaglioPerIdUIU(query,usr,pwd))
 
		if not isinstance(resInd['mutazioniUiu'],list):
			resIndList = [resInd['mutazioniUiu']]
		else:
			resIndList = resInd['mutazioniUiu']
		
		resIndCat = [dict(r)['indirizziCatastali'] for r in resIndList if 'indirizziCatastali' in dict(r).keys()]
                
		try:
			if isinstance(resIndCat[0],list):
                              
				resIndCat = [r for r in resIndCat[0]]
		except:
			ret['success']=0
			ret['message']='indirizzi catastale mancante'
			return ret
			
		indirizzi = SigmaterElencoIndirizzi(resIndCat)
	except:
		ret['success']=0
		ret['message']='indirizzo catastale mancante'
		return ret
		
	if not isinstance(res['titolarita'],list):
		res = [res['titolarita']]
	else:
		res = res['titolarita']
		
	titolari = deep_normalize(res)
	res =SigmaterElencoTitolari(titolari)
	ret = dict()
	ret['intestatari']=res
	ret['indirizziCatastali']=indirizzi
	return ret
	
	
def SigmaterUIU(codCom,foglio,mappale,usr,pwd):
	# chiama entrambi i servizi per avere i dati del catasto UIU
	query="<comune><codCom>%s</codCom></comune><foglio>%s</foglio><numero>%s</numero>" %(codCom,foglio,mappale)
	ret={}
	try:
		res = deep_normalize(ricercaPerUIU(query,usr,pwd))
		if not isinstance(res['risultatoRicerca'],list):
			res = [deep_normalize(res['risultatoRicerca'])]
		else:
			res = deep_normalize(res['risultatoRicerca'])
	except:
		ret['success']=0
		ret['message']='Inserisci msg sigmater'
		return ret
	dettaglioImmobile=[]
	
	for imm in res:
               
		try:
			# chiama il servizio dettaglio UIU 
			if 'subalterno' in imm.keys():         
				dettaglio = dettaglioDatiUIU(codCom,foglio,mappale,imm['idImmobile'],imm['subalterno'],usr,pwd)
				dettaglioImmobile.append(dettaglio) 
			else:
				# se non trova il subalterno restituisce solo gli indirizzi catastali				
				resDict={}
				res=[r['indirizziCatastali'] for r in res if 'indirizziCatastali' in r.keys()]
				if not isinstance(res[0],list):
					res=[dict(res[0])]    
				else:
					res=deep_normalize(res[0])		
				resDict['indirizziCatastali']=res
				dettaglioImmobile.append(resDict)
		except:
			ret['success']=0
			ret['message']='dettaglio immobile mancante'
			return ret
	return dettaglioImmobile
