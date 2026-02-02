import time
import random
import string
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
base = 10  
extra = random.randint(0, 97)  
tdelay = base + extra
def get_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def fill_form(driver):
    wait = WebDriverWait(driver, 5)
    
    # Wait for the form to load
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']")))
    except:
        print("Could not find questions. Form might not be loaded or is closed.")
        return False

    # Get all question containers
    questions = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
    
    for q in questions:
        try:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", q)
            # Small pause for scroll to finish, but kept short as requested
            time.sleep(0.2) 

            # Check for Radio Buttons (Multiple Choice)
            radios = q.find_elements(By.CSS_SELECTOR, "div[role='radio']")
            if radios:
                choice = random.choice(radios)
                driver.execute_script("arguments[0].click();", choice)
                time.sleep(0.1)
                continue
            
            # Check for Checkboxes
            checkboxes = q.find_elements(By.CSS_SELECTOR, "div[role='checkbox']")
            if checkboxes:
                # Always select at least 1
                count = len(checkboxes)
                if count > 0:
                    # Select random amount, but at least 1
                    num_to_select = random.randint(1, count)
                    choices = random.sample(checkboxes, num_to_select)
                    for cb in choices:
                        driver.execute_script("arguments[0].click();", cb)
                        time.sleep(0.1)
                continue
            
            # Check for Text Inputs
            text_inputs = q.find_elements(By.TAG_NAME, "input")
            text_areas = q.find_elements(By.TAG_NAME, "textarea")
            
            valid_inputs = [i for i in text_inputs if i.get_attribute("type") in ["text", "email", "url", "number", "tel"] and i.is_displayed()]
            all_text_fields = valid_inputs + [t for t in text_areas if t.is_displayed()]
            
            if all_text_fields:
                for tf in all_text_fields:
                    tf.click()
                    tf.clear()
                    tf.send_keys(get_random_string(random.randint(5, 20)))
                    time.sleep(0.1)
                continue
            
        except Exception as e:
            pass

    time.sleep(0.5)

    # Generic handling for Next/Submit buttons
    try:
        # Get all role='button' elements
        all_buttons = driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
        
        target_button = None
        
        # Priority 1: Exact text match for Submit/Next keywords
        for btn in all_buttons:
            if not btn.is_displayed(): continue
            txt = btn.text.lower()
            
            # Skip "Clear form" / "Back" buttons
            if any(x in txt for x in ["xóa", "clear", "hủy", "back", "quay lại"]):
                continue
                
            if any(x in txt for x in ["gửi", "submit", "tiếp", "next"]):
                target_button = btn
                # We want the LAST one usually (Submit is often at the end)
                # so we don't break; we let interaction loop continue to find the last match 
                # OR we just pick this one if we are confident. 
                # Google forms usually has Back | Next/Submit. So Next/Submit is last.
                
        # Priority 2: If no text match found, pick the last visible button that ISN'T a clear/back button
        if not target_button:
            visible_buttons = [b for b in all_buttons if b.is_displayed()]
            valid_buttons = []
            for btn in visible_buttons:
                txt = btn.text.lower()
                if not any(x in txt for x in ["xóa", "clear", "hủy", "back", "quay lại"]):
                    valid_buttons.append(btn)
            
            if valid_buttons:
                target_button = valid_buttons[-1]

        if target_button:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", target_button)
            return True
             
        print("Could not find any suitable submit/next button.")
        return False
    except Exception as e:
        print(f"Error clicking submit: {e}")
        return False

def wait_with_countdown(seconds):
    for i in range(seconds, 0, -1):
        print(f"{ConsoleColor.OKCYAN}Waiting... {i}s remaining   {ConsoleColor.ENDC}", end="\r")
        time.sleep(1)
    print(" " * 50, end="\r") # Clear line

def main():
    print("Enter Google Form URL:")
    url = input().strip()
    if not url: return

    try:
        count = int(input("How many times to spam? "))
    except:
        count = 10

    print("Initializing Browser...")
    
    driver = None
    
    # Try connecting to existing Chrome on port 9222 first
    try:
        print("Creating options...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        print("Attempting to connect to existing Chrome (port 9222)...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print(f"{ConsoleColor.OKGREEN}Connected to existing Chrome!{ConsoleColor.ENDC}")
    except Exception as e:
        print(f"Could not connect to existing Chrome: {e}")
        print("Launching new Chrome instance instead...")
        
        # Fallback to new instance
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-infobars")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as ex:
            print(f"{ConsoleColor.FAIL}Failed to launch Chrome: {ex}{ConsoleColor.ENDC}")
            return
            
    # Define ConsoleColor locally or import if not present (it was removed in previous step, adding back for safety or removing usage)
    # The previous full file replacement removed ConsoleColor class. Let's fix that or use plain print.
    # Re-adding simple ANSI codes for clarity if needed, or just plain print.
    
    successful = 0
    
    try:
        # Navigate if needed
        try:
            if url not in driver.current_url:
                driver.get(url)
        except:
             driver.get(url)
        
        for i in range(count):
            print(f"Form {i+1}/{count}...", end="\r")
            
            if fill_form(driver):
                try:
                    # Wait for confirmation to ensure submission happened
                    # Look for "Submit another response" or generic confirmation message
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'câu trả lời') or contains(text(), 'response')] or //a[contains(text(), 'hồi khác') or contains(text(), 'response')]"))
                    )
                    successful += 1
                    print(f"{ConsoleColor.OKGREEN}Submission Confirmed!{ConsoleColor.ENDC}")
                except:
                    print(f"{ConsoleColor.WARNING}Confirmation timeout. Assuming sent.{ConsoleColor.ENDC}")
                
                # Calculate random delay for this iteration
                # Base 600s (10 mins) + random 0-600s (up to 10 mins) = 10-20 minutes delay
                random_delay = 60 + random.randint(0, 60)
                
                print(f"Waiting {random_delay}s before next loop...")
                wait_with_countdown(random_delay)
                
                driver.get(url)
            else:
                print(f"{ConsoleColor.FAIL}Failed to fill/submit. Retrying in 10s...{ConsoleColor.ENDC}")
                wait_with_countdown(10)
                driver.get(url)
                
            # Loop continues...

        print(f"\nDone! Successfully filled {successful}/{count} times.")
        
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Only close if we launched it ourselves (detected by checking debug port capability maybe?)
        # Or just tell user to close.
        # If attached to existing, driver.quit() might NOT close the window but detach session, or close it. 
        # Usually driver.quit() closes the window.
        # Let's ask user.
        print("Script finished.")
        # input("Press Enter to close connection...")
        # driver.quit()

class ConsoleColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    main()