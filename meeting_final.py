from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

# ==========================================
# 1. HIGH-SPEED PROFILE SETUP (UNTOUCHED)
# ==========================================
chrome_options = Options()
profile_path = r"C:\Users\HP\Desktop\MyAutoProfile"
if not os.path.exists(profile_path):
    os.makedirs(profile_path)

chrome_options.add_argument(f"user-data-dir={profile_path}")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-allow-origins=*")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")
chrome_options.page_load_strategy = 'eager'
chrome_options.add_experimental_option("detach", True)

print("🚀 Launching Chrome at Max Speed...")
driver = webdriver.Chrome(options=chrome_options)
wait      = WebDriverWait(driver, 8)
fast_wait = WebDriverWait(driver, 2)
actions   = ActionChains(driver)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def js_click(element):
    """Guaranteed click via JS — bypasses overlays and React event quirks."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.02)
    driver.execute_script("arguments[0].click();", element)

def react_set_input(element, value):
    """Forces React-controlled <input> to register value via React's native setter."""
    driver.execute_script("""
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        nativeInputValueSetter.call(arguments[0], arguments[1]);
        arguments[0].dispatchEvent(new Event('input',    { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change',   { bubbles: true }));
        arguments[0].dispatchEvent(new FocusEvent('blur',{ bubbles: true }));
    """, element, value)

def open_dropdown_and_select(label_xpath, option_xpath, step_name, retries=3):
    """Opens a React-Select dropdown and selects the target option."""
    print(f"[*] Step: {step_name}")
    label = wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))
    for attempt in range(retries):
        try:
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.05)
            driver.execute_script(
                "arguments[0].parentElement"
                ".querySelector('input,[role=\"combobox\"],[class*=\"control\"],[class*=\"select\"]')"
                ".click();",
                label
            )
            option = WebDriverWait(driver, 1.0).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            js_click(option)
            print(f"    ✅ {step_name} selected.")
            return True
        except Exception:
            try:
                actions.move_to_element(label).move_by_offset(0, 40).click().perform()
                option = WebDriverWait(driver, 1.0).until(
                    EC.element_to_be_clickable((By.XPATH, option_xpath))
                )
                js_click(option)
                print(f"    ✅ {step_name} selected (fallback.)")
                return True
            except Exception:
                pass
    print(f"    ⚠️  {step_name} failed after {retries} retries.")
    return False

def wait_for_dropdown_to_load(label_xpath, timeout=8):
    """Polls until the dropdown control is no longer disabled/loading."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            label = driver.find_element(By.XPATH, label_xpath)
            ctrl = driver.execute_script(
                "return arguments[0].parentElement"
                ".querySelector('[class*=\"control\"],[class*=\"select\"]');",
                label
            )
            if ctrl:
                classes = ctrl.get_attribute("class") or ""
                if "disabled" not in classes and "loading" not in classes:
                    return True
        except Exception:
            pass
        time.sleep(0.1)
    return False

def click_room_card():
    """
    From HTML inspection:
      owl-item
        └─ lib-room-card  (Angular host — NO click handler here)
             └─ div.rmcrd  ← THE actual clickable element (has flex layout, image, text)
                  ├─ div.container → img + h4 "Meeting Room No 02"
                  └─ div (building info)

    Strategy: find the text node → walk UP to lib-room-card → querySelector('.rmcrd')
    Fallback: walk UP from text looking for div with class 'rmcrd' or 'pointer'
    """
    for room_text in ["Meeting Room No 02", "Meeting Room No. 02"]:
        try:
            text_el = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{room_text}')]")
                )
            )

            # JS: from text node → find lib-room-card → get .rmcrd inside it
            real_card = driver.execute_script("""
                var el = arguments[0];

                // Strategy 1: walk up to lib-room-card, then find .rmcrd inside
                var hostEl = null;
                for (var i = 0; i < 20; i++) {
                    if (!el || el.tagName === 'BODY') break;
                    var tag = (el.tagName || '').toUpperCase();
                    if (tag === 'LIB-ROOM-CARD') {
                        hostEl = el;
                        break;
                    }
                    el = el.parentElement;
                }

                if (hostEl) {
                    // .rmcrd is the real clickable div inside lib-room-card
                    var rmcrd = hostEl.querySelector('.rmcrd');
                    if (rmcrd) return rmcrd;

                    // fallback: first div child of lib-room-card shadow/content
                    var firstDiv = hostEl.querySelector('div');
                    if (firstDiv) return firstDiv;

                    return hostEl;
                }

                // Strategy 2: walk up from text node looking for .rmcrd directly
                el = arguments[0];
                for (var j = 0; j < 15; j++) {
                    if (!el || el.tagName === 'BODY') break;
                    var cls = el.className || '';
                    if (cls.indexOf('rmcrd') !== -1) return el;
                    el = el.parentElement;
                }

                // Strategy 3: owl-item → lib-room-card → .rmcrd
                el = arguments[0];
                for (var k = 0; k < 20; k++) {
                    if (!el || el.tagName === 'BODY') break;
                    var cls2 = el.className || '';
                    if (cls2.indexOf('owl-item') !== -1) {
                        var libCard = el.querySelector('lib-room-card');
                        if (libCard) {
                            var rmcrd2 = libCard.querySelector('.rmcrd');
                            if (rmcrd2) return rmcrd2;
                            var div = libCard.querySelector('div');
                            if (div) return div;
                            return libCard;
                        }
                        return el.firstElementChild;
                    }
                    el = el.parentElement;
                }

                return arguments[0].parentElement;
            """, text_el)

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", real_card)
            time.sleep(0.05)

            # Try JS click first (bypasses overlays)
            driver.execute_script("arguments[0].click();", real_card)
            time.sleep(0.1)

            # Also dispatch Angular-friendly mouse events in case JS click alone is not enough
            driver.execute_script("""
                var el = arguments[0];
                ['mouseenter', 'mouseover', 'mousedown', 'mouseup', 'click'].forEach(function(evtName) {
                    var evt = new MouseEvent(evtName, {bubbles: true, cancelable: true, view: window});
                    el.dispatchEvent(evt);
                });
            """, real_card)

            return True

        except Exception as e:
            print(f"    ⚠️  click_room_card attempt failed: {e}")
            continue

    return False

def paginate_and_find_room(max_pages=30):
    """
    Scans each results page; directly clicks the room card when found.
    Returns True if room was found+clicked, False otherwise.
    """
    print("[*] Scanning for 'Meeting Room No 02'...")

    next_btn_xpaths = [
        "//button[@aria-label='Next' or @aria-label='next' or @aria-label='>' or @title='Next']",
        "//button[normalize-space(text())='>']",
        "//a[normalize-space(text())='>']",
        "//button[normalize-space(text())='Next']",
        "//a[normalize-space(text())='Next']",
        "//button[.//*[contains(@class,'next') or contains(@class,'arrow-right') or contains(@class,'chevron-right')]]",
        "//*[contains(@class,'next') and not(@disabled)]",
        "//*[contains(@class,'pagination')]//li[last()]/button",
        "//*[contains(@class,'pagination')]//button[last()]",
    ]

    for page_num in range(1, max_pages + 1):
        print(f"    📄 Scanning page {page_num}...")
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH,
                    "//*[contains(@class,'card') or contains(@class,'room')"
                    " or contains(@class,'owl-item') or contains(text(),'Meeting Room')]"
                ))
            )
        except Exception:
            pass

        # Check if room text is visible on this page
        try:
            WebDriverWait(driver, 0.8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Meeting Room No 02')]")
                )
            )
            print(f"    🎯 'Meeting Room No 02' text found on page {page_num}!")
            return True  # Signal found; click happens in main flow
        except Exception:
            pass

        # Not found — go to next page
        next_clicked = False
        for xpath in next_btn_xpaths:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                disabled = btn.get_attribute("disabled")
                cls = btn.get_attribute("class") or ""
                if disabled or "disabled" in cls:
                    break
                js_click(btn)
                time.sleep(0.2)
                next_clicked = True
                break
            except Exception:
                continue

        if not next_clicked:
            print("    ⛔ No active Next button — end of results.")
            return False

    print("    ❌ Room not found across all pages.")
    return False


# ==========================================
# 3. MAIN EXECUTION
# ==========================================
try:
    print("⚡ Navigating to booking portal...")
    driver.get("https://peoplefirst.ril.com/webapp/#/crbs")
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//*[contains(text(), 'Create New Booking')]")
    ))
    print("    ✅ Portal loaded.")

    # ----------------------------------------------------------
    # STEP 1: LOCATION → Reliance Corporate Park
    # ----------------------------------------------------------
    open_dropdown_and_select(
        label_xpath  = "//*[normalize-space()='Location']",
        option_xpath = "//*[contains(text(), 'Reliance Corporate Park')]",
        step_name    = "Location → Reliance Corporate Park"
    )

    # ----------------------------------------------------------
    # STEP 2: BOOKING DATE → 12/6/2026
    # ----------------------------------------------------------
    print("[*] Step: Booking Date → 12/6/2026...")
    actions.send_keys(Keys.ESCAPE).perform()
    date_input = wait.until(EC.element_to_be_clickable((By.XPATH,
        "(//label[normalize-space()='Booking Date']/following::input)[1]"
        " | (//*[normalize-space()='Booking Date']/following::input)[1]"
    )))
    js_click(date_input)
    time.sleep(0.05)
    react_set_input(date_input, "12/6/2026")
    time.sleep(0.05)
    date_input.send_keys(Keys.TAB)
    print("    ✅ Booking Date set.")

    # ----------------------------------------------------------
    # STEP 3: START TIME → 20:00
    # ----------------------------------------------------------
    open_dropdown_and_select(
        label_xpath  = "//*[normalize-space()='Start Time']",
        option_xpath = "(//*[normalize-space()='20:00'])[last()]",
        step_name    = "Start Time → 20:00"
    )

    # ----------------------------------------------------------
    # STEP 4: END TIME → 22:00
    # ----------------------------------------------------------
    open_dropdown_and_select(
        label_xpath  = "//*[normalize-space()='End Time']",
        option_xpath = "(//*[normalize-space()='22:00'])[last()]",
        step_name    = "End Time → 22:00"
    )

    # ----------------------------------------------------------
    # STEP 5: BUILDING → Building 30-2F
    # ----------------------------------------------------------
    print("[*] Waiting for Building dropdown AJAX...")
    wait_for_dropdown_to_load("//*[normalize-space()='Building']", timeout=4)
    open_dropdown_and_select(
        label_xpath  = "//*[normalize-space()='Building']",
        option_xpath = "(//*[contains(text(), 'Building 30-2F') or contains(text(), '30-2F')])[last()]",
        step_name    = "Building → Building 30-2F"
    )

    # ----------------------------------------------------------
    # STEP 6: WING → E
    # ----------------------------------------------------------
    print("[*] Waiting for Wing dropdown AJAX...")
    wait_for_dropdown_to_load("//*[normalize-space()='Wing']", timeout=3)
    open_dropdown_and_select(
        label_xpath  = "//*[normalize-space()='Wing']",
        option_xpath = "(//*[normalize-space()='E' or text()='E'])[last()]",
        step_name    = "Wing → E"
    )

    # ----------------------------------------------------------
    # STEP 7: SEARCH AVAILABLE ROOMS
    # ----------------------------------------------------------
    print("[*] Clicking 'Search Available Rooms'...")
    actions.send_keys(Keys.ESCAPE).perform()
    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//button[contains(text(), 'Search Available Rooms')]"
        " | //*[contains(text(), 'Search Available Rooms')]"
    )))
    js_click(search_btn)
    print("    ✅ Search triggered. Waiting for room cards...")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,
            "//*[contains(text(),'Meeting Room') or contains(text(),'VC Room')]"
        ))
    )
    print("    ✅ Room results loaded.")

    # ----------------------------------------------------------
    # STEP 8: PAGINATE UNTIL "Meeting Room No 02" IS VISIBLE
    # ----------------------------------------------------------
    found = paginate_and_find_room(max_pages=30)
    if not found:
        raise Exception("'Meeting Room No 02' not found across all result pages.")

    # ----------------------------------------------------------
    # STEP 9: CLICK THE ACTUAL INNER CARD (not owl-item wrapper)
    # ----------------------------------------------------------
    print("[*] Clicking room card (inner element)...")
    clicked = click_room_card()
    if not clicked:
        raise Exception("Failed to click room card after finding it.")
    print("    ✅ Room card clicked.")
    time.sleep(0.4)  # extra wait for Angular modal animation

    # ----------------------------------------------------------
    # STEP 10: TERMS & CONDITIONS → "I agree"
    # ----------------------------------------------------------
    print("[*] Waiting for Terms & Conditions modal...")

    # Step 10a: single JS poll — checks ALL selectors every 50ms, no wasted timeouts
    tc_found = driver.execute_script("""
        var deadline = Date.now() + 6000;
        function check() {
            var selectors = [
                '[role="dialog"]',
                'mat-dialog-container',
                '.modal',
                '.dialog',
                '[class*="modal"]',
                '[class*="dialog"]'
            ];
            for (var i = 0; i < selectors.length; i++) {
                if (document.querySelector(selectors[i])) return true;
            }
            // also check text
            var all = document.querySelectorAll('*');
            for (var j = 0; j < all.length; j++) {
                var t = all[j].textContent || '';
                if (t.indexOf('Terms') !== -1 && t.indexOf('Conditions') !== -1
                    && all[j].children.length < 5) return true;
            }
            return false;
        }
        var start = Date.now();
        while (Date.now() < deadline) {
            if (check()) return true;
        }
        return false;
    """)
    if not tc_found:
        raise Exception("T&C modal did not appear after room card click.")
    print("    ✅ T&C modal appeared.")

    # Step 10c: single wait with all variants combined via | operator
    agree_btn = None
    try:
        agree_btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,
            "//button[normalize-space()='I agree']"
            " | //button[normalize-space()='I Agree']"
            " | //button[normalize-space()='Agree']"
            " | //button[normalize-space()='AGREE']"
            " | //button[normalize-space()='Accept']"
            " | //button[normalize-space()='OK']"
            " | //button[normalize-space()='Proceed']"
            " | //button[normalize-space()='Continue']"
            " | //button[contains(text(),'gree')]"
            " | //button[contains(text(),'ccept')]"
            " | //button[contains(text(),'roceed')]"
            " | //*[@role='button'][contains(normalize-space(),'gree') or contains(normalize-space(),'ccept')]"
        )))
        print(f"    ✅ Agree button found: '{agree_btn.text.strip()}'")
    except Exception:
        pass

    # Step 10d: fallback — click the LAST visible button inside the modal
    if agree_btn is None:
        print("    ⚠️  Named XPath failed — trying last-button-in-modal fallback...")
        for mxp in ["//*[@role='dialog']", "//mat-dialog-container", "//*[contains(@class,'modal')]", "//*[contains(@class,'dialog')]", "//body"]:
            try:
                modal = driver.find_element(By.XPATH, mxp)
                btns = modal.find_elements(By.XPATH, ".//button | .//*[@role='button']")
                vis_btns = [b for b in btns if b.is_displayed()]
                if vis_btns:
                    agree_btn = vis_btns[-1]
                    print(f"    ✅ Using last visible button: '{agree_btn.text.strip()}'")
                    break
            except Exception:
                continue

    if agree_btn is None:
        raise Exception("Could not find any agree/accept button. Check debug button list above.")

    js_click(agree_btn)
    print("    ✅ 'I agree' clicked.")

    # ----------------------------------------------------------
    # STEP 11: CREATE NEW BOOKING MODAL — wait for it
    # ----------------------------------------------------------
    print("[*] Waiting for booking details modal...")
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH,
            "//*[contains(text(), 'Booking Title')]"
        ))
    )
    print("    ✅ Booking modal appeared.")

    # ----------------------------------------------------------
    # STEP 12: BOOKING TITLE → "ISOC"
    # ----------------------------------------------------------
    print("[*] Entering Booking Title 'ISOC'...")
    title_input = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//input[contains(@placeholder,'Title') or contains(@placeholder,'title') or contains(@placeholder,'Booking')]"
        " | //*[normalize-space()='Booking Title']/following::input[1]"
        " | //*[normalize-space()='Booking Title']/..//input[1]"
    )))
    js_click(title_input)
    time.sleep(0.05)
    title_input.send_keys(Keys.CONTROL + "a")
    title_input.send_keys(Keys.BACKSPACE)
    react_set_input(title_input, "ISOC")
    time.sleep(0.05)
    print("    ✅ Booking Title set to 'ISOC'.")

    # ----------------------------------------------------------
    # STEP 13: CONFIRM BOOKING
    # Scroll modal to bottom so button is in viewport, then click.
    # ----------------------------------------------------------
    print("[*] Clicking 'Confirm Booking'...")
    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//button[normalize-space()='Confirm Booking']"
        " | //button[contains(text(),'Confirm Booking')]"
        " | //*[@role='button'][contains(text(),'Confirm Booking')]"
    )))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_btn)
    time.sleep(0.1)
    js_click(confirm_btn)
    print("    ✅ 'Confirm Booking' clicked.")

    print("\n🏆 BOOM! Booking confirmed!")
    print("    Room  : Meeting Room No 02")
    print("    Date  : 12-Jun-2026")
    print("    Time  : 20:00 – 22:00")
    print("    Title : ISOC")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()