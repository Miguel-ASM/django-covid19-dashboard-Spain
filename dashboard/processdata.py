# Import Built in modules
import json
from urllib.request import urlretrieve # retrieve files from urls
import os # operative system utilities
import re # regular expressions
from io import StringIO

# Third party modules
import pandas as pd
import geopandas as gpd
import numpy as np

# The codes for the autonomous comunities (CCAA) in the dataframe use the ISO convention
# 'ISO 3166-2:ES' : https://www.iso.org/obp/ui/es/#iso:code:3166:ES.
# I make a mapping from the names of the CCAA to the ISO codes with a dictionary
def make_CCAA_dict():
    communities ="""
    ES-AN,Andalucía
    ES-AR,Aragón
    ES-AS,Asturias
    ES-CN,Canarias
    ES-CB,Cantabria
    ES-CM,Castilla La Mancha
    ES-CL,Castilla y León
    ES-CT,Catalunya
    ES-EX,Extremadura
    ES-GA,Galiza
    ES-IB,Illes Balears
    ES-RI,La Rioja
    ES-MD,Madrid
    ES-MC,Murcia
    ES-NC,Navarra
    ES-PV,Euskadi
    ES-VC,Comunitat Valenciana
    ES-CE,Ceuta
    ES-ML,Melilla
    """
    # Dictionary relating "CCA names":"ISO CODES"
    CCAA_dict = {}
    for line in communities.strip().split('\n'):
        code,name = line.strip().split(',')
        code = code.replace('ES-','')
        CCAA_dict[name] = CCAA_dict.get(name,code)
    return CCAA_dict

# The CCAA are encoded with cartographic IDS from 1 to 19 in the geodata_frame.
# Make a dictionary to translate them into CCAA ISO codes.
def make_CCAA_cartodb_ID_dict():
    cartodb_ID_str ="""
    ES-AN,16
    ES-AR,15
    ES-AS,14
    ES-CN,19
    ES-CB,12
    ES-CM,10
    ES-CL,11
    ES-CT,9
    ES-EX,7
    ES-GA,6
    ES-IB,13
    ES-RI,17
    ES-MD,5
    ES-MC,4
    ES-NC,3
    ES-PV,2
    ES-VC,8
    ES-CE,18
    ES-ML,1
    """
    # Dictionary relating "cartographic ID numbers":"ISO CODES"
    CCAA_cartodb_ID_dict = {}
    for line in cartodb_ID_str.strip().split('\n'):
        code,ID = line.strip().split(',')
        ID = int(ID)
        code = code.replace('ES-','')
        CCAA_cartodb_ID_dict[code] = CCAA_cartodb_ID_dict.get(code,ID)
    return CCAA_cartodb_ID_dict

# Function to download the csv file with the data of coronavirus outbreak in Spain
def downloadCSVfileObject(csvfile_url='https://cnecovid.isciii.es/covid19/resources/agregados.csv'):
    """
    Takes as a parameter the url to the csv file. Returns a stringIO object
    """
    # Download file
    file_path, HTTP_Message = urlretrieve(csvfile_url);
    # Process the file doing the following:
    # - read the original file which is encoded originally encoded as 'iso-8859-1'. The outputfile will be 'utf-8'
    # - removing some unwanted symbols that can break everything:
    #           -'*' symbols for foot notes.
    unwanted_chars = r'[*]' #regex string with the set of unwanted characters.
    with open(file_path,'r',encoding='iso-8859-1') as f_in:
        csv_content_str = re.sub(unwanted_chars, '', f_in.read(), flags=re.MULTILINE).strip()
    return StringIO(csv_content_str)

# Function to make a data frame for the national data from the csv file
def makeNationalDataFrame(csv_file_stringIO):
    csv_file_stringIO.seek(0,0)
    # Get the names of the columns of the csv file
    columns = list( pd.read_csv(csv_file_stringIO,nrows=0).columns )
    # Column names for the data
    ISO_code_column_name = columns[0]
    date_column_name = columns[1]
    cases_column_name = columns[2]
    PCR_column_name = columns[3]
    TestAC_column_name = columns[4]
    Hospitalized_column_name = columns[5]
    UCI_column_name = columns[6]
    deaths_column_name = columns[7]
    recovered_column_name = columns[8]
    # Data types for the columns
    data_types = {
        columns[0]:str,
        columns[1]:str,
        columns[2]:np.float64,
        columns[3]:np.float64,
        columns[4]:np.float64,
        columns[5]:np.float64,
        columns[6]:np.float64,
        columns[7]:np.float64,
        columns[8]:np.float64
    }
    fill_na_dict =  {
        columns[0]:'',
        columns[1]:'',
        columns[2]:0.,
        columns[3]:0.,
        columns[4]:0.,
        columns[5]:0.,
        columns[6]:0.,
        columns[7]:0.,
        columns[8]:0.
    }
    # Load the data into a pandas data frame with the correct data types
    csv_file_stringIO.seek(0,0)
    data = pd.read_csv(csv_file_stringIO,dtype=data_types)
    csv_file_stringIO.close()
    # Remove Unnamed columns:
    unnamed_cols_iterator = filter(lambda column: 'Unnamed:' in column ,columns )
    for col in unnamed_cols_iterator:
        data.pop(col);
    # Substitute the NA values with 0s
    data.fillna(fill_na_dict,inplace=True)
    # strip tailing whitespaces in the column names
    data.rename(columns=lambda name : name.strip(),inplace=True)
    # Put the dates in the YYYY-MM-DD format and datetime64 type
    data[date_column_name] = pd.to_datetime(data[date_column_name],format='%d/%m/%Y',errors='coerce')
    # remove the rows with no date values
    data.dropna(inplace=True,subset=[date_column_name])
    # sort the rows by date value
    data.sort_values(by=[date_column_name],ignore_index=True,inplace=True)
    # Update the value of the active cases column with the PCR number
    cases_0_value_mask = data[cases_column_name] == 0
    data.loc[cases_0_value_mask,cases_column_name] = data.loc[cases_0_value_mask,PCR_column_name]
    # Add a column for active cases
    data['Casos Activos'] = data[cases_column_name] - data[deaths_column_name] - data[recovered_column_name]
    # Add a column with the cartographic IDS to match the geojson file
    CCAA_cartodb_ID_dict = make_CCAA_cartodb_ID_dict();
    data['cartodb_id'] = [CCAA_cartodb_ID_dict[code] for code in data[ISO_code_column_name]]
    # return the data frame
    return data


# Function to create a dictionary with a dataframe for every CCAA.
# The key is the CCAA name
def makeCommunitiesDataFrameDict(national_data_frame):
    CCAA_label = national_data_frame.columns[0]
    communities_data_frames_dict = dict()
    CCAA_dict = make_CCAA_dict()
    for name,code in CCAA_dict.items():
        df = national_data_frame[national_data_frame[CCAA_label]==code]
        df.reset_index(drop=True,inplace=True)
        communities_data_frames_dict[name] = df
    return communities_data_frames_dict



# Create a class to contain all the data in a single object
class Covid_data():

    # Path to the json file with the geographical data
    path_to_geoJSON = os.path.join(
        os.path.dirname(__file__),
        'static/dashboard/geoJSON/ign_spanish_adm1_ccaa_displaced_canary.json'
    )

    def __init__(self):
        with open(Covid_data.path_to_geoJSON,'r') as f:
            self.geoJSON_dict_CCAA = json.load(f)
        del(f)
        data_COVID19_spain = makeNationalDataFrame(downloadCSVfileObject())
        columns = list( data_COVID19_spain.columns )
        # Column names for the data
        ISO_code_column_name = columns[0]
        date_column_name = columns[1]
        cases_column_name = columns[2]
        PCR_column_name = columns[3]
        TestAC_column_name = columns[4]
        Hospitalized_column_name = columns[5]
        UCI_column_name = columns[6]
        deaths_column_name = columns[7]
        recovered_column_name = columns[8]
        active_cases_column_name = columns[9]
        cartodb_id_column_name = columns[10]


        #Assign the previous values to instance attributes
        self.column_names_dict = dict(
            ISO_code_column_name = ISO_code_column_name,
            date_column_name = date_column_name,
            cases_column_name = cases_column_name,
            PCR_column_name = PCR_column_name,
            TestAC_column_name = TestAC_column_name,
            Hospitalized_column_name = Hospitalized_column_name,
            UCI_column_name = UCI_column_name,
            deaths_column_name = deaths_column_name,
            recovered_column_name = recovered_column_name,
            active_cases_column_name = active_cases_column_name,
            cartodb_id_column_name = cartodb_id_column_name
        )

        data_COVID19_spain_last = pd.DataFrame(data_COVID19_spain[data_COVID19_spain[date_column_name]==max(data_COVID19_spain[date_column_name])])
        data_COVID19_spain_last.reset_index(drop=True,inplace=True)

        self.CCAA_dict = make_CCAA_dict()
        self.CCAA_cartodb_ID_dict = make_CCAA_cartodb_ID_dict()
        self.data_COVID19_spain = data_COVID19_spain
        self.communities_data_frames_dict = makeCommunitiesDataFrameDict(data_COVID19_spain)
        self.data_COVID19_spain_last = data_COVID19_spain_last
