import calculo_de_ponto

oberdan = calculo_de_ponto.Ponto('folhacutesemselecao', 'oberdan')
clayton = calculo_de_ponto.Ponto('folhacutesemselecao','clayton')


oberdan.convertepdfparaimagem()
clayton.convertepdfparaimagem()


oberdan.buscainformacoesnaimagem()
oberdan.calcular_horas(3,0)

clayton.buscainformacoesnaimagem()
clayton.calcular_horas(-2,0)
