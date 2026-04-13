# Appium + Android Emulator Setup Guide

## Quick Start

### 1. Install Java (required for Android SDK)
```bash
sudo apt-get install -y openjdk-11-jdk
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

### 2. Install Android SDK Command-line Tools
```bash
# Download from https://developer.android.com/studio#command-tools
# Or use sdkmanager:
sdkmanager "platform-tools" "emulator" "system-images;android-30;google_apis;x86_64"
```

Set environment:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin
```

### 3. Create an Android Virtual Device (AVD)
```bash
# List available system images
avdmanager list target

# Create AVD
avdmanager create avd \
  --name "TestDevice_API30" \
  --package "system-images;android-30;google_apis;x86_64" \
  --device "pixel_4"

# Start emulator
emulator -avd TestDevice_API30 -no-snapshot-load &

# Wait for boot
adb wait-for-device
adb shell getprop sys.boot_completed  # wait until "1"
```

### 4. Install Node.js and Appium
```bash
# Node.js (if not installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Appium
npm install -g appium

# UiAutomator2 driver (for Android)
appium driver install uiautomator2

# XCUITest driver (for iOS — macOS only)
# appium driver install xcuitest
```

### 5. Install Python client
```bash
pip install Appium-Python-Client --break-system-packages
```

### 6. Start Appium Server
```bash
appium --base-path /wd/hub --port 4723
# Or in background:
appium --base-path /wd/hub --port 4723 > appium.log 2>&1 &
```

### 7. Verify Setup
```bash
python3 scripts/check_environment.py
```

---

## Desired Capabilities Reference

```python
from appium.options import AppiumOptions

options = AppiumOptions()
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.app = "/abs/path/to/app.apk"
options.device_name = "emulator-5554"  # from `adb devices`
options.no_reset = False               # reinstall app each run
options.full_reset = False             # keep app data between runs if True
options.new_command_timeout = 60       # seconds before timeout
options.auto_grant_permissions = True  # auto-grant runtime permissions
```

For iOS:
```python
options.platform_name = "iOS"
options.automation_name = "XCUITest"
options.platform_version = "16.0"
options.device_name = "iPhone 14"
options.bundle_id = "com.example.app"
```

---

## Element Locator Strategies (priority order)

1. **accessibility id** — best, platform-independent
   ```python
   driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Login Button")
   ```

2. **id / resource-id** — Android: `com.example.app:id/login_button`
   ```python
   driver.find_element(AppiumBy.ID, "com.example.app:id/login_btn")
   ```

3. **uiautomator** — powerful Android selector
   ```python
   driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Login")')
   ```

4. **xpath** — use sparingly, fragile
   ```python
   driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@text="Login"]')
   ```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `adb: command not found` | Add `$ANDROID_HOME/platform-tools` to PATH |
| Emulator stuck at boot | Run `adb reboot` or recreate AVD |
| `Could not start a new session` | Check Appium server is running at port 4723 |
| `UiAutomator2 not installed` | Run `appium driver install uiautomator2` |
| App crashes on install | Check minSdk in APK vs emulator API level |
| Elements not found | Increase implicit wait or use explicit `WebDriverWait` |
| Permission dialogs blocking test | Set `options.auto_grant_permissions = True` |

---

## iOS Notes (macOS only)

iOS testing requires Xcode + iOS Simulator and is only possible on macOS.
For CI/CD: use a macOS GitHub Actions runner or a Mac build machine.

```bash
# Install xcpretty
gem install xcpretty

# Build + install .ipa to simulator
xcrun simctl install booted path/to/app.ipa
```