import datetime
import time
from tkinter import CURRENT
import mysql.connector
import os
from mysql.connector import Error
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#Login credentials
username = 'Lyceo Username'
password = 'Lyceo Password'
db_hostname = 'server ip/hostname'
db_username = 'server username'
db_password = 'server password'
db_name = 'homi' # Moet hezelfde zijn als de database opgegeven in "Make DB.py"
credentials = 'location of credentials.json'
old_data_sync_amount = 50

TIMEOUT = 10
MONTHS = {'JAN.': 1,
          'FEB.': 2,
          'MRT.': 3,
          'APR.': 4,
          'MEI': 5,
          'JUN.': 6,
          'JUL.': 7,
          'AUG.': 8,
          'SEP.': 9,
          'OKT.': 10,
          'NOV.': 11,
          'DEC.': 12}

def startGoogleAPI():
    SCOPES = ['https://www.googleapis.com/auth/calendar.app.created']

    creds = None

    if os.path.exists(username + '.json'):
        creds = Credentials.from_authorized_user_file(
            username + '.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials, SCOPES)
            creds = flow.run_local_server(port=9090)
        # Save the credentials for the next run
        with open(username + '.json', 'w') as token:
            token.write(creds.to_json())
            
    service = build('calendar', 'v3', credentials=creds)
    return service
            
def makeCalendar(service):
        query = f"""SELECT CalendarId FROM homi.users WHERE IdUser = '{username}'"""
        calendar_id = read_query(connection, query)
        calendar_id = str(calendar_id[0]).replace("('", '')
        calendar_id = str(calendar_id).replace("',)", '')
        print(calendar_id)

        if str(calendar_id) == '(None,)':
            calendar = {
                'summary': 'Werken Lyceo'
            }
            response = service.calendars().insert(body=calendar).execute()

            query = f"""UPDATE homi.users SET CalendarId = '{response['id']}' WHERE IdUser = '{username}'"""
            execute_query(connection, query)
            
            return response['id']
        else:
            return calendar_id

def create_db_connection(host_name, user_name, user_password, db_name):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def startBrowser():
    options = Options()
    # options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    # service = Service(r'C:\bin\geckodriver.exe')

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, TIMEOUT)
    driver.get("https://werkenbijapp.lyceo.nl/login")

    return wait, driver

def signIn(wait: WebDriverWait):
    success = False
    while not success:
        wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="btn-login"]'))).click()
        wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="username"]'))).send_keys(username)
        wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="password"]'))).send_keys(password)
        wait.until(ec.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/form/div[3]/button'))).click()
        try:
            wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="btn-login"]')))
        except:
            success = True
    try:
        wait.until(ec.visibility_of_element_located((By.XPATH, '/html/body/app-root/ion-app/ion-router-outlet/help-page/ion-footer/ion-button'))).click()
        time.sleep(1)
    except:
        pass

def getNewData(wait: WebDriverWait, driver, new, max_data = 9999):
    if new:
        driver.execute_script("arguments[0].scrollIntoView();", wait.until(ec.visibility_of_element_located((By.XPATH, '/html/body/app-root/ion-app/ion-router-outlet/app-menu-layout/ion-tabs/div/ion-router-outlet/app-assignments-page/ion-tabs/div/ion-router-outlet/app-planned-assignments/ion-content/app-assignment-card[1]'))))
    else:
        driver.execute_script("arguments[0].scrollIntoView();", wait.until(ec.visibility_of_element_located((By.XPATH, '/html/body/app-root/ion-app/ion-router-outlet/app-menu-layout/ion-tabs/div/ion-router-outlet/app-assignments-page/ion-tabs/div/ion-router-outlet/app-finished-assignments/ion-content/app-assignment-card[1]'))))
    num_assignments = None
    data = []
    first_date = None
    last_date = None
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    while len(data) != num_assignments and len(data) < max_data:
        num_assignments = len(data)

        assignments = wait.until(ec.visibility_of_any_elements_located((By.CSS_SELECTOR, 'app-assignment-card')))
        print(len(assignments))

        for assignment in assignments:
            assignment_info = assignment.find_elements(By.XPATH, './ion-item-sliding/ion-item/div[2]/*')
            if assignment_info[0].text != '':
                assignment_title = f'{assignment_info[0].text} {assignment_info[1].text}'
                assignment_subtitle = ' '.join(assignment_info[3].text.split('\n'))
                assignment_date_raw = assignment_info[2].text.split('\n')[0]
                assignment_start_time = assignment_info[2].text.split('\n')[1].split(' - ')[0]
                assignment_end_time = assignment_info[2].text.split('\n')[1].split(' - ')[1]
                
                assignment_days = []
                assignment_months = []
                
                i = 0

                while len(assignment_date_raw.split()) > i:
                    assignment_days.append(assignment_date_raw.split()[i + 1])
                    assignment_months.append(MONTHS[assignment_date_raw.split()[i + 2]])
                    i += 4
                    
                i = 0
                while i < len(assignment_days):
                    assignment_month = assignment_months[i]
                    assignment_day = assignment_days[i]

                    if assignment_month - current_month == -11:
                        current_year += 1
                    elif assignment_month - current_month == 11:
                        current_year += -1
                    
                    current_month = assignment_month

                    assignment_start = datetime.datetime.strptime(f"{current_year}-{assignment_month}-{assignment_day}-{assignment_start_time.split(':')[0]}-{assignment_start_time.split(':')[1]}", '%Y-%m-%d-%H-%M')
                    assignment_end = datetime.datetime.strptime(f"{current_year}-{assignment_month}-{assignment_day}-{assignment_end_time.split(':')[0]}-{assignment_end_time.split(':')[1]}", '%Y-%m-%d-%H-%M')
                
                    if [assignment_title, assignment_subtitle, assignment_start, assignment_end] not in data:
                        data.append([assignment_title, assignment_subtitle, assignment_start, assignment_end])
                        print([assignment_title, assignment_subtitle, assignment_start, assignment_end])

                    if first_date == None:
                        first_date = assignment_start
                    last_date = assignment_end
                    
                    i += 1

            driver.execute_script("arguments[0].scrollIntoView();", assignment)
            
    return data, first_date, last_date

def getOldData(first_date: datetime.datetime, last_date: datetime.datetime, connection):
    current_date = datetime.datetime.now()
    data = []
    if first_date < last_date:
        if first_date < current_date:
            query = f"""SELECT * FROM {db_name}.`{username}` WHERE AssignmentStart>='{first_date}' and AssignmentEnd<='{last_date}';"""
        else:
            query = f"""SELECT * FROM {db_name}.`{username}` WHERE AssignmentStart>='{current_date}' and AssignmentEnd<='{last_date}';"""
    else:
        query = f"""SELECT * FROM {db_name}.`{username}` WHERE AssignmentStart<='{first_date}' and AssignmentEnd>='{current_date}';"""
    assignments = read_query(connection, query)
    for assignment in assignments:
        data.append(list(assignment))
            
    return data

def removeassignment(event_id: str, connection, service):
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    except:
        pass
    
    query = f"""DELETE FROM {db_name}.`{username}` WHERE EventId='{event_id}';"""
    execute_query(connection, query)

def addassignment(assignment_title, assignment_subtitle, assignment_start, assignment_end, connection, calendar_id, service):
    start = f'{assignment_start.year}-{assignment_start.month}-{assignment_start.day}T{assignment_start.hour}:{assignment_start.minute}:00'
    end = f'{assignment_end.year}-{assignment_end.month}-{assignment_end.day}T{assignment_end.hour}:{assignment_end.minute}:00'
    googleEvent = {
        'summary': assignment_title,
        'description': assignment_subtitle,
        'start': {
            'dateTime': start,
            'timeZone': 'Europe/Amsterdam'
        },
        'end': {
            'dateTime': end,
            'timeZone': 'Europe/Amsterdam'
        },
    }
    response = service.events().insert(calendarId=calendar_id, body=googleEvent).execute()
    
    query = f"""INSERT INTO {db_name}.`{username}` (`EventId`, `assignmentTitle`, `assignmentSubtitle`, `assignmentStart`, `AssignmentEnd`) 
                VALUES ('{response['id']}', '{assignment_title}', '{assignment_subtitle}', '{assignment_start}', '{assignment_end}')"""
    execute_query(connection, query)

def compareData(new_data: list, old_data: list):
    assignments_to_add = []
    assignments_to_remove = []
    updated_old_data = []
    for assignment in old_data:
        if [assignment[1], assignment[2], assignment[3], assignment[4]] not in new_data:
            assignments_to_remove.append(assignment)
        elif [assignment[1], assignment[2], assignment[3], assignment[4]] not in updated_old_data:
            updated_old_data.append([assignment[1], assignment[2], assignment[3], assignment[4]])
        else:
            assignments_to_remove.append(assignment)
    
    old_data = [[x[1], x[2], x[3], x[4]] for x in old_data]
    for assignment in new_data:
        if assignment not in old_data:
            assignments_to_add.append(assignment)
   
    return assignments_to_add, assignments_to_remove

def data(wait, driver, connection, calendar_id, service, new, max_data = 9999):
    new_data, first_date, last_date = getNewData(wait, driver, new, max_data)
    old_data = getOldData(first_date, last_date, connection)
    assignments_to_add, assignments_to_remove = compareData(new_data, old_data)

    for assignment in assignments_to_add:
        addassignment(assignment[0], assignment[1], assignment[2], assignment[3], connection, calendar_id, service)
    for assignment in assignments_to_remove:
        removeassignment(assignment[0], connection, service)
        
while True:
    try:
        connection = create_db_connection(db_hostname, db_username, db_password, db_name)
        service = startGoogleAPI()
        calendar_id = makeCalendar(service)
        wait, driver = startBrowser()
        signIn(wait)
        
        driver.get('https://werkenbijapp.lyceo.nl/opdrachten/gepland')
        time.sleep(2)
        data(wait, driver, connection, calendar_id, service, True)

        driver.get('https://werkenbijapp.lyceo.nl/opdrachten/afgerond')
        time.sleep(2)
        data(wait, driver, connection, calendar_id, service, False, old_data_sync_amount)

        driver.close()
    except Exception as e:
        print(e)
        try:
            driver.close()
        except Exception as e:
            print(f"Error during startup\n{e}")
