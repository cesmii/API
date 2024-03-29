## Required Files
mutation_data.csv	query_cesmii_plot.py	query_cesmii_plot.xlsm	xlwings.xlam cesmii_credentials.py

## Prererqs:
This demo was tested on Windows with Python 3.7.0

# Instructions

## 1. Set up *.xlsm file to run Python code
You must Developer module in Excel spreadsheet that save the file with macros as *.xlsm
* In command prompt Run `pip install xlwings==0.25.3`
* Add the xlwings Add-In to Excel: In command prompt run `.\xlwings.xlam addin install` then `.\xlwings.xlam runpython install`. Agree to any Excel prompt. 
* Add Developer Tab (Options => Customize Ribbon => Choose commands from: Main Tabs => Developer)
* From the Developer Tab click "Excel Add-Ins" and browse the location of xlwings.xlam file and add
* From Developer Tab, Click the Visual Basic Interface and then ==> Tools ==> References ==> Add xlwings (tick mark)
* From Developer Tab, Click the Visual Basic Interface, Add the following Python Function to Modules. This will call Python from Excel.

      Sub Call_Python_Function()
        RunPython ("import query_cesmii_plot; query_cesmii_plot.read_data()")
      End Sub


## 2. Set up credentials

Copy the file `cesmii_credentials_example.py` as `cesmii_credentials.py` and change the following on the right side of each equal sign (=):

Replace the content of the 5 variables below with actual value 
```
authenticator_name="From https://yourinstance.cesmii.net/developer/graphql/authentication-management"
authenticator_passwd="From https://yourinstance.cesmii.net/developer/graphql/authentication-management"
user_name="Login info from https://yourinstance.cesmii.net/"
authenticator_role="From https://yourinstance.cesmii.net/developer/graphql/authentication-management"
instance_graphql_endpoint = "https://yourinstance.cesmii.net/graphql"
```

## 3. Setup Python Script

Open `query_cesmii_plot.py` and define `tagIds` (line 183) to match IDs from your SMIP instance. This is where the data will be written from Excel to the platform. It should correspond to a Tag ID or Equipment Instance ID.

## 4. Run the mutation

Open `query_cesmii_plot.xlsm` and run the mutation from the xlwings tab of the file by clicking "Run main" on the right.

If there are errors related to missing modules, use pip install to install those dependencies.


