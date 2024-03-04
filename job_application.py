from flask import Flask, request, jsonify
from selenium.webdriver.common.by import By
import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
import string
import sys
import os
from twocaptcha import TwoCaptcha
import logging
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)

CORS(app)

app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')


def solve_recaptha(sitekey,url):


    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


    api_key = os.getenv('APIKEY_2CAPTCHA', '4ed5a62c7e200d2d96076b15f3a6850d')

    solver = TwoCaptcha(api_key)

    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=url)
        return result

    except Exception as e:
        sys.exit(e)

def download_cv(url,file_name):
    # download cv
    # Download the PDF file using requests
    downloaded_file_path = file_name
    response = requests.get(url)
    with open(downloaded_file_path, 'wb') as file:
        file.write(response.content)


@app.route('/', methods=['GET'])
def hello_jobs():
    return jsonify({'message':"hello jobees!!!"})

@app.route('/api/recruitingapp', methods=['POST'])
def recruitingapp():
    # Assuming you expect JSON data in the request
    data = request.get_json()
    try:
        # Initialize logging configuration to write log messages to a file named 'recruitingapp.log'
        logging.basicConfig(filename='recruitingapp.log', level=logging.INFO)
        # Try to retrieve the password from the 'applicant' dictionary in 'data'
        try:
            password = data['applicant']['password']
            account_exist = True
        except:
            account_exist = False
            password = '12345678$#aliA'

        # Set up Chrome options for configuring the browser
        chrome_options = Options()
        # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        # Initialize a Chrome WebDriver instance
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        # Open the specified job ad URL in the Chrome browser
        driver.get(data['job']['job_ad_url'])
        already_close = driver.find_element(By.CSS_SELECTOR,"div.container__inner h1").text
        if already_close == 'Schade, die Stelle scheint schon besetzt worden zu sein.':
            return jsonify({"message": "this job application is not available", 'application_id': data['application_id'],"status_code": '200'})
        driver.get(driver.find_element(By.CSS_SELECTOR,"a.button.button--link.header__cta.button--solid.b-background.b-border").get_attribute('href'))
        a=1
        # Check the gender in the 'applicant' dictionary and select the corresponding option on the web page
        if data['applicant']['gender'] =='male':
            # select gender
            try:
                # Use list comprehension to click on the appropriate radio button for male
                [v.click() for v in driver.find_elements(By.CSS_SELECTOR,'label.form_element_radiobuttonhorizontal') if 'Salutation_M' in v.get_attribute('for')]
            except:
                pass
        elif data['applicant']['gender'] == 'female':
            # select gender
            try:
                # Use list comprehension to click on the appropriate radio button for female
                [v.click() for v in driver.find_elements(By.CSS_SELECTOR, 'label.form_element_radiobuttonhorizontal') if
                 'Salutation_F' in v.get_attribute('for')]
            except:
                pass
        else:
            # select gender
            try:
                # Select another gender (assuming 'D' represents another gender)
                [v.click() for v in driver.find_elements(By.CSS_SELECTOR, 'label.form_element_radiobuttonhorizontal') if
                 'Salutation_D' in v.get_attribute('for')]
            except:
                pass

        # Fill the name

        # Input the applicant's first name into the specified text field using its CSS selector
        driver.find_element(By.CSS_SELECTOR,'input[name="form_data10"]').send_keys(data['applicant']['firstname'])
        # Input the applicant's last name into the specified text field using its CSS selector
        driver.find_element(By.CSS_SELECTOR,'input[name="form_data11"]').send_keys(data['applicant']['lastname'])
        # Input the applicant's birthdate into the specified date picker field using its CSS selector
        driver.find_element(By.CSS_SELECTOR,'input[data-picker-type="date"]').send_keys(data['applicant']['birthdate'].replace('.',"/"))
        # Input the applicant's email into the specified email input field using its CSS selector
        driver.find_element(By.CSS_SELECTOR,'input.input_type_email').send_keys(data['applicant']['email'])
        time.sleep(2)
        # Input the applicant's password into the specified password input field using its CSS selector
        driver.find_element(By.CSS_SELECTOR,'input[type="password"]').send_keys(password)
        time.sleep(2)
        # Try to find the error message element and extract its text
        try:
            error_message = driver.find_element(By.CSS_SELECTOR,"span.check_form_error_message").text
        except:
            error_message = ""

        # Check if the error message indicates that the email/login is already in the system
        if error_message.strip() == 'Diese E-Mail-Adresse / Login ist bereits im System vorhanden. Für jede weitere Bewerbung bitte oben via "Login" anmelden.':
            # Iterate through elements to find and click on the 'Login' link
            for click_login in driver.find_elements(By.CSS_SELECTOR,"a.displayelement_text"):
                try:
                    # Check if the text of the element is 'Login'
                    if click_login.text== 'Login':
                        click_login.click()
                        time.sleep(2)
                        # Switch to the alert
                        alert = driver.switch_to.alert

                        # Accept the alert
                        alert.accept()
                        time.sleep(2)
                        a=1
                except:
                    pass

            # Use WebDriverWait to wait up to 20 seconds for the presence of the specified input field and enter the applicant's email
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#input_UserName"))).send_keys(data['applicant']['email'])
            # Use WebDriverWait to wait up to 20 seconds for the presence of the specified input field and enter the password
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#input_password"))).send_keys(password)
            # Use WebDriverWait to wait up to 20 seconds for the presence of the specified button and click on it
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="Login"]'))).click()


        try:
            # Try to find and extract the text content of a specific element using WebDriverWait
            already_submit_error = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.form_content_boundary'))).text
        except:
            pass

        # Check if a specific error message indicating a duplicate application is present
        if "Es existiert bereits eine Bewerbung für diese Stelle." in already_submit_error:
            # Save a screenshot of the page
            driver.save_screenshot("recruitingapp_after.png")
            driver.quit()
            # Return a response indicating that the user has already applied for the job
            return jsonify({"message":"you have already applied for this job thanks",'application_id':data['application_id'],"status_code":'200'})


        try:
            # Input the applicant's street into the specified textarea using its CSS selector
            driver.find_element(By.CSS_SELECTOR,'textarea[name="form_data18"]').send_keys(data['applicant']['street'])
            time.sleep(1)
            # Input the applicant's ZIP code into the specified input field using its CSS selector
            driver.find_element(By.CSS_SELECTOR,'input[name="form_data19"]').send_keys(data['applicant']['zip'])
            time.sleep(1)
            # Input the applicant's city into the specified input field using its CSS selector
            driver.find_element(By.CSS_SELECTOR,'input[name="form_data20"]').send_keys(data['applicant']['city'])
            time.sleep(1)
            # Select the applicant's country from a dropdown menu using its CSS selector and option title
            driver.find_element(By.CSS_SELECTOR,'select[name="form_data21"] option[title="' + f'{data["applicant"]["country_name"]}'+'"]').click()
            time.sleep(1)
            # Input the applicant's phone number into the specified input field using its CSS selector
            driver.find_element(By.CSS_SELECTOR,'input[name="form_data23"]').send_keys(data['applicant']['phone'])
            time.sleep(1)
            # Input the applicant's email into the specified input field using its CSS selector
            driver.find_element(By.CSS_SELECTOR,'input[name="form_data24"]').send_keys(data['applicant']['email'])
            time.sleep(1)
        except:
            pass

        # Specify the file name for the CV to be downloaded
        file_name = 'cv.pdf'
        # Call the custom function 'download_cv' to download the CV from the provided URL
        download_cv(data['documents'][0]['url'],file_name)

        try:
            # Input the file path into the specified input field using its CSS selector
            driver.find_element(By.CSS_SELECTOR,'input[name="form_data31"]').send_keys(os.getcwd()+'//'+file_name)
            time.sleep(5)
            # Select an option from a dropdown menu using its CSS selector and option title
            driver.find_element(By.CSS_SELECTOR, 'select[name="form_data37"] option[title="migros-gruppe.jobs"]').click()
            time.sleep(0.5)

            # Use list comprehension to click on a radio button for data agreement
            [v.click() for v in driver.find_elements(By.CSS_SELECTOR, 'label.form_element_radiobutton') if 'DataAgree_No' in v.get_attribute('for')]

            # Click on a checkbox using its CSS selector
            driver.find_element(By.CSS_SELECTOR, 'label[for="input_3634"]').click()
            time.sleep(0.5)
            # Save a screenshot of the page before submitting a form
            driver.save_screenshot("recruitingapp_before0.png")
            if data['dry_run'] == True:
                driver.quit()
                return jsonify({"message": "for test dry run", 'application_id': data['application_id'], "status_code": '200'})

            # Click on a button using its CSS selector to submit the form
            driver.find_element(By.CSS_SELECTOR, 'button[name="form_submit"]').click()
            time.sleep(0.5)

            try:
                # Wait up to 20 seconds for the presence of an element with the CSS selector "h1.form_title"
                # Once found, extract and store the text content of the element
                element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.form_title"))).text
            except:
                element = ""

            # Check if the text content of the element is 'Frage beantworten'
            if element.strip() == 'Frage beantworten':
                while True:
                    try:
                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label in ['Wie viele Jahre Berufserfahrung können Sie im Bereich Treuhandwesen vorweisen?','Wie viele Jahre Berufserfahrung können Sie im Detailhandel vorweisen?','Wie lange sind Sie bereits in einer Führungsposition tätig und wie viele Mitarbeitende haben Sie maximal geführt?']:
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys(data['applicant']['years_of_experience'])

                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                            time.sleep(3)
                    except:
                        pass

                    try:
                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == 'Geben Sie uns Ihr Wunschpensum an.':
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys('30-40 hours')
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                            time.sleep(3)
                    except:
                        pass
                    # Click on labels within div elements with class 'form_content_answerquestion_answer' where the input value is "1"
                    # Click on a button with the name 'form_submit' after answering the question
                    for v in driver.find_elements(By.CSS_SELECTOR, 'div.form_content_answerquestion_answer'):
                        try:
                            if "1" == v.find_element(By.CSS_SELECTOR, 'input').get_attribute('value'):
                                v.find_element(By.CSS_SELECTOR, "label").click()
                                time.sleep(2)
                                # Click on a button with the name 'form_submit' after answering the question
                                WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                        except:
                            pass


                    time.sleep(3)

                    # Input text into a textarea with the name 'form_data2'
                    try:

                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == 'Per wann könnten Sie die Stelle antreten?':
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys('as soon as possible')
                            time.sleep(2)
                            # Click on a button with the name 'form_submit'
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                    except:
                        pass

                    # Input text into a textarea with the name 'form_data2'
                    try:
                        time.sleep(3)
                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == 'Bitte geben Sie uns Ihre Lohnvorstellungen bekannt (brutto, 100%, x13).':
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys('100%')
                            time.sleep(2)
                            # Click on a button with the name 'form_submit'
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                    except:
                        pass
                    # Input text into a textarea with the name 'form_data2'
                    try:
                        time.sleep(3)
                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == 'Bitte geben Sie uns Ihre Lohnvorstellungen bekannt':
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys('None')
                            time.sleep(2)
                            # Click on a button with the name 'form_submit'
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                    except:
                        pass

                    time.sleep(3)
                    # Save a screenshot of the page
                    driver.save_screenshot("recruitingapp_before.png")

                    try:
                        question_label = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == "":
                            # Try to click on a button with the name 'form_submit'
                            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                            time.sleep(2)
                    except:
                        # Try to click on a button with the name 'form_submit'
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                        time.sleep(2)
                        pass

                    try:
                        # Wait up to 20 seconds for the presence of an element with the CSS selector 'h1#maintitle_1'
                        # Once found, extract and store the text content of the element
                        confirmation_message = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1#maintitle_1'))).text
                        if confirmation_message == 'Bestätigung':
                            break
                    except:
                        confirmation_message = ""
        except:
            # Input the file path into the specified input field using its CSS selector
            driver.find_element(By.CSS_SELECTOR, 'input[name="form_data8"]').send_keys(os.getcwd() + '//' + file_name)
            time.sleep(5)
            # Select an option from a dropdown menu using its CSS selector and option title
            driver.find_element(By.CSS_SELECTOR,'select[name="form_data14"] option[title="migros-gruppe.jobs"]').click()
            time.sleep(2)

            # Use list comprehension to click on a radio button for data agreement
            [v.click() for v in driver.find_elements(By.CSS_SELECTOR, 'label.form_element_radiobutton') if 'DataAgree_No' in v.get_attribute('for')]
            time.sleep(2)
            # Click on a button with the name 'form_submit' to submit the form
            driver.find_element(By.CSS_SELECTOR, 'button[name="form_submit"]').click()
            time.sleep(3)

            try:
                # wait 10 seconds before looking for element
                element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.form_title"))).text
            except:
                element = ""

            # Check if the text content of the element is 'Frage beantworten'
            if element.strip() == 'Frage beantworten':
                while True:
                    try:
                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label in ['Wie viele Jahre Berufserfahrung können Sie im Bereich Treuhandwesen vorweisen?','Wie viele Jahre Berufserfahrung können Sie im Detailhandel vorweisen?','Wie lange sind Sie bereits in einer Führungsposition tätig und wie viele Mitarbeitende haben Sie maximal geführt?']:
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys(data['applicant']['years_of_experience'])
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                            time.sleep(3)

                    except:
                        pass

                    try:
                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == 'Geben Sie uns Ihr Wunschpensum an.':
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys('30-40 hours')
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                            time.sleep(3)
                    except:
                        pass
                    # Click on labels within div elements with class 'form_content_answerquestion_answer' where the input value is "1"
                    # [v.find_element(By.CSS_SELECTOR, "label").click() for v in driver.find_elements(By.CSS_SELECTOR, 'div.form_content_answerquestion_answer') if "1" == v.find_element(By.CSS_SELECTOR, 'input').get_attribute('value')]
                    for v in driver.find_elements(By.CSS_SELECTOR, 'div.form_content_answerquestion_answer'):
                        try:
                            if "1" == v.find_element(By.CSS_SELECTOR, 'input').get_attribute('value'):
                                v.find_element(By.CSS_SELECTOR, "label").click()
                                time.sleep(2)
                                # Click on a button with the name 'form_submit' after answering the question
                                WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                                time.sleep(3)
                        except:
                            pass

                    # Input text into a textarea with the name 'form_data2'
                    try:
                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == 'Per wann könnten Sie die Stelle antreten?':
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys('as soon as possible')
                            time.sleep(2)
                            # Click on a button with the name 'form_submit'
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                    except:
                        pass

                    # Input text into a textarea with the name 'form_data2'
                    try:
                        time.sleep(3)
                        question_label = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == 'Bitte geben Sie uns Ihre Lohnvorstellungen bekannt (brutto, 100%, x13).':
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys('100%')
                            time.sleep(2)
                            # Click on a button with the name 'form_submit'
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                    except:
                        pass
                    # Input text into a textarea with the name 'form_data2'
                    try:
                        time.sleep(3)
                        question_label = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == 'Bitte geben Sie uns Ihre Lohnvorstellungen bekannt':
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'textarea[name="form_data2"]'))).send_keys('None')
                            time.sleep(2)
                            # Click on a button with the name 'form_submit'
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                    except:
                        pass

                    # Save a screenshot of the page
                    # driver.save_screenshot("recruitingapp_before.png")


                    # Click on a button with the name 'form_submit'
                    try:
                        question_label = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.questions_question'))).text
                        if question_label == "":
                            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                            time.sleep(3)
                            try:
                                # Try to click on a button with the name 'form_submit'
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                                time.sleep(2)
                            except:
                                pass
                    except:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="form_submit"]'))).click()
                        time.sleep(2)

                    try:
                        confirmation_message = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1#maintitle_1'))).text
                        if confirmation_message == 'Bestätigung':
                            break
                    except:
                        confirmation_message = ""
                        pass
        # If the confirmation message is 'Bestätigung'
        confirmation_message = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1#maintitle_1'))).text
        if confirmation_message =='Bestätigung':
            # Save a screenshot of the page
            driver.save_screenshot("recruitingapp_after.png")
            # Close the WebDriver instance
            driver.quit()
            # Check if the account exists
            if account_exist:
                # Return a dictionary with success message, application ID, and status code
                return jsonify({"message": "application has been successfully sent",'application_id':data['application_id'],"status_code":'200'})
            elif account_exist == False:
                # Return a dictionary with success message, application ID, and status code
                return jsonify({"message": "application has been successfully sent","password":password,'application_id':data['application_id'],"status_code":'200'})
        else:
            # Save a screenshot of the page
            driver.save_screenshot("recruitingapp_after.png")
            # Close the WebDriver instance
            driver.quit()
            # Return a dictionary with an error message, application ID, and status code
            return jsonify({"message": "Something Went Wrong!!",'application_id':data['application_id'],"status_code":'400'})

    except Exception as e:
        logging.info(e)
        # Close the WebDriver instance
        print(e)
        # Return a dictionary with an error message, including the exception details, application ID, and status code
        return jsonify({"message": f"Something Went Wrong!! {e}",'application_id':data['application_id'],"status_code":'400'})

@app.route('/api/successfactors', methods=['POST'])
def successfactors():
    data = request.get_json()
    try:
        try:
            # Configure logging to write log messages to a file named 'successfactors.log' with INFO level
            logging.basicConfig(filename='successfactors.log', level=logging.INFO)
            # Attempt to retrieve the password from the 'data' dictionary under the 'applicant' key
            password = data['applicant']['password']
            # Set 'account_exist' to True since password retrieval was successful
            account_exist = True
        except:
            # If an exception occurs (e.g., KeyError or any other), set 'account_exist' to False and set password
            account_exist = False
            password = '12345678$#aliA'

        # Create ChromeOptions object to configure Chrome WebDriver
        chrome_options = Options()
        # Add the "--headless" argument to run the browser in headless mode (without GUI)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        # Create a WebDriver instance using Chrome, passing the configured options
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        # Navigate to the job advertisement URL provided in the 'data' dictionary
        driver.get(data['job']['job_ad_url'])

        try:
            no_longer_avaiable = driver.find_element(By.CSS_SELECTOR,"div.main-inner h1").text
            if no_longer_avaiable == 'Diese Stelle ist leider nicht mehr ausgeschrieben!':
                driver.quit()
                return jsonify({"message": "this job application is not available", 'application_id': data['application_id'],"status_code": '200'})


        except:
            pass
        # Locate the username input field using CSS selector and input the applicant's email
        driver.get(driver.find_element(By.CSS_SELECTOR,'a[title="Jetzt bewerben"]').get_attribute('href'))

        driver.find_element(By.CSS_SELECTOR,"input#username").send_keys(data['applicant']['email'])
        time.sleep(0.5)
        # Locate the password input field using CSS selector and input the password
        driver.find_element(By.CSS_SELECTOR,"input#password").send_keys(password)
        time.sleep(0.5)
        # Locate the login button using CSS selector and perform a click action to submit the form
        driver.find_element(By.CSS_SELECTOR,"span.aquabtn.active").click()

        # Attempt to locate and retrieve error message related to job application
        try:
            # Wait for up to 5 seconds until the specified element (error message) is present if not then move on
            error_message = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.rcmJobApplyExceptionMsg'))).text
            # Check if the error message indicates that the applicant has already applied for the job
            if error_message == 'Sie haben sich bereits für diese Stelle beworben.':
                # Close the WebDriver and return a response indicating successful handling of the case
                driver.quit()
                # return message
                return jsonify({"message":"you have already applied for this job thanks",'application_id':data['application_id'],"status_code":'200'})
            if error_message == 'Diese Stelle kann zurzeit nicht angezeigt werden. Sie wurde entweder gelöscht, oder man kann sich nicht länger darauf bewerben.':
                # Close the WebDriver and return a response indicating successful handling of the case
                driver.quit()
                # return message
                return jsonify({"message":"This position cannot currently be displayed. It has either been deleted or you can no longer apply for it",'application_id':data['application_id'],"status_code":'200'})

        except:
            error_message = ""

        try:
            # Wait for up to 5 seconds until the specified element (error message) is present if not then move on
            error_message = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#errorMsg_1 strong'))).text
        except:
            error_message = ""

        # Check if the error message indicates invalid username or password
        if error_message == 'Benutzername oder Kennwort ungültig. Bitte geben Sie Ihre Anmeldedaten erneut ein.':
            try:
                # Find all elements with CSS selector 'div.bottomLink a' where the text is 'Noch kein Profil? Hier registrieren'
                [v.click() for v in driver.find_elements(By.CSS_SELECTOR,"div.bottomLink a") if v.text.strip() == 'Noch kein Profil? Hier registrieren']
                time.sleep(2)
                # Attempt to click the elements again (second attempt)
                [v.click() for v in driver.find_elements(By.CSS_SELECTOR,"div.bottomLink a") if v.text.strip() == 'Noch kein Profil? Hier registrieren']
            except:
                pass

            try:
                # Wait for up to 10 seconds until the specified element (input#fbclc_userName) is present
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#fbclc_userName')))
                # Input the applicant's email into the username field
                driver.find_element(By.CSS_SELECTOR,"input#fbclc_userName").send_keys(data['applicant']['email'])
                time.sleep(0.5)
                # Confirm the email by inputting it again into the corresponding field
                driver.find_element(By.CSS_SELECTOR, "input#fbclc_emailConf").send_keys(data['applicant']['email'])
                time.sleep(0.5)
                # Input the applicant's password into the password fiel
                driver.find_element(By.CSS_SELECTOR, "input#fbclc_pwd").send_keys(password)
                time.sleep(0.5)
                # Confirm the password by inputting it again into the corresponding field
                driver.find_element(By.CSS_SELECTOR, "input#fbclc_pwdConf").send_keys(password)
                time.sleep(0.5)
                # Input the applicant's first name into the corresponding field
                driver.find_element(By.CSS_SELECTOR, "input#fbclc_fName").send_keys(data['applicant']['firstname'])
                time.sleep(0.5)
                # Input the applicant's last name into the corresponding field
                driver.find_element(By.CSS_SELECTOR, "input#fbclc_lName").send_keys(data['applicant']['lastname'])
                time.sleep(0.5)
                # Select the country from the dropdown list based on the provided value
                driver.find_element(By.CSS_SELECTOR, "select#fbclc_country option[value="+f"'{data['applicant']['country']}']").click()
                time.sleep(0.5)
                # Click on the data privacy link
                driver.find_element(By.CSS_SELECTOR, "a#dataPrivacyId").click()
                time.sleep(0.5)
                # Click on the "Accept" button in the data privacy modal
                driver.find_element(By.CSS_SELECTOR, 'div.modal-dialog_btns button[title="Akzeptieren"]').click()
                time.sleep(0.5)
                # Click on the "Create Account" button
                driver.find_element(By.CSS_SELECTOR, 'button#fbclc_createAccountButton').click()
                time.sleep(0.5)

            except:
                pass

        try:
            try:
                error_message = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.rcmJobApplyExceptionMsg'))).text
                if error_message == 'Diese Stelle kann zurzeit nicht angezeigt werden. Sie wurde entweder gelöscht, oder man kann sich nicht länger darauf bewerben.':
                    # Close the WebDriver and return a response indicating successful handling of the case
                    driver.quit()
                    # return message
                    return jsonify({"message": "This position cannot currently be displayed. It has either been deleted or you can no longer apply for it",
                                       'application_id': data['application_id'], "status_code": '200'})
            except:
                pass

            # Wait for up to 10 seconds until all elements specified by the CSS selector are present
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.rcmFormSection.row h2")))
            # Specify the file name for the downloaded CV
            file_name = 'cv.pdf'
            # Download the CV by calling the 'download_cv' function with the URL and file name
            download_cv(data['documents'][0]['url'], file_name)

            try:
                # Attempt to click on an element specified by the CSS selector
                driver.find_element(By.CSS_SELECTOR, 'span[aria-labelledby="38: 52:_ariaActionLabel"]').click()
            except:
                pass
            # Locate the file upload input field and provide the file path for uploading
            driver.find_element(By.CSS_SELECTOR, "input.fileUpload").send_keys(os.getcwd() + '//' + file_name)
            # Pause for 4 seconds to allow the file to be processed after upload
            time.sleep(4)

        except:
            pass

        # Check if the applicant's gender is 'male' or not 'female'
        if data['applicant']['gender'] == 'male' or data['applicant']['gender'] != 'female':
            # Scroll to the bottom of the page using JavaScript
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            # Use a list comprehension to find and click on buttons within elements with specified CSS selectors
            [v.find_element(By.CSS_SELECTOR,"button").click() for v in driver.find_elements(By.CSS_SELECTOR,"div.rcmFormSection.row h2") if v.text =='Profilinformationen']

            # Click on the input field for additional title options
            driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Weitere Optionen für Anrede"]').click()
            time.sleep(1)
            # Click on the option with title 'Herr' (Mr.) for the salutation
            driver.find_element(By.CSS_SELECTOR,'a[title="Herr"]').click()
            time.sleep(0.5)
        # Check if the applicant's gender is 'female'
        if data['applicant']['gender'] == 'female':
            # Scroll to the bottom of the page using JavaScript
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            # Use a list comprehension to find and click on buttons within elements with specified CSS selectors
            [v.find_element(By.CSS_SELECTOR,"button").click() for v in driver.find_elements(By.CSS_SELECTOR,"div.rcmFormSection.row h2") if v.text =='Profilinformationen']

            driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Weitere Optionen für Anrede"]').click()
            time.sleep(1)
            # Click on the option with title 'Frau' (Mrs.) for the salutation
            driver.find_element(By.CSS_SELECTOR,'a[title="Frau"]').click()
            time.sleep(0.5)

        # Click on the input field for additional options for the country code
        driver.find_element(By.CSS_SELECTOR,'input[aria-label="Weitere Optionen für Landesvorwahl"]').click()
        time.sleep(1)
        while True:
            try:
                # Click on the option with the title specified in the 'data' dictionary for the country name
                driver.find_element(By.CSS_SELECTOR,'a[title="' + f'{data["applicant"]["country_name"]}' + '"]').click()
                # Exit the loop if the click is successful
                break
            except:
                # If an exception occurs (e.g., element not found), click on the input field again
                driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Weitere Optionen für Landesvorwahl"]').click()
                time.sleep(1)

        time.sleep(1)
        # Clear the contents of the input field with the name "cellPhone"
        cellphone = driver.find_element(By.CSS_SELECTOR, 'input[name="cellPhone"]')
        cellphone.clear()
        time.sleep(0.5)
        # Input the applicant's phone number into the "cellPhone" input field
        cellphone.send_keys(data['applicant']['phone'])
        time.sleep(1)
        # Click on the date picker element with the specified placeholder text
        driver.find_element(By.CSS_SELECTOR,'ui5-date-picker-xweb-calendar-widget[placeholder="TT.MM.JJJJ"]').click()
        time.sleep(1)
        try:
            # Change the value attribute using JavaScript
            new_value = ""  # Replace "New Value" with the desired value
            # Find the date picker element using a CSS selector
            element = driver.find_element(By.CSS_SELECTOR,'ui5-date-picker-xweb-calendar-widget[placeholder="TT.MM.JJJJ"]')
            # Execute JavaScript to set the 'value' attribute of the element
            driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", element, new_value)
            time.sleep(1)
            # Input the applicant's birthdate into the date picker element
            driver.find_element(By.CSS_SELECTOR,'ui5-date-picker-xweb-calendar-widget[placeholder="TT.MM.JJJJ"]').send_keys(data['applicant']['birthdate'])
        except:
            pass
        time.sleep(1)
        # Retrieve street and city information from the 'data' dictionary
        street = data['applicant']['street']
        city  = data['applicant']['city']
        # Combine street and city into a single address string
        address = street +" "+city
        # Clear the contents of the input field with the name "address"
        address_element = driver.find_element(By.CSS_SELECTOR, 'input[name="address"]')
        address_element.clear()
        # Input the combined address into the "address" input field
        address_element.send_keys(address)

        time.sleep(1)
        # Clear the contents of the input field with the name "zip"
        zip_elemt = driver.find_element(By.CSS_SELECTOR, 'input[name="zip"]')
        zip_elemt.clear()
        # Input the applicant's zip code into the "zip" input field
        zip_elemt.send_keys(data['applicant']['zip'])
        city_element = driver.find_element(By.CSS_SELECTOR, 'input[name="city"]')
        # Clear the contents of the input field with the name "city"
        city_element.clear()
        # Input the applicant's city into the "city" input field
        city_element.send_keys(data['applicant']['city'])
        time.sleep(0.5)
        # Click on the button with the specified aria-label for data agreement
        driver.find_element(By.CSS_SELECTOR,'button[aria-label="Weitere Optionen für Ich erkläre mich damit einverstanden, dass meine Daten zur Abwicklung der Bewerbung an Unternehmen innerhalb der Coop Gruppe weitergeleitet werden können."]').click()
        time.sleep(2)
        try:
            # Attempt to click on the element with the title "Ja" (Yes)
            driver.find_element(By.CSS_SELECTOR,'a[title="Ja"]').click()
        # Handle the case where the above click attempt results in an exception
        except:
            # Click on the button with the specified aria-label for data agreement
            driver.find_element(By.CSS_SELECTOR,'button[aria-label="Weitere Optionen für Ich erkläre mich damit einverstanden, dass meine Daten zur Abwicklung der Bewerbung an Unternehmen innerhalb der Coop Gruppe weitergeleitet werden können."]').click()
            time.sleep(2)
            # Attempt to click on the element with the title "Ja" (Yes) again
            driver.find_element(By.CSS_SELECTOR, 'a[title="Ja"]').click()

        time.sleep(1)

        # Use a list comprehension to find and click on buttons within elements with specified CSS selectors
        [v.find_element(By.CSS_SELECTOR, "button").click() for v in driver.find_elements(By.CSS_SELECTOR, "div.rcmFormSection.row h2") if v.text == 'Stellenspezifische Informationen']

        # Click on the input field for additional options related to being an employee at Coop Gruppe
        driver.find_element(By.CSS_SELECTOR,'input[aria-label="Weitere Optionen für Ich bin bereits Mitarbeiter/in bei der Coop Gruppe"]').click()
        time.sleep(3)

        # Click on the option with title "Nein" (No)
        driver.find_element(By.CSS_SELECTOR,'a[title="Nein"]').click()
        time.sleep(2)
        try:
            # Attempt to find and input text into a textarea element
            driver.find_element(By.CSS_SELECTOR,"div.RCMFormField.rcmFormQuestionElement.textAreaXL textarea").send_keys('Any day')
        except:
            pass

        try:
            # Iterate over form questions to find the one related to evening shifts
            for form_questions in driver.find_elements(By.CSS_SELECTOR,"div.RCMFormField.rcmFormQuestionElement"):
                if 'Sind Abendeinsätze (gemäss unseren Öffnungszeiten) für Sie möglich?' in form_questions.text:
                    # Click on the first radio button (assumed to be the positive option)
                    form_questions.find_elements(By.CSS_SELECTOR,"label.radioLabel")[0].click()
                if 'Ist Ihnen die Stelle durch einen Mitarbeitenden von Coop empfohlen worden?' in form_questions.text:
                    # Click on the first radio button (assumed to be the positive option)
                    form_questions.find_elements(By.CSS_SELECTOR,"label.radioLabel")[1].click()
                if 'Ist dir die Stelle durch einen Mitarbeitenden von Coop empfohlen worden?' in form_questions.text:
                    # Click on the first radio button (assumed to be the positive option)
                    form_questions.find_elements(By.CSS_SELECTOR,"label.radioLabel")[1].click()
                if 'Für diese Stelle suchen wir eine/-n Mitarbeitende/-n im Stundenlohn. Würde dieses Pensum deinen Vorstellungen entsprechen?' in form_questions.text:
                    # Click on the first radio button (assumed to be the positive option)
                    form_questions.find_elements(By.CSS_SELECTOR,"label.radioLabel")[0].click()
                if 'Sind Abendeinsätze für dich möglich? (ab 17.00 Uhr)' in form_questions.text:
                    # Click on the first radio button (assumed to be the positive option)
                    form_questions.find_elements(By.CSS_SELECTOR,"label.radioLabel")[0].click()
                if 'Sind Wochenendeinsätze für dich möglich?' in form_questions.text:
                    # Click on the first radio button (assumed to be the positive option)
                    form_questions.find_elements(By.CSS_SELECTOR,"label.radioLabel")[0].click()
                if  "Wenn ja, durch wen (Name, Vorname)? Bitte den Namen zwingend auch in den Bewerbungsunterlagen erwähnen." in form_questions.text:
                    form_questions.find_element(By.CSS_SELECTOR, "textarea").send_keys('no')


        except:
            pass
        try:
            # Iterate over form questions to find the one related to Saturday shifts
            for form_questions in driver.find_elements(By.CSS_SELECTOR,"div.RCMFormField.rcmFormQuestionElement"):
                if 'Sind Einsätze am Samstag für Sie möglich?' in form_questions.text:
                    # Click on the first radio button (assumed to be the positive option)
                    form_questions.find_elements(By.CSS_SELECTOR,"label.radioLabel")[0].click()
        except:
            pass
        # Scroll to the bottom of the page using JavaScript
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Save a screenshot before clicking the "Bewerben" button
        driver.save_screenshot("successfactors_before.png")
        time.sleep(2)
        if data['dry_run'] == True:
            return jsonify({"message": "for test dry run", 'application_id': data['application_id'],"status_code": '200'})

        # Use a list comprehension to find and click on elements with the specified CSS selector and text
        [v.click() for v in driver.find_elements(By.CSS_SELECTOR,"span.rcmSaveButton") if v.text == 'Bewerben']


        try:
            # Wait for up to 10 seconds until all elements specified by the CSS selector are present
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#applyConfirmMsg")))
            # Save a screenshot after successfully submitting the application
            driver.save_screenshot("successfactors_after.png")
            # Quit the driver
            driver.quit()
            # Check if an account exists based on the previous logic
            if account_exist:
                # Return an message and status code
                return jsonify({"message": "application has been successfully sent",'application_id':data['application_id'],"status_code":'200'})
            elif account_exist == False:
                # Return an message and status code
                return jsonify({"message": "application has been successfully sent","password":password,'application_id':data['application_id'],"status_code":'200'})


        except Exception as E:
            logging.info(E)
            driver.quit()
            # Return an error message and status code
            return jsonify({"message": f"Something Went Wrong!! {E}",'application_id':data['application_id'],"status_code":'400'})

    except Exception as E:
        logging.info(E)
        driver.quit()
        # Return an error message and status code
        return jsonify({"message": f"Something Went Wrong!! {E}",'application_id':data['application_id'],"status_code":'400'})

@app.route('/api/ostendis', methods=['POST'])
def ostendis():
    data = request.get_json()
    try:
        # Set up logging to write log messages to a file named 'ostendis.log' with INFO level
        logging.basicConfig(filename='ostendis.log', level=logging.INFO)
        # Create Chrome options for configuring the WebDriver
        chrome_options = Options()
        # run the Chrome browser in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        # Create a new instance of the Chrome WebDriver with the specified options
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        # Open the provided job ad URL in the Chrome browser
        driver.get(data['job']['job_ad_url'])
        try:
            time.sleep(2)
            expires = driver.find_element(By.CSS_SELECTOR,"div#headroom h1").text
            if expires == 'Inserat abgelaufen oder gelöscht.':
                return jsonify({"message": "this job application is not available", 'application_id': data['application_id'],"status_code": '200'})
        except:
            pass
        driver.get(driver.find_element(By.CSS_SELECTOR,"a.btn.btn-primary").get_attribute('href'))

        try:
            # Use WebDriverWait to wait up to 6 seconds until a specific element with CSS selector 'p.card-text' is present,
            # then retrieve its text content
            job_not_available = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p.card-text'))).text
            # Check if the text contains a specific message indicating that the application deadline has expired
            if 'Vielen Dank für Ihr Interesse an dieser Stelle. Da die Bewerbungsfrist bereits abgelaufen ist' in job_not_available:
                # If the message is found, quit the WebDriver, and return a response indicating the expired deadline
                driver.quit()
                return jsonify({"message": "the application deadline has already expired", 'application_id': data['application_id'],"status_code": '200'})
        except:
            pass

        # Check the gender of the applicant specified in the 'data' dictionary
        if data['applicant']['gender'] == 'male':
            # If the gender is male, wait for up to 20 seconds until the male gender input element is present, then click it
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#CVdropperSexID-M'))).click()

        elif data['applicant']['gender'] == 'female':
            # If the gender is female, wait for up to 20 seconds until the male gender input element is present, then click it
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#CVdropperSexID-F'))).click()
        else:
            # If the gender is not male or female, assume it's another gender ('D') and wait for up to 20 seconds
            # until the respective gender input element is present, then click it
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#CVdropperSexID-D'))).click()

        # Input the applicant's first name into the corresponding input field with the ID 'CVdropperFirstName'
        driver.find_element(By.CSS_SELECTOR,"input#CVdropperFirstName").send_keys(data['applicant']['firstname'])
        time.sleep(2)
        # Input the applicant's last name into the corresponding input field with the ID 'CVdropperLastName'
        driver.find_element(By.CSS_SELECTOR,"input#CVdropperLastName").send_keys(data['applicant']['lastname'])
        time.sleep(2)
        # Input the applicant's email into the corresponding input field with the ID 'CVdropperApplicationEmail'
        driver.find_element(By.CSS_SELECTOR,"input#CVdropperApplicationEmail").send_keys(data['applicant']['email'])
        time.sleep(2)
        # Click on the checkbox element using the general 'input' type selector
        driver.find_element(By.CSS_SELECTOR,'input[type="checkbox"]').click()
        time.sleep(2)

        # Specify the desired filename for the downloaded CV

        file_name = 'cv.pdf'
        # Download the CV from the specified URL in the 'documents' section of the 'data' dictionary
        download_cv(data['documents'][0]['url'], file_name)
        # Locate the file input element using the CSS selector and provide the path of the downloaded CV file
        driver.find_element(By.CSS_SELECTOR, 'input[type="file"]').send_keys(os.getcwd() + '//' + file_name)

        # Create an infinite loop to repeatedly attempt the following actions
        while True:
            try:
                # Save a screenshot before clicking the submit button
                driver.save_screenshot("ostendis_before.png")
                # Wait for up to 15 seconds until the submit button with ID 'submitAll' is present, then click it
                if data['dry_run'] == True:
                    driver.quit()
                    return jsonify({"message": "for test dry run", 'application_id': data['application_id'],"status_code": '200'})
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button#submitAll'))).click()
                # Break out of the loop after successfully clicking the submit button
                break
            except:
                time.sleep(3)
                pass

        time.sleep(4)

        try:
            # Wait for up to 15 seconds until the success alert with CSS selector 'div#confirmation div.alert.alert-success' is present,
            # then retrieve its text content
            alert_message  = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#confirmation div.alert.alert-success'))).text
            # Check if the alert message matches the expected success message
            if "Herzlichen Dank, Ihre Daten wurden erfolgreich übermittelt. Sie können diese Seite nun schliessen." == alert_message:
                # Save a screenshot after successfully submitting the application
                driver.save_screenshot("ostendis_after.png")
                # Quit the WebDriver
                driver.quit()
                # Return a success response with a message and status code
                return jsonify({"message": "application has been successfully sent", 'application_id': data['application_id'],"status_code": '200'})
            else:
                driver.save_screenshot("ostendis_after.png")
                # If the alert message doesn't match the expected success message, still consider it a success and return a response
                driver.quit()
                return jsonify({"message": "application has been successfully sent", 'application_id': data['application_id'],"status_code": '200'})
        except Exception as E:
            driver.save_screenshot("ostendis_after.png")
            # If an exception occurs during the process, quit the WebDriver and return an error response with a message and status code
            driver.quit()
            return jsonify({"message": f"Something Went Wrong!! {E}", 'application_id': data['application_id'],"status_code": '400'})



    except Exception as E:

        logging.info(E)
        driver.quit()
        return jsonify({"message": f"Something Went Wrong!! {E}",'application_id': data['application_id'],"status_code": '400'})

@app.route('/api/ernstselmoni', methods=['POST'])
def ernstselmoni():
    data = request.get_json()
    try:
        # Set up logging to save information to a log file named 'ernstselmoni.log' with INFO level
        logging.basicConfig(filename='ernstselmoni.log', level=logging.INFO)
        # Create ChromeOptions object to configure the behavior of the ChromeDriver
        chrome_options = Options()
        # run Chrome in headless mode (without a visible GUI)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        # Initialize a new instance of the Chrome WebDriver with the specified options
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # Navigate to the job advertisement URL provided in the 'data' dictionary
        driver.get(data['job']['job_ad_url'])
        try:
            driver.get(driver.find_element(By.CSS_SELECTOR,"a.btn.button").get_attribute('href'))
        except:
            return jsonify({"message": "this job application is not available", 'application_id': data['application_id'],"status_code": '200'})
        # Check the gender of the applicant and select the corresponding option in a dropdown menu
        if data['applicant']['gender'] == 'male':
            # Wait up to 15 seconds for the presence of an element and click on the specified option
            WebDriverWait(driver, 15).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'select[name="customeraddressshopperanrede"] option[value="1"]'))).click()
        elif data['applicant']['gender'] == 'female':
            # Wait up to 15 seconds for the presence of an element and click on the specified option
            WebDriverWait(driver, 15).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'select[name="customeraddressshopperanrede"] option[value="2"]'))).click()
        else:
            # If the gender is not male or female, assume another option and click on it
            WebDriverWait(driver, 15).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'select[name="customeraddressshopperanrede"] option[value="4"]'))).click()

        # Wait up to 15 seconds for the presence of an element and enter the applicant's first name
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="customeraddressshoppervorname"]'))).send_keys(
            data['applicant']['firstname'])
        # Wait up to 15 seconds for the presence of an element and enter the applicant's last name
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="customeraddressshoppername"]'))).send_keys(
            data['applicant']['lastname'])
        # Wait up to 15 seconds for the presence of an element and enter the applicant's street address
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[name="customeraddressstreetwithouthousenumber"]'))).send_keys(
            data['applicant']['street'])
        # Wait up to 15 seconds for the presence of an element and enter the applicant's ZIP code
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="customeraddressshopperplz"]'))).send_keys(
            data['applicant']['zip'])
        # Wait up to 15 seconds for the presence of an element and enter the applicant's city
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="customeraddressshopperort"]'))).send_keys(
            data['applicant']['city'])
        # Wait up to 15 seconds for the presence of an element and select the applicant's country from a dropdown
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                        'select[name="customeraddressshopperland"] option[value="' + f'{data["applicant"]["country"]}' + '"]'))).click()
        # Wait up to 15 seconds for the presence of an element and enter the applicant's mobile phone number
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="customeraddressshoppermobile"]'))).send_keys(
            data["applicant"]['phone'])
        # Wait up to 15 seconds for the presence of an element and enter the applicant's email address
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[name="customeraddressshopperaddressemail"]'))).send_keys(
            data["applicant"]['email'])
        # Wait up to 15 seconds for the presence of an element and enter the applicant's birthdate
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="DateOfBirth"]'))).send_keys(
            data["applicant"]['birthdate'])

        # Specify the file name for the CV file to be downloaded
        file_name = 'cv.pdf'
        # Download the CV file from the specified URL using a custom function (download_cv)
        download_cv(data['documents'][0]['url'], file_name)

        # Wait up to 15 seconds for the presence of an element and upload the CV file using the input[type="file"] element
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))).send_keys(
            os.getcwd() + '//' + file_name)
        time.sleep(3)

        # Extract the data-sitekey attribute value from the <div> with class 'g-recaptcha'

        data_site_key = driver.find_element(By.CSS_SELECTOR, "div.g-recaptcha").get_attribute('data-sitekey')
        while True:
            try:
                # Call a custom function (solve_recaptcha) to solve the reCAPTCHA with the extracted data-sitekey
                result_captcha = solve_recaptha(data_site_key, data['job']['job_ad_url'])
                time.sleep(2)
                # Break out of the loop if reCAPTCHA is successfully solved
                break
            except:
                pass

        # Use JavaScript to set the innerHTML of the element with ID 'g-recaptcha-response' to the solved captcha code
        driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{result_captcha['code']}'")
        try:
            # If found, click the element
            driver.find_element(By.CSS_SELECTOR, 'a[aria-label="dismiss cookie message"]').click()
            time.sleep(1)
        except:
            pass

        # Wait up to 15 seconds for the presence of the input element with the name 'jobportal_taca' and click it
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="jobportal_taca"]'))).click()
        time.sleep(1)
        # Save a screenshot of the current state of the webpage with the filename 'ernstselmoni_before.png'
        driver.save_screenshot("ernstselmoni_before.png")
        # Click the input element with the name 'jobportal_application_submit'

        if data['dry_run'] == True:
            driver.quit()
            return jsonify({"message": "for test dry run", 'application_id': data['application_id'], "status_code": '200'})

        driver.find_element(By.CSS_SELECTOR, 'input[name="jobportal_application_submit"]').click()

        # Wait up to 6 seconds for the presence of the div element with class 'infoblock' and get its text content
        alert_message_sent = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.infoblock'))).text
        # Check if the substring "Besten Dank für Ihr Interesse" is present in the retrieved text
        if "Besten Dank für Ihr Interesse" in alert_message_sent:
            # Save a screenshot of the current state of the webpage with the filename 'ernstselmoni_after.png'
            driver.save_screenshot("ernstselmoni_after.png")
            driver.quit()
            # Return a success message along with application details and status code
            return jsonify({"message": "application has been successfully sent", 'application_id': data['application_id'],
                    "status_code": '200'})
        else:
            # Save a screenshot of the current state of the webpage with the filename 'ernstselmoni_after.png'
            driver.save_screenshot("ernstselmoni_after.png")
            # Quit the driver
            driver.quit()
            # Return an error message along with application details and status code
            return jsonify({"message": "Something Went Wrong!!", 'application_id': data['application_id'], "status_code": '400'})


    except Exception as E:
        logging.info(E)
        driver.save_screenshot("ernstselmoni_after.png")
        driver.quit()
        # Return an error message along with application details and status code
        return jsonify({"message": f"Something Went Wrong!! {E}", 'application_id': data['application_id'],
                "status_code": '400'})

@app.route('/api/swissholidaypark', methods=['POST'])
def swissholidaypark():
    def generate_random_string():
        # Generate 2 random alphabets
        random_letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))

        # Generate 1 random number
        random_number = random.randint(0, 9)

        # Concatenate the random letters and number to form a 3-character string
        random_string = f"{random_letters}{random_number}"

        return random_string

    # Set initial value for email_checkup variable to False
    data = request.get_json()
    email_checkup = False
    try:
        try:
            # Try to get the password from the provided data dictionary
            password = data['applicant']['password']
            account_exist = True
        except:
            account_exist = False
            password = '12345678$#aliA'

        # Configure logging to write logs to 'swissholidaypark.log' file with INFO level
        logging.basicConfig(filename='swissholidaypark.log', level=logging.INFO)
        chrome_options = Options()
        # Set up Chrome options for a headless browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        # Create a Chrome WebDriver instance with the specified options
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        # Open the job ad URL in the headless Chrome browser
        driver.get(data['job']['job_ad_url'])

        driver.get(driver.find_element(By.CSS_SELECTOR,'a[itemprop="applyUrl"]').get_attribute('href'))


        while True:
            # Check if email_checkup is True
            if email_checkup == True:
                # Split the email address and create a new email with a random string
                email_new = data['applicant']['email'].split('@')
                new_email_key = email_new[0]+generate_random_string()+'@'+email_new[-1]
                # Enter the new email in the corresponding input field
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#register_candidate_step1_email"))).send_keys(new_email_key)
            else:
                # If email_checkup is False, enter the original email in the input field
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#register_candidate_step1_email"))).send_keys(data['applicant']['email'])

            # Check the gender and perform corresponding actions
            if data['applicant']['gender'] == 'male':
                # Click on the Salutation dropdown
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[aria-label="Salutation"]'))).click()
                try:
                    # Iterate through Salutation options and click on "Mr"
                    for salutaion in WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.select2-results__option'))):
                        if salutaion.text == "Mr":
                            salutaion.click()
                except:
                    pass
            elif data['applicant']['gender'] == 'female':
                # Click on the Salutation dropdown
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[aria-label="Salutation"]'))).click()
                try:
                    # Iterate through Salutation options and click on "Ms"
                    for salutaion in WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.select2-results__option'))):
                        if salutaion.text == "Ms":
                            salutaion.click()
                except:
                    pass
            else:
                # Click on the Salutation dropdown
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[aria-label="Salutation"]'))).click()
                try:
                    # Iterate through Salutation options and click on "Diverse"
                    for salutaion in WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.select2-results__option'))):
                        if salutaion.text == "Diverse":
                            salutaion.click()
                except:
                    pass

            # Fill First Name
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#register_candidate_step1_profile_firstname"))).send_keys(data['applicant']['firstname'])
            # Fill Last Name
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#register_candidate_step1_profile_lastname"))).send_keys(data['applicant']['lastname'])
            # Fill Phone
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#register_candidate_step1_profile_phone"))).send_keys(data['applicant']['phone'])
            # Fill Street
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#register_candidate_step1_profile_address_street_name"))).send_keys(data['applicant']['street'])
            # Fill Zip Code
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#register_candidate_step1_profile_address_zipCode"))).send_keys(data['applicant']['zip'])
            # Fill City
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#register_candidate_step1_profile_address_city_name"))).send_keys(data['applicant']['city'])
            # Check the box for extended data persistence
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'label[for="register_candidate_step1_hasExtendedDataPersistence"]'))).click()
            # Click the submit button
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button#submitButton'))).click()
            time.sleep(3)
            # Try to locate and capture the warning text within a specific element
            try:
                warning_text = WebDriverWait(driver, 7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div#registrationErrorWarning'))).text
            except:
                warning_text = ""
            # Check if the warning text contains a specific message indicating an existing email address
            if 'This e-mail address is being used already.' in warning_text:
                # If the warning indicates an existing email address, perform the following actions:
                # Click on the "No account yet? Register now." link
                driver.find_element(By.CSS_SELECTOR, 'input[value="No account yet? Register now."]').click()
                # Refresh the page
                driver.refresh()
                # Set a flag to indicate that an email checkup is needed
                email_checkup = True
            else:
                break

        try:
            # Attempt to click the submit button with a timeout of 15 seconds
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button#submitButton'))).click()
            time.sleep(3)
        except:
            pass

        # Set the file_name variable to 'cv.pdf'
        file_name = 'cv.pdf'
        # Download the CV from the specified URL and save it with the given file name
        download_cv(data['documents'][0]['url'], file_name)

        # Locate the input element with the ID 'formDocument' and send the file path to it
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#formDocument'))).send_keys(os.getcwd() + '//' + file_name)
        time.sleep(7)

        # Retrieve the text of the label associated with the input element with the attribute 'for' set to 'formDocument'
        cv_upload = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'label[for="formDocument"]'))).text

        # Check if the text retrieved from the label associated with 'formDocument' is 'UPLOAD AGAIN'
        if cv_upload == 'UPLOAD AGAIN':
            # Click the 'submitButton' button twice with pauses in between because of delay issue
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button#submitButton'))).click()
            time.sleep(2)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button#submitButton'))).click()
            time.sleep(2)
            # Click the element with ID 'select2-jobApplicationSource-container' to open a dropdown
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span#select2-jobApplicationSource-container'))).click()
            time.sleep(2)

            # Try to locate and click the 'Homepage' option in the dropdown
            try:
                for job_opportunity in WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.select2-results__option"))):
                    if job_opportunity.text == 'Homepage':
                        job_opportunity.click()
            except:
                pass
            # Capture a screenshot before clicking the 'submitButton'
            driver.save_screenshot("swissholidaypark_before.png")
            if data['dry_run'] == True:
                return jsonify({"message": "for test dry run", 'application_id': data['application_id'], "status_code": '200'})
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button#submitButton'))).click()
            # Retrieve the text of the alert message and check if it's 'Thank you for your application!'
            alert_message = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.alert h3'))).text
            if alert_message == 'Thank you for your application!':
                driver.save_screenshot("swissholidaypark_after.png")
                # Quit the driver and return a success message with application id and status code
                driver.quit()
                return jsonify({"message": "application has been successfully sent",'application_id':data['application_id'],"status_code":'200'})


    except Exception as E:
        logging.info(E)
        driver.save_screenshot("swissholidaypark_after.png")
        driver.quit()
        # Quit the driver and return a error message with application id and status code
        return jsonify({"message": "Something Went Wrong!!",'application_id':data['application_id'],"status_code":'400'})

@app.route('/api/fenacocareer', methods=['POST'])
def fenacocareer():
    try:
        data = request.get_json()
        # Configure logging to write messages to 'fenacocareer.log' file at INFO level
        logging.basicConfig(filename='fenacocareer.log', level=logging.INFO)
        try:
            # Try to access the 'password' field from the 'data' dictionary under 'applicant' key
            password = data['applicant']['password']
            # If the above line succeeds, set 'account_exist' to True
            account_exist = True
        except:
            # Set a default password in case the 'password' field is not found
            account_exist = False
            password = '12345678$#aliA'

        # Create Chrome options to customize the behavior of the Chrome browser
        chrome_options = Options()
        #run the browser in headless mode (without a visible UI)
        # chrome_options.add_argument("--headless")
        # Create a new instance of the Chrome WebDriver with the specified options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        # Maximize the browser window to ensure elements are visible
        driver.maximize_window()
        # Navigate to the specified job advertisement URL from the 'data' dictionary
        driver.get(data['job']['job_ad_url'])
        # Wait until the 'Login' input field is present in the DOM and visible
        # Then, enter the applicant's email into the 'Login' input field
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            if 'Wir bedauern, diese Vakanz wurde bereits wieder geschlossen.' in driver.find_element(By.CSS_SELECTOR,"div#siteframe").text:
                driver.quit()
                return jsonify({"message": "this job application is not available", 'application_id': data['application_id'],"status_code": '200'})
        except:
            pass
        try:
            driver.get(driver.find_element(By.CSS_SELECTOR,"a.apply-link").get_attribute('href'))
        except:
            pass
        try:
            driver.get(driver.find_element(By.CSS_SELECTOR,"a.apply").get_attribute('href'))
        except:
            pass
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#Login"))).send_keys(data['applicant']['email'])
        except:
            driver.quit()
            return jsonify(
                {"message": "this job application is not available", 'application_id': data['application_id'],
                 "status_code": '200'})

        time.sleep(2)
        # Wait until the 'Password' input field is present in the DOM and visible
        # Then, enter the applicant's password into the 'Password' input field
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#Password"))).send_keys(password)
        time.sleep(2)
        # Wait until the 'btnConnexion' button is present in the DOM and visible
        # Then, click the 'btnConnexion' button to submit the login form
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#btnConnexion"))).click()

        time.sleep(1)
        # Check the gender of the applicant from the 'data' dictionary
        if data['applicant']['gender'] =='male':
            # If the gender is male, locate the corresponding option in the dropdown list and click it
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_GeneralInfoEdit_SubFormApplicant_ctl00_fldapplicant_civility_Civility option[value="1021"]'))).click()

        elif data['applicant']['gender'] =='female':
            # If the gender is female, locate the corresponding option in the dropdown list and click it
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_GeneralInfoEdit_SubFormApplicant_ctl00_fldapplicant_civility_Civility option[value="1020"]'))).click()

        else:
            # If the gender is not specified or any other value, use a default option in the dropdown list and click it
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_GeneralInfoEdit_SubFormApplicant_ctl00_fldapplicant_civility_Civility option[value="2388"]'))).click()

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified input field identified by CSS selector
        first_name = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[name="ctl00$ctl00$corpsRoot$corps$applicantFieldsForm$GeneralInfoEdit$SubFormApplicant$ctl00$fldapplicant_firstname$FirstName"]')))
        # Clear the existing content in the 'first_name' input field
        first_name.clear()
        # Enter the applicant's first name into the 'first_name' input field using data from the 'applicant' dictionary
        first_name.send_keys(data['applicant']['firstname'])

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified input field identified by CSS selector
        last_name =WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[name="ctl00$ctl00$corpsRoot$corps$applicantFieldsForm$GeneralInfoEdit$SubFormApplicant$ctl00$fldapplicant_name$Name"]')))
        # Clear the existing content in the 'last_name' input field
        last_name.clear()
        # Enter the applicant's last name into the 'last_name' input field using data from the 'applicant' dictionary
        last_name.send_keys(data['applicant']['lastname'])

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified textarea identified by CSS selector
        address_element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[name="ctl00$ctl00$corpsRoot$corps$applicantFieldsForm$PersonalInformationEdit$SubFormPersonalInformation$ctl00$fldpersonalinformation_address$Address"]')))
        # Clear the existing content in the 'address_element' textarea
        address_element.clear()
        # Enter the applicant's street address into the 'address_element' textarea using data from the 'applicant' dictionary
        address_element.send_keys(data['applicant']['street'])

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified input field identified by CSS selector
        postal_code = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="ctl00$ctl00$corpsRoot$corps$applicantFieldsForm$PersonalInformationEdit$SubFormPersonalInformation$ctl00$fldpersonalinformation_postalcode$PostalCode"]')))
        # Clear the existing content in the 'postal_code' input field
        postal_code.clear()
        # Enter the applicant's postal code (zip code) into the 'postal_code' input field using data from the 'applicant' dictionary
        postal_code.send_keys(data['applicant']['zip'])

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified input field identified by CSS selector
        city_element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="ctl00$ctl00$corpsRoot$corps$applicantFieldsForm$PersonalInformationEdit$SubFormPersonalInformation$ctl00$fldpersonalinformation_city$City"]')))
        # Clear the existing content in the 'city_element' input field
        city_element.clear()
        # Concatenate the applicant's city and state and enter it into the 'city_element' input field
        # City and state are retrieved from the 'applicant' dictionary in the 'data' variable
        city_element.send_keys(data['applicant']['city']+', '+data['applicant']['state'])

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified input field identified by CSS selector
        phone_number_elemt =WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="ctl00$ctl00$corpsRoot$corps$applicantFieldsForm$PersonalInformationEdit$SubFormPersonalInformation$ctl00$fldpersonalinformation_phonenumber1$PhoneNumber1"]')))
        # Clear the existing content in the 'phone_number' input field
        phone_number_elemt.clear()
        # Enter the applicant's phone number into the 'phone_number' input field using data from the 'applicant' dictionary
        phone_number_elemt.send_keys(data['applicant']['phone'])

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified input field identified by CSS selector
        birthdate_element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="ctl00$ctl00$corpsRoot$corps$applicantFieldsForm$PersonalInformationEdit$SubFormPersonalInformation$ctl00$fldpersonalinformation_birthdate$BirthDate"]')))
        # Clear the existing content in the 'birthdate_element' input field
        birthdate_element.clear()
        # Enter the applicant's birthdate into the 'birthdate_element' input field using data from the 'applicant' dictionary
        birthdate_element.send_keys(data['applicant']['birthdate'])

        # Use WebDriverWait to wait up to 15 seconds for the presence of all option elements within the specified dropdown list identified by CSS selector
        for loop_country in WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_PersonalInformationEdit_SubFormPersonalInformation_ctl00_fldpersonalinformation_residencecountry_ResidenceCountry option'))):
            # Check if the country from the 'applicant' dictionary is present in the text of the current option
            if data['applicant']['country'] in loop_country.text:
                # If found, get the value attribute of the option
                option_value = loop_country.get_attribute('value')
                # Locate and click the option with the identified value in the dropdown list
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,f'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_PersonalInformationEdit_SubFormPersonalInformation_ctl00_fldpersonalinformation_residencecountry_ResidenceCountry option[value="{option_value}"]'))).click()
                break

        # Use WebDriverWait to wait up to 15 seconds for the presence of all option elements within the specified dropdown list identified by CSS selector
        for nationality in WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_PersonalInformationEdit_SubFormPersonalInformation_ctl00_fldpersonalinformation_applicantnationalitycollection_ApplicantNationalityCollection option'))):
            # Check if the text of the current nationality option is present in the 'nationality' list of the 'applicant' dictionary
            if nationality.text in data['applicant']['nationality']:
                # If found, get the value attribute of the option
                nationaliyt_option = nationality.get_attribute('value')
                # Locate and click the option with the identified value in the dropdown list
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,f'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_PersonalInformationEdit_SubFormPersonalInformation_ctl00_fldpersonalinformation_applicantnationalitycollection_ApplicantNationalityCollection option[value="{nationaliyt_option}"]'))).click()

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified option element in the first dropdown list identified by CSS selector
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,f'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_FurtherInformationEdit_SubFormFurtherInformation_ctl00_fldfurtherinformation_customcodetablevalue2_CustomCodeTableValue2 option[value="3374"]'))).click()
        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified option element in the second dropdown list identified by CSS selector
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,f'select#ctl00_ctl00_corpsRoot_corps_applicantFieldsForm_FurtherInformationEdit_SubFormFurtherInformation_ctl00_fldfurtherinformation_customcodetablevalue3_CustomCodeTableValue3 option[value="1754"]'))).click()

        # Set the file_name variable to 'cv.pdf'
        file_name = 'cv.pdf'
        # Download the CV file from the specified URL in the 'documents' dictionary
        download_cv(data['documents'][0]['url'], file_name)

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified link and click it
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'a#ctl00_ctl00_corpsRoot_corps_formulairePJ_rptAttachedFile_ctl00_MultiPJAndSelection_BlocPJ_rptLoadedFiles_ctl00_DisplayAttchedFileControl_btnModifyAttachedFileImprovedHtml'))).click()
        time.sleep(2)
        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified input field, then set its value to the absolute path of the downloaded file
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[name="ctl00$ctl00$corpsRoot$corps$formulairePJ$rptAttachedFile$ctl00$MultiPJAndSelection$BlocPJ$rptLoadedFiles$ctl00$DisplayAttchedFileControl$PJUpload"]'))).send_keys(os.getcwd() + '//' + file_name)
        time.sleep(2)
        # Click on the 'Modify' button for the first attached file
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input#ctl00_ctl00_corpsRoot_corps_formulairePJ_rptAttachedFile_ctl00_MultiPJAndSelection_BlocPJ_rptLoadedFiles_ctl00_DisplayAttchedFileControl_btnModify'))).click()
        time.sleep(2)
        # Click on the 'Modify' button for the second attached file
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'a#ctl00_ctl00_corpsRoot_corps_formulairePJ_rptAttachedFile_ctl01_MultiPJAndSelection_BlocPJ_rptLoadedFiles_ctl00_DisplayAttchedFileControl_btnModifyAttachedFileImprovedHtml'))).click()
        time.sleep(2)
        # Upload a file for the second attached file
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[name="ctl00$ctl00$corpsRoot$corps$formulairePJ$rptAttachedFile$ctl01$MultiPJAndSelection$BlocPJ$rptLoadedFiles$ctl00$DisplayAttchedFileControl$PJUpload"]'))).send_keys(os.getcwd() + '//' + file_name)
        time.sleep(2)
        # Click on the 'Modify' button for the second attached file after the upload
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[name="ctl00$ctl00$corpsRoot$corps$formulairePJ$rptAttachedFile$ctl01$MultiPJAndSelection$BlocPJ$rptLoadedFiles$ctl00$DisplayAttchedFileControl$btnModify"]'))).click()
        time.sleep(2)
        # Upload a file for the third attached file
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[name="ctl00$ctl00$corpsRoot$corps$formulairePJ$rptAttachedFile$ctl02$MultiPJAndSelection$BlocPJ$UploadAttachedFileControl$PJ"]'))).send_keys(os.getcwd() + '//' + file_name)
        time.sleep(2)
        # Click on the 'Add' button for the third attached file after the upload
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[name="ctl00$ctl00$corpsRoot$corps$formulairePJ$rptAttachedFile$ctl02$MultiPJAndSelection$BlocPJ$UploadAttachedFileControl$btnAddPJ"]'))).click()
        time.sleep(2)
        # Click on the 'Delete' button for the third attached fil
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'a#ctl00_ctl00_corpsRoot_corps_formulairePJ_rptAttachedFile_ctl02_MultiPJAndSelection_BlocPJ_rptLoadedFiles_ctl00_DisplayAttchedFileControl_btnDeleteAttachedFileButtonImprovedHtml'))).click()
        time.sleep(4)
        # Select the last option in the dropdown for the first attached file
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'select[name="ctl00$ctl00$corpsRoot$corps$formulairePJ$rptAttachedFile$ctl00$MultiPJAndSelection$SelectionPJ$DDLPj"] option')))[-1].click()
        time.sleep(1)
        # Select the last option in the dropdown for the second attached file
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'select[name="ctl00$ctl00$corpsRoot$corps$formulairePJ$rptAttachedFile$ctl01$MultiPJAndSelection$SelectionPJ$DDLPj"] option')))[-1].click()

        time.sleep(1)
        # Click on the 'Submit' button
        driver.save_screenshot("fenacocareer_before.png")
        if data['dry_run'] == True:
            return jsonify({"message": "for test dry run", 'application_id': data['application_id'], "status_code": '200'})
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="ctl00$ctl00$corpsRoot$corps$bt_Envoyer"]'))).click()
        time.sleep(2)

        # Use WebDriverWait to wait up to 15 seconds for the presence of the specified div element identified by CSS selector
        if 'wurde erfolgreich gesendet' in WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#ctl00_ctl00_ctl07_ulInformation'))).text:
            # If the success message is found, quit the driver and return a success response
            driver.save_screenshot("fenacocareer_after.png")
            driver.quit()
            return jsonify({"message": "application has been successfully sent",'application_id':data['application_id'],"status_code":'200'})
        elif 'Der Benutzer hat sich bereits auf dieses Stellenangebot beworben' in WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#ctl00_ctl00_ctl07_defaultValidationSummary'))).text:
            # If the user has already applied message is found, quit the driver and return a response
            driver.save_screenshot("fenacocareer_after.png")
            driver.quit()
            return jsonify({"message": "you have already applied for this job thanks",'application_id':data['application_id'],"status_code":'200'})
        else:
            # If neither success nor already applied message is found, quit the driver and return an error response
            driver.save_screenshot("fenacocareer_after.png")
            driver.quit()
            return jsonify({"message": "Something Went Wrong!!",'application_id':data['application_id'],"status_code":'400'})

    except Exception as E:
        logging.info(E)
        driver.quit()
        return jsonify({"message": f"Something Went Wrong!! {E}",'application_id':data['application_id'],"status_code":'200'})

if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=int("3000"),debug=True)
    # app.run(host='127.0.0.1',port=int("5000"))
    app.run()
