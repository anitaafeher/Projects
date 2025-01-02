import streamlit as st 
import pandas as pd
import numpy as np
import datetime 
import re
import psycopg2 as ps


#connection
def get_connection():
     connection = ps.connect(
          dbname = 'codecool',
          user='postgres',
          password = 'postgres',
          host = 'localhost',
          port = '5432'
     )
     return connection

def save_data(first_name, middle_name, last_name, birthday, gender, phone, email):
     conn = get_connection()
     cursor = conn.cursor()
     sql = 'INSERT INTO personal_data (first_name, middle_name, last_name, birthday, gender, phone_number, email) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id'
     cursor.execute(sql, [first_name, middle_name, last_name, birthday, gender, phone, email])
     conn.commit()
     result = cursor.fetchone()
     if result is None:
        raise Exception("Failed to retrieve the ID after saving personal data.")
     id = result[0]
     cursor.close()
     conn.close()
     return id

def save_address(person_id, address1, address2, city, state, zipcode, country):
     conn = get_connection()
     cursor = conn.cursor()
     sql2 = 'INSERT INTO address_info (person_id, address_line_1, address_line_2, city, state_province, postal_zip_code, country) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING address_id'
     cursor.execute(sql2, [person_id, address1, address2, city, state, zipcode, country])
     conn.commit()
     result = cursor.fetchone()
     if result is None:
        raise Exception("Failed to retrieve the ID after saving address data.")
     address_id = result[0]
     cursor.close()
     conn.close()
     return address_id

def save_education(person_id, education, institution, gradyear):
     conn = get_connection()
     cursor = conn.cursor()
     sql3 = 'INSERT INTO EducationInformation (person_id, highest_level_of_education, institution, year_of_graduation) VALUES (%s, %s, %s, %s) RETURNING education_id'
     cursor.execute(sql3, [person_id, education, institution, gradyear])
     conn.commit()
     result = cursor.fetchone()
     if result is None:
        raise Exception("Failed to retrieve the ID after saving education data.")
     education_id = result[0]
     cursor.close()
     conn.close()
     return education_id

def save_employment(person_id, employment_status, position, company):
     conn = get_connection()
     cursor = conn.cursor()
     sql4 = 'INSERT INTO EmploymentInformation (person_id, current_employment_status, current_job_title_position, company_organization) VALUES (%s, %s, %s, %s) RETURNING employment_id'
     cursor.execute(sql4, [person_id, employment_status, position, company])
     conn.commit()
     result = cursor.fetchone()
     if result is None:
        raise Exception("Failed to retrieve the ID after saving employment data.")
     employment_id = result[0]
     cursor.close()
     conn.close()
     return employment_id

def get_data():
     conn = get_connection()
     cursor = conn.cursor()
     select = 'SELECT pd.id AS person_id, pd.first_name, pd.middle_name, pd.last_name, pd.birthday, pd.gender, pd.phone_number, pd.email, ai.address_line_1, ai.address_line_2, ai.city, ai.state_province, ai.postal_zip_code, ai.country, ei.highest_level_of_education, ei.institution, ei.year_of_graduation, emp.current_employment_status, emp.current_job_title_position, emp.company_organization FROM personal_data pd LEFT JOIN address_info ai ON pd.id = ai.person_id LEFT JOIN EducationInformation ei ON pd.id = ei.person_id LEFT JOIN EmploymentInformation emp ON pd.id = emp.person_id;'
     cursor.execute(select)
     records = cursor.fetchall()
     cursor.close()
     conn.close()
     return records

if 'page' not in st.session_state:
    st.session_state.page = 0

#for session_state - this will keep the filled data in the fields
for key in ['first_name', 'middle_name', 'last_name', 'birthday', 'gender', 'phone', 'email',
            'address1', 'address2', 'city', 'state', 'zipcode', 'country',
            'education', 'institution', 'gradyear', 'employment_status', 'company', 'position']:
    if key not in st.session_state:
        st.session_state[key] = ''

#page functions
def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1


st.title(":red[Personal Data Collector]") 



#Variables
min_date = datetime.date(1900, 1, 1) #1.
max_date = datetime.date.today() #1.
email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$' #1. 
countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua & Deps", "Argentina",
    "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh",
    "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia",
    "Bosnia Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina", "Burundi",
    "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Rep", "Chad", "Chile",
    "China", "Colombia", "Comoros", "Congo", "Congo Democratic Rep", "Costa Rica", "Croatia",
    "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic",
    "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
    "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana",
    "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras",
    "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland Republic", "Israel",
    "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
    "Korea North", "Korea South", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon",
    "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
    "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",
    "Montenegro", "Morocco", "Mozambique", "Myanmar, Burma", "Namibia", "Nauru", "Nepal",
    "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Norway", "Oman", "Pakistan",
    "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland",
    "Portugal", "Qatar", "Romania", "Russian Federation", "Rwanda", "St Kitts & Nevis",
    "St Lucia", "Saint Vincent & the Grenadines", "Samoa", "San Marino", "Sao Tome & Principe",
    "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia",
    "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka",
    "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan",
    "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey",
    "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
    "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam",
    "Yemen", "Zambia", "Zimbabwe"
] #2.
current_year = datetime.date.today().year #3.
years = list(range(1900, current_year + 1)) #3. 


#0. Welcome page 
if st.session_state.page == 0:
    st.header('Welcome to our site where we collect data', divider='red')
    st.markdown('just for funsies :face_with_monocle:')
    st.subheader('*Csaba & Anita*')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Fill Form', key='fill_form'):
            st.session_state.page = 1
    with col2:
        if st.button('See Policy', key='see_policy'):
            st.session_state.page = 'policy'


# Policy page
elif st.session_state.page == "policy":
    st.header("Data Collection and Storage Policy")

    st.markdown("""
    **Purpose of Data Collection**
    
    This application collects personal data to better understand user demographics and background information, including personal, address, education, and employment details. The data collected is solely for educational purposes in the context of this course and is not intended for commercial use.
    
    **Types of Data Collected**
    
    The following types of information may be collected:
    
    - **Personal Information**: Name, date of birth, and contact details.
    - **Address Information**: Residential address.
    - **Education Information**: Highest level of education, school name, and graduation date.
    - **Employment Information**: Current or most recent job title and employer.
    
    **Data Consent**
    
    By checking the consent checkbox and submitting the form, you agree to allow the collection, storage, and processing of your data as described in this policy.
    
    **Data Storage and Security**
    
    The data collected through this form will be securely stored in a PostgreSQL database, accessible only to authorized individuals within the scope of this educational project. All reasonable steps are taken to protect your data from unauthorized access.
    
    **Data Retention**
    
    Data will be retained only for the duration of this course project and will be permanently deleted upon project completion.
    
    **Your Rights**
    
    You may request to view, modify, or delete your data at any time by contacting the project administrator. Data deletion will be processed promptly upon request, provided it is within the course timeline.
    """)

    if st.button("Back to Welcome Page", key='back_to_welcome_page'):
        st.session_state.page = 0


#1. Personal details
elif st.session_state.page==1:
    st.header("Please fill in your personal information! :clipboard:", divider='red')

    st.session_state.first_name = st.text_input('Enter your firstname! ', value=st.session_state.first_name)
    st.session_state.middle_name = st.text_input('Enter your middle name! ', value=st.session_state.middle_name, placeholder='optional')
    st.session_state.last_name = st.text_input('Enter your last name! ', value=st.session_state.last_name)
    st.session_state.birthday = st.date_input('When is your birthday?', value=st.session_state.birthday if st.session_state.birthday else None, min_value=min_date, max_value=max_date)
    st.session_state.gender = st.radio('What is your gender? ', ['male','female', 'whatever you feel like'], index=['male', 'female', 'whatever you feel like'].index(st.session_state.gender) if st.session_state.gender else 0)
    st.session_state.phone = st.text_input('Please provide you phone number! ', value=st.session_state.phone)
    st.session_state.email = st.text_input('Please provide your e-mail address! ', value=st.session_state.email, placeholder='youremail@something.xyz')

# Validate email
    if st.session_state.email and not re.match(email_pattern, st.session_state.email):
        st.error("Please enter a valid email address!")

    #Navigation buttons
    if st.button("Previous", key='previous_personal'):
        prev_page()
    if st.button("Next", key='next_personal'):
        next_page()


#2. Address information
elif st.session_state.page==2:
    st.header("Please fill in your address information! :house_with_garden:", divider='red')

    st.session_state.address1 = st.text_input('Please, fill in your address! ', value=st.session_state.address1, placeholder='street name, house number')
    st.session_state.address2 = st.text_input('Please fill in your address! ', value=st.session_state.address2, placeholder='floor, door number - optional')
    st.session_state.city = st.text_input('Please, add your city! ', value=st.session_state.city, placeholder='e.g. Törtel')
    st.session_state.state = st.text_input('Please add your state/province! ', value=st.session_state.state, placeholder='optional')
    st.session_state.zipcode = st.text_input('Please, add your postal/ZIP code! ', value=st.session_state.zipcode)
    st.session_state.country = st.selectbox('Please, choose your country! ', countries, index=countries.index(st.session_state.country) if st.session_state.country in countries else 0)

    #Navigation buttons
    if st.button("Previous", key='previous_address'):
        prev_page()
    if st.button("Next", key='next_address'):
        next_page()

#3. Education
elif st.session_state.page==3:
    st.header("Please provide information about your education! :books:", divider='red')
    
    st.session_state.education = st.selectbox('What is your highest level of education? ', ("elementary", "high school", "bachelor's", "master's", "PhD"), index=["elementary", "high school", "bachelor's", "master's", "PhD"].index(st.session_state.education) if st.session_state.education else 0)
    st.session_state.institution = st.text_input('Where did you graduate?', value=st.session_state.institution)
    st.session_state.gradyear = st.selectbox('When did you graduate?', options=years, index=years.index(st.session_state.gradyear) if st.session_state.gradyear in years else 0)

    #Navigation buttons
    if st.button("Previous", key='previous_education'):
        prev_page()
    if st.button("Next", key='next_education'):
        next_page()

#4. Employment
elif st.session_state.page==4:
    st.header("Please share some details regarding your employment! :briefcase:" , divider='red')
    
    st.session_state.employment_status = st.selectbox('What is your current employment status? ', ("Employed", "Unemployed", "Student", "Entrepreneur/Self-employed", "Other"), index=("Employed", "Unemployed", "Student", "Entrepreneur/Self-employed", "Other").index(st.session_state.employment_status) if st.session_state.employment_status else 0)

    if st.session_state.employment_status == "Employed":
        st.session_state.company = st.text_input('Which company are you working for?', value=st.session_state.company)
        st.session_state.position = st.text_input('What is your current role/position within the company?', value=st.session_state.position)
        
        #Navigation button
    if st.button("Previous", key='previous_employment'):
        prev_page()
    if st.button("Next", key='next_employment'):
        next_page()


#End of form
elif st.session_state.get('page') == 5:
    st.header('Consent and Submission')
    st.subheader('*You have reached the end of our form. You can submit your information after clicking the consent box below. Thank you for your contribution!*')
    
    agree = st.checkbox("I agree to have my information collected and stored.")
    submit_clicked = st.button('Submit')

    if submit_clicked:
        if agree: #save data if consent is given
            try:
                person_id = save_data(st.session_state['first_name'], st.session_state['middle_name'], st.session_state['last_name'], st.session_state['birthday'], st.session_state['gender'], st.session_state['phone'], st.session_state['email'])
                save_address(person_id, st.session_state['address1'], st.session_state['address2'], st.session_state['city'], st.session_state['state'], st.session_state['zipcode'], st.session_state['country'])
                save_education(person_id, st.session_state['education'], st.session_state['institution'], st.session_state['gradyear'])
                save_employment(person_id, st.session_state['employment_status'], st.session_state['position'], st.session_state['company'] if st.session_state['employment_status'] == "Employed" else '')

                st.success(f"Your data has been collected successfully under ID: {id}")
            except Exception as e:
                st.error(f"An error occurred while saving your data: {e}")
        else:
            st.error("Please click the box above to agree before submitting your data.")

    col1, col2, col3 = st.columns(3)

    

    if st.session_state.get('action') == 'table':
        data = get_data()
        df = pd.DataFrame(data, columns=['person_id', 'first_name', 'middle_name', 'last_name', 'birthday', 'gender', 'phone_number', 'email', 
                                        'address_line_1', 'address_line_2', 'city', 'state_province', 'postal_zip_code', 'country', 
                                        'highest_level_of_education', 'institution', 'year_of_graduation', 
                                        'current_employment_status', 'current_job_title_position', 'company_organization'])
        st.dataframe(df)
        
    with col1:
        if st.button("Load data"):
            st.session_state.action = 'table'
            st.rerun()

    with col2:
        if st.button("Previous", key='previous_submit'):
            prev_page()
    with col3:
        if st.button('See Policy', key='see_policy'):
            st.session_state.page = 'policy'
