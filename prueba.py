# -*- coding: utf-8 -*-
# Programa que representa los datos del Astmon
# Autor: Susana (versión 0, 7 julio 2021) 

    print('Representación gráfica de los datos de Astmon OSN')
    print('       ')
    """
    Muy importante nombre de los ficheros a la hora de elegir las gráficas:

        ** Las carpetas de las diez posiciones cuelgan de /data/Astmon/posX
        ** Los datos están en /data/Astmon/posX/graficas/
           MMMYYYY_posX_F.dat donde MMM son las tres primeras letras del mes y F es uno de los   
           filtros B,V,R o I o si es una noche o noches YYYYMMDD_posX_F.dat
    """
    print('Introduce que quieres comparar:')
    print('- Los cuatro filtros (B,V,R,I) en un periodo de tiempo (mes o días) en una posición (de la 1 a la 10) [1]'
    print('- Un filtro en un mismo periodo de tiempo en diferentes años en una posición [2]'
    print('- Un filtro en un periodo de tiempo en diferentes posiciones [3]' 
 
    pregunta = int(input('Introduce 1, 2 o 3:'))
    
    if pregunta == 1:
       posicion = int(input('Dime posición (0 al 10):'
       period = str(input('Dime mes y año (formato MMMYYYY) o noche (formato YYYYMMDD):')
       datav = period + 'pos'+ pos + '_V.dat'
       datab = period + 'pos'+ pos + '_B.dat'
       datar = period + 'pos'+ pos + '_R.dat'
       datai = period + 'pos'+ pos + '_I.dat'
       print('Periodo', period, 'en la posicion', pos)
    
    if pregunta == 2:
       filtro = str(input('Dime filtro (B,V,R o I):'
       posicion = int(input('Dime posición (0 al 10):'
       ano = 0
       year = int(input('¿Cúantos años quieres representar?:')
       
       while ano < year:
            period = str(input('Dime mes y año (formato MMMYYYY) o noche (formato YYYYMMDD):')
            ano = ano + 1
            data = period + 'pos'+ posicion + '_' + filtro + '.dat'
    if pregunta == 3:
       filtro = str(input('Dime filtro (B,V,R o I):'
       period = str(input('Dime mes y año (formato MMMYYYY) o noche (formato YYYYMMDD):')
         
       posicion = int(input('Dime posición (0 al 10):'
