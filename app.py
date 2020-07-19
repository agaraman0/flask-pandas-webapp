import pandas as pd
from zipfile import ZipFile
import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__,template_folder='template')

path = os.getcwd()

def readxlsxfile(filename):
    
    data = pd.read_excel(path + '/' + filename)
    data = pd.DataFrame(data)
    return data

def nearestNaturalnum(row):
    if row[1] > 0:
        if row[1] - int(row[1]) > 0.5:
            return int(row[1]) + 1
        else:
            return int(row[1])
    else:
        if row[1] - int(row[1]) > -0.5:
            return int(row[1])
        else:
            return int(row[1]) - 1

@app.route('/upload')
def upload_file():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename('data.xlsx'))
      return 'file uploaded successfully'

# task 1 data seperation based on suffix of matabolite "PC", "LPC", "Plasmalogen"
@app.route('/dataseperation')
def dataseperation():

   
   data = readxlsxfile('data.xlsx')
   
   plasmalogen_data = data.loc[data["Accepted Compound ID"].str.endswith('plasmalogen')==True]
   pc_data = data1 = data.loc[data["Accepted Compound ID"].str.endswith(' PC')==True]
   lpc_data = data1 = data.loc[data["Accepted Compound ID"].str.endswith('LPC')==True]

   plasmalogen_data.to_excel(path + '/plasmalogen_data.xlsx')
   pc_data.to_excel(path + '/pc_data.xlsx')
   lpc_data.to_excel(path + '/lpc_data.xlsx')

   zipObj = ZipFile(path + '/suffixMatabolite.zip', 'w')
   zipObj.write('plasmalogen_data.xlsx')
   zipObj.write('pc_data.xlsx')
   zipObj.write('lpc_data.xlsx')

   zipObj.close()

   return send_file(path + '/suffixMatabolite.zip')

# task 2 to create Retention time round off column
@app.route('/dataRTroundoff')
def dataRTroundoff():
   
   data = readxlsxfile('data.xlsx')
   data['Retention Time RoundOff'] = data.apply(nearestNaturalnum,axis=1)
   data.to_excel(path + '/dataRTroundoff.xlsx')

   return send_file(path + '/dataRTroundoff.xlsx',as_attachment=True)

# task 3 to create mean matabolites of samples which have equal RT roundoff
@app.route('/dataMeanRTsamples')
def dataMeanSamples():
   data = readxlsxfile('data.xlsx')
   data['Retention Time RoundOff'] = data.apply(nearestNaturalnum,axis=1)
   df = data.groupby('Retention Time RoundOff').mean()
   df.drop(['m/z','Retention time (min)'],axis = 1)

   data.to_excel(path + '/dataMeanRTsamples.xlsx')

   return send_file(path + '/dataMeanRTsamples.xlsx',as_attachment=True)

# to render any excel file which is already present in our dir
@app.route('/renderTemplate')
def render():
   filename = ""
   filename = request.args.get("filename")
   if filename != "":
      if os.path.isfile(path + '/' + filename):
         data = readxlsxfile(filename)
         return data.to_html()
      else:
         return "File not found"

if __name__ == '__main__':
   app.run(debug = True)