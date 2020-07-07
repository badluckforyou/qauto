import os

class AppSettings:
    
    TITLE = "Qauto|v0.0.0beta"
    COMPANY = ""
    ROWSNUMBER = 20
    PROJECTS = {
        "Bindo Pos Store K7701": "k7701",
        "Bindo Pos Store GG8157": "GG8157",
        "Bindo Pos Store GG8157-TA": "GG8157_TA",
        "Bindo Pos Store RETAIL-02": "Retail_02",
    }
    PACKAGES = {
        "Bindo Pos Store K7701": ["com.bindo.bindo-pos-dev"],
        "Bindo Pos Store GG8157": ["com.bindo.bindo-pos-dev"],
        "Bindo Pos Store GG8157-TA": ["com.bindo.bindo-pos-dev"],
        "Bindo Pos Store RETAIL-02": ["com.bindo.bindo-pos-dev"],
    }
    PLATFORMS = ["ios", "android", "web"]
    METHODS = ["Post", "Get", "Put", "Delete"]
    DATATYPE = ["JSON", "TEXT", "DICT"]
    RESOLUTIONS = []
    FILEPATH = os.path.dirname(os.path.abspath(__file__))
    TESTERFOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testersinfo")
    LOGPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")

if not os.path.exists(AppSettings.TESTERFOLDER):
    os.mkdir(AppSettings.TESTERFOLDER)