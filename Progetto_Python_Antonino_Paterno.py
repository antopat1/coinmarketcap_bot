import requests
import json
from pprint import pprint
LIMITECAP_ACQUISTO=76000000 #definita come limite volume inidicato al punto 4 del progetto
var_json={}

class report_bot:
    #definisco il metodo costruttore
    def __init__(self):
        self.url='https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.headers={'Accepts':'application/json','X-CMC_PRO_API_KEY': '0a2fb2a6-05a5-4731-8f4f-19090466df18',} # inserire API per verifica
        self.params = {'start': '1', 'limit': '100', 'convert': 'USD'}

    #definisco metodo per richiede dati al dataprovider
    def ottieni_dati(self):
        r=requests.get(url=self.url,headers=self.headers,params=self.params).json() #richiama la funzione get del modulo request che si aspetta di ricevere i 3 parametri di base inseriti all'istanziazione dell'oggetto della classe BOT; il risultato lo vogliamo in formato Json
        return r['data'] # dell'oggetto JSON appena acquisito,mi limito ai dati associati alla chiave 'data'

"""
funzione criptovaluta con il volume maggiore (in $) delle ultime 24 ore
"""
def maggior_volume(dati_ingr):
    val_Bvolume = None
    for valuta in dati_ingr:
        if not val_Bvolume or valuta['quote']['USD']['volume_24h'] > val_Bvolume['quote']['USD']['volume_24h']:
            val_Bvolume = valuta
    print("\nLa Criptovaluta a maggior volume nelle ultime 24 ore è:", val_Bvolume['name'], "con un volume di" , round(val_Bvolume['quote']['USD']['volume_24h'],3) , "$" )
    var_json['1)Crito_Maggior_Volume_24h']=val_Bvolume['name']

"""
funzione migliori criptovalute per incremento % ultime 24h
"""
def stampa_primi(diz_ing):
    primi_dieci = reversed(list(diz_ing[-10:]))
    diz_val = {}
    print("\nDi seguito le prime dieci valute in ordine di incremento percentuale nelle ultime 24 ore\n")
    for i in primi_dieci:
        pprint(f"{i[0]} -> {i[1][0]}")
        diz_val[i[0]] = i[1][0]
    var_json['2)Prime_dieci_per_incremento_%_24h']=sorted(diz_val.items(),key=lambda kv: kv[1],reverse=True)

"""
funzione peggiori criptovalute per incremento % ultime 24h
"""
def stampa_ultimi(diz_ing):
    ultimi_dieci = reversed(list(diz_ing[0:10]))
    diz_val={}
    print("\nQueste invece le ultime dieci \n")
    for i in ultimi_dieci:
        pprint(f"{i[0]} -> {i[1][0]}")
        diz_val[i[0]] = i[1][0]
    var_json['3)Ultime_dieci_per_incremento%_24H'] = sorted(diz_val.items(),key=lambda kv:kv[1],reverse=True)

"""
Funzione che raggruppa gli algoritmi per scorrere ed analizzare liste e dizionari per il calcolo 
"""
def calcolo_spesa(diz_ing,tip_calcolo):
    conta=0
    quant_denaro=0
    quant_limit=0
    quant_preced=0
    val_precente = {}
    if tip_calcolo==0:
        for v in reversed(diz_ing):
            if conta<20:
                quant_denaro+=v[1][2]
                val_precente[v[0]]=v[1][2]
                conta+=1
    elif tip_calcolo==1:
        for vb in reversed(diz_ing):
            if vb[1][3]> LIMITECAP_ACQUISTO:
                quant_limit+=vb[1][2]
    else:
        conta=0
        for vc in reversed(diz_ing):
            if conta<20:
                val_precente[vc[0]]=vc[1][2]/(1+(vc[1][0]/100))
                conta+=1
        ord_val=reversed(sorted(val_precente.items(),key=lambda kv: kv[1]))
        conta=0
        for vd in ord_val:
            if conta<20:
                quant_preced+=vd[1]
                conta+=1

    if tip_calcolo==0:
        var_json['4)Spesa_per_acquisto_Top20']=round(quant_denaro,3)
        return quant_denaro
    elif tip_calcolo==1:
        var_json['5)Spesa_per_acquisto_Voloume_sopra_limite'] = round(quant_limit,3)
        return quant_limit
    else:
        return quant_preced

"""
Funzione principale con la quale si richiamano i restanti metodi 
"""
def ordina_reportizza(dati_ingr):
    diz_valute= {}
    for valuta in dati_ingr:
        dati_val = []
        nome_v=valuta['name']
        inc_v=round(valuta['quote']['USD']['percent_change_24h'],2)
        cap_v = valuta['quote']['USD']['market_cap']
        prez_v = valuta['quote']['USD']['price']
        volum_v = valuta['quote']['USD']['volume_24h']
        dati_val.append(inc_v)
        dati_val.append(cap_v)
        dati_val.append(prez_v)
        dati_val.append(volum_v)
        diz_valute[nome_v]= dati_val

    incr_ord=sorted(diz_valute.items(),key=lambda kv: kv[1])
    stampa_primi(incr_ord)
    stampa_ultimi(incr_ord)
    cap_ord = sorted(diz_valute.items(),key=lambda kv: kv[1][1])
    spesa_tot=round(calcolo_spesa(cap_ord,0),2)
    print("\n"f'Per acquistare un unità di ciascuna delle prima 20 criptovalute occorre una spesa di {spesa_tot} $')
    cap_ord = sorted(diz_valute.items(), key=lambda kv: kv[1][3])
    spesa_magglimit=round(calcolo_spesa(cap_ord,1),2)
    print("\n"f'Per acquistare un unità di criptovalute il cui volume nelle ultime 24h è maggiore  di 76000000 occorre una spesa di {spesa_magglimit} $\n')
    cap_ord= sorted(diz_valute.items(), key=lambda kv: kv[1][1])
    spesa_preced=calcolo_spesa(cap_ord,2)

    print(f"Acquistando le prime 20 Critpovalute per capitalizzazione, 24 fa ore avrei speso {round(spesa_preced,3)} $, questo porta ad un DELTA di guadagno/perdita di {round((spesa_tot - spesa_preced),3)} $ pari al {round(((round((spesa_tot - spesa_preced),3)/round(spesa_preced,3))*100),2)} %\n")
    var_json['6)Equity_line%_ultime_24H'] = round(((round((spesa_tot - spesa_preced),3)/round(spesa_preced,3))*100),2)
    pprint(var_json)
    stringaJson=json.dumps(var_json) #avvio processo scrittura file Json su file
    with open('Progetto_Python_Antonino_Paterno_10_11_21.json','w') as outfile:
        outfile.write(stringaJson)

#istanzio un oggetto della classe robot e ne richiamo i metodi principali per restituire le richieste del progetto
elabora_report=report_bot()
dati_grezzi=elabora_report.ottieni_dati()
maggior_volume(dati_grezzi)
ordina_reportizza(dati_grezzi)




