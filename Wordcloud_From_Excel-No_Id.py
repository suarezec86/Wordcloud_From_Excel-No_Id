from _Params import CallParams

import pandas as pd
import re
import csv
import sys
import os

'''
El output sale con los campos aptos para importar a la herramienta online
https://www.nubedepalabras.es/
'''

# function to get unique values 
def unique(list1): 
    # insert the list to the set 
    list_set = set(list1) 
    # convert the set to the list 
    unique_list = (list(list_set)) 
    unique_list.sort()
    return unique_list

def CallGroupbyCount(df,fields):#fields in array
    #import pandas as pd
    df = df.groupby(fields).size().reset_index(name='Value')
    return df

def CallSortDf(df, orderBy, orderByAsc):
    #import pandas as pd
    df = df.sort_values(
        by = orderBy,
        ascending = orderByAsc
    )
    print("OK: Sorted DataFrame")
    return df

def CallLoadCSV(myPath,fileName,fields):
    #import sys
    try:
        # Check if file is open before start
        myfile = open(myPath + fileName + ".csv", "r+") # or "a+", whatever you need
    except IOError:
        sys.exit("Close the file (" + fileName + ") and run againg the process.")
    
    try:
        df = pd.read_csv(myPath + fileName + '.csv', thousands=',', encoding ='utf-8')
    except Exception as e: 
        print(e)
        qContinue=input("File ("+ fileName +") not found. Do you want to continue (y/n)").lower()
        if qContinue=='y':
            df = pd.DataFrame(columns=fields)
        else:
            print("Process Ended abruptly.")
            quit()
        
    print("OK: Historical data of",fileName)
    return df

def CallExportToCsv(myPath, fileName, df):    
    fileName = myPath + fileName + '.csv'
    df.to_csv (
        fileName, 
        index = False, 
        header=True,
        float_format='%.2f',
        line_terminator='\n',
        encoding='utf-7'
    )
    return fileName

def CallExportToExcel1(fileName, df, myPath, sheetName):
    # import pandas as pd
    fileName = myPath + fileName + '.xlsx'
    column_list = df.columns
    # Create a Pandas Excel writer using XlsxWriter engine.
    writer = pd.ExcelWriter(fileName, engine='xlsxwriter')
    df.to_excel (
        writer, 
        sheet_name = sheetName,
        index = False, 
        header=False,
        startrow=1,
        encoding='utf-7',
        freeze_panes=(1,0)
    )
    # Get workbook and worksheet objects
    # workbook  = writer.book
    worksheet = writer.sheets[sheetName]
    
    for idx, val in enumerate(column_list):
        worksheet.write(0, idx, val)

    writer.save()
        
    print("OK: File exported")
        
    return fileName

#======================================================================
# Parameters

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))

    params = CallParams()
    pathFileInput = directory + '\\'
    pathFileOutput = directory + '\\'
    stopwordsPath= directory + '\\'
    
    inputFileName =  params['inputFileName']
    outputFileName = params['outputFileName']
    
    stopwordsFileName = params['stopwordsFileName']
    textTitle = params['textTitle']
    col1Name = params['Col1Name']
    col2Name = params['Col2Name']
    col3Name = params['Col3Name']
    col4Name = params['Col4Name']
    
    letter_replace={'á':'a','é':'e','í':'i','ó':'o','ú':'u','à':'a','è':'e','ì':'i','ò':'o','ù':'u','ü':'u'}
    #======================================================================

    # Load list of words/phrases to analyse
    df1 = CallLoadCSV(pathFileInput,inputFileName,[textTitle])

    # Load stopwords
    with open(stopwordsPath+stopwordsFileName+'.csv',encoding='utf-8') as f:
        reader = csv.reader(f)
        myStopWords = []
        for i,row in enumerate(reader):
            if(i>0):
                myStopWords.append(','.join(map(str,row)).title())
    f.close()
    
    dfs=[]
    myResult=[]
    for index, row in df1.iterrows(): 
        i = str(row[textTitle]) 
        separate = i.split(" ") 
        
        for j in range(len(separate)): 
            separate[j] = separate[j].lower() 

            #print("!!!: ",separate[j]," $$$: ",separate[j].find('http',0,4))
            if (separate[j].find('http',0,4) != 0):            
                for key, value in letter_replace.items():
                    separate[j]=re.sub(key, value, separate[j])
                    
                After_regex=[re.sub("[^a-z0-9ñ]+", '', separate[j]).title()]
                if not set(myStopWords).intersection(After_regex):
                    myResult=After_regex
            #print("After regex:" ,After_regex)
            dfs+= myResult
            #print("Append: ",dfs)

    df2 = pd.DataFrame(dfs,columns=[col2Name])
    df2 = CallGroupbyCount(df2,[col2Name])

    df2 = df2.rename(columns={'Value':col1Name})
    df2 = CallSortDf(df2,[col1Name],[False])
    df2 = df2[[col1Name,col2Name]]
    df2[col3Name] = ""
    df2[col4Name] = ""

    CallExportToCsv(pathFileOutput,outputFileName,df2)
    # CallExportToExcel1("Output",df2,pathFileOutput,"Wordcloud")
else:
    print("File Wordcloud_From_Excel-No_Id.py imported")