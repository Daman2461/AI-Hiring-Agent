import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from getpass import getpass

"""
WARNING: Scraping full LinkedIn profiles is against LinkedIn's Terms of Service. This script is for educational/demo use only.
Use at your own risk. For hackathon/personal use only.
"""

def linkedin_login(driver, username, password):
    driver.get('https://www.linkedin.com/login')
    time.sleep(2)
    user_input = driver.find_element(By.ID, 'username')
    pass_input = driver.find_element(By.ID, 'password')
    user_input.send_keys(username)
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)
    time.sleep(3)
    # Check for login success
    if 'feed' in driver.current_url or 'checkpoint' in driver.current_url:
        print('Login successful!')
        return True
    else:
        print('Login failed. Check credentials or complete CAPTCHA manually.')
        return False

def scrape_profile(driver, url):
    driver.get(url)
    time.sleep(3)
    profile = {"url": url}
    try:
        profile['name'] = driver.find_element(By.XPATH, '//h1').text.strip()
    except:
        profile['name'] = ''
    try:
        profile['headline'] = driver.find_element(By.XPATH, '//div[contains(@class, "text-body-medium") and @data-test-id="headline"]').text.strip()
    except:
        profile['headline'] = ''
    # Experience
    profile['experience'] = []
    try:
        exp_sections = driver.find_elements(By.XPATH, '//section[contains(@id, "experience") or contains(@class, "experience-section")]//li')
        for exp in exp_sections:
            try:
                title = exp.find_element(By.XPATH, './/span[contains(@class, "t-14") and contains(@class, "t-bold")]').text.strip()
            except:
                title = ''
            try:
                company = exp.find_element(By.XPATH, './/span[contains(@class, "t-14") and contains(@class, "t-normal")]').text.strip()
            except:
                company = ''
            try:
                date = exp.find_element(By.XPATH, './/span[contains(@class, "t-14") and contains(@class, "t-normal") and contains(@class, "t-black--light")]').text.strip()
            except:
                date = ''
            profile['experience'].append({"title": title, "company": company, "date": date})
    except:
        pass
    # Education
    profile['education'] = []
    try:
        edu_sections = driver.find_elements(By.XPATH, '//section[contains(@id, "education") or contains(@class, "education-section")]//li')
        for edu in edu_sections:
            try:
                school = edu.find_element(By.XPATH, './/span[contains(@class, "t-14") and contains(@class, "t-bold")]').text.strip()
            except:
                school = ''
            try:
                degree = edu.find_element(By.XPATH, './/span[contains(@class, "t-14") and contains(@class, "t-normal")]').text.strip()
            except:
                degree = ''
            profile['education'].append({"school": school, "degree": degree})
    except:
        pass
    # Skills
    profile['skills'] = []
    try:
        skills_btn = driver.find_element(By.XPATH, '//a[@data-control-name="skill_details"]')
        driver.execute_script("arguments[0].click();", skills_btn)
        time.sleep(2)
        skills = driver.find_elements(By.XPATH, '//span[contains(@class, "pv-skill-category-entity__name-text")]')
        for skill in skills:
            profile['skills'].append(skill.text.strip())
    except:
        pass
    return profile

def main():
    # Get LinkedIn credentials
    username = os.getenv('LINKEDIN_USER') or input('LinkedIn Email: ')
    password = os.getenv('LINKEDIN_PASS') or getpass('LinkedIn Password: ')
    # Load links from a file or list
    links_file = 'linkedin_links.txt'
    if os.path.exists(links_file):
        with open(links_file) as f:
            links = [line.strip() for line in f if line.strip()]
    else:
        links = []
        print(f'Put LinkedIn profile URLs (one per line) in {links_file}')
        return
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    if not linkedin_login(driver, username, password):
        driver.quit()
        return
    results = []
    for url in links:
        print(f'Scraping: {url}')
        profile = scrape_profile(driver, url)
        results.append(profile)
        time.sleep(2)
    driver.quit()
    with open('linkedin_profiles.json', 'w') as f:
        json.dump(results, f, indent=2)
    print('Saved all profiles to linkedin_profiles.json')

if __name__ == '__main__':
    main() 