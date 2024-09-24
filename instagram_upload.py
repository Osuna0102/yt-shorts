from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def upload_video_to_instagram(video_file, title, username, password):
    # Initialize the WebDriver (Opera)
    options = webdriver.ChromeOptions()
    options.binary_location = r"C:\Users\Administrador\AppData\Local\Programs\Opera\opera.exe"  # Replace with the path to your Opera executable
    service = Service(executable_path=r"D:\Descargas\operadriver_win64\operadriver_win64\operadriver.exe")  # Replace with the path to your OperaDriver executable
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Open Instagram login page
        driver.get("https://www.instagram.com/accounts/login/")
        
        # Wait for the login fields to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        
        # Enter username and password
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        
        # Wait for the main page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav"))
        )
        
        # Navigate to the upload page
        driver.get("https://www.instagram.com/create/select/")
        
        # Wait for the file input to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "file"))
        )
        
        # Upload the video file
        file_input = driver.find_element(By.NAME, "file")
        file_input.send_keys(os.path.abspath(video_file))
        
        # Wait for the video to be processed and the next button to be clickable
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
        ).click()
        
        # Wait for the title input to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@aria-label='Write a caption…']"))
        )
        
        # Enter the title
        caption_input = driver.find_element(By.XPATH, "//textarea[@aria-label='Write a caption…']")
        caption_input.send_keys(title)
        
        # Click the share button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Share']"))
        ).click()
        
        # Wait for the upload to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Done']"))
        )
        
        print("Video uploaded to Instagram successfully.")
        
    finally:
        # Close the WebDriver
        driver.quit()

# Example usage
if __name__ == "__main__":
    username = "your_instagram_username"
    password = "your_instagram_password"
    video_file = "path_to_your_video.mp4"
    title = "Your video title"
    
    upload_video_to_instagram(video_file, title, username, password)